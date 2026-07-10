/**
 * Python Process Bridge — spawns the Python gridcore_adapter as a child
 * process and communicates via JSON-RPC over stdin/stdout.
 *
 * This replaces the hardcoded defaultDispatcher with the real Python
 * runtime, giving TerminalSurface and TeletextSurface access to all
 * 13 uCode commands, VAULT, CEEFAX, and LENS.
 */

import { spawn, type ChildProcess } from 'child_process'
import { join } from 'path'
import type { CommandDispatcher, CommandResult } from './runtime-bridge'

export interface PythonBridgeOptions {
  /** Path to the Python venv (absolute or relative to project root) */
  venvPath?: string
  /** Project root directory */
  projectRoot?: string
  /** Timeout in ms for each command dispatch */
  timeoutMs?: number
}

/** Resolve the project root from this source file's location */
function defaultProjectRoot(): string {
  // packages/gridcore/src/bridge/python-process-bridge.ts → ../../..
  const fromSrc = join(__dirname, '..', '..', '..')
  return fromSrc
}

export class PythonProcessBridge {
  private process: ChildProcess | null = null
  private dispatcher: CommandDispatcher | null = null
  private ready: boolean = false
  private pending: Map<string, {
    resolve: (result: CommandResult) => void
    reject: (err: Error) => void
  }> = new Map()
  private requestId = 0
  private buffer = ''

  constructor(private options: PythonBridgeOptions = {}) {}

  /** Start the Python subprocess and return a dispatcher */
  async start(): Promise<CommandDispatcher> {
    if (this.dispatcher) return this.dispatcher

    const root = this.options.projectRoot ?? defaultProjectRoot()
    const python = join(
      this.options.venvPath ?? join(root, '.venv', 'bin'),
      'python'
    )

    const adapterScript = join(
      root,
      'runtimes', 'basic', 'bridge', 'gridcore_adapter.py'
    )

    this.process = spawn(python, [adapterScript], {
      cwd: root,
      stdio: ['pipe', 'pipe', 'pipe'],
      env: { ...process.env, PYTHONUNBUFFERED: '1' },
    })

    this.process.stdout!.on('data', (data: Buffer) => {
      this.handleStdout(data)
    })

    this.process.stderr!.on('data', (data: Buffer) => {
      // Stderr is for logging, not JSON-RPC
      const msg = data.toString().trim()
      if (msg) console.error('[python-bridge stderr]', msg)
    })

    this.process.on('exit', (code) => {
      this.ready = false
      if (code !== 0 && code !== null) {
        console.error(`[python-bridge] exited with code ${code}`)
      }
      this.rejectAll(new Error(`Python process exited (code ${code})`))
    })

    this.process.on('error', (err) => {
      this.ready = false
      console.error('[python-bridge] process error:', err.message)
      this.rejectAll(err)
    })

    // Create the dispatcher
    this.dispatcher = (command: string): Promise<CommandResult> => {
      return this.dispatchCommand(command)
    }

    this.ready = true
    return this.dispatcher
  }

  /** Stop the Python process */
  stop(): void {
    if (this.process) {
      this.process.stdin!.end()
      this.process.kill()
      this.process = null
    }
    this.ready = false
    this.dispatcher = null
    this.pending.clear()
  }

  /** Check if the bridge is running */
  isReady(): boolean {
    return this.ready && this.process !== null
  }

  // ── Private helpers ──────────────────────────────────────────

  private async dispatchCommand(command: string): Promise<CommandResult> {
    if (!this.process || !this.process.stdin) {
      return { output: 'Python runtime not running.' }
    }

    const id = String(++this.requestId)
    const request = {
      jsonrpc: '2.0',
      method: 'dispatch',
      params: { command },
      id,
    }

    return new Promise<CommandResult>((resolve, reject) => {
      const timeout = this.options.timeoutMs ?? 5000
      const timer = setTimeout(() => {
        this.pending.delete(id)
        reject(new Error(`Command timed out after ${timeout}ms: ${command}`))
      }, timeout)

      this.pending.set(id, {
        resolve: (result) => {
          clearTimeout(timer)
          resolve(result)
        },
        reject: (err) => {
          clearTimeout(timer)
          reject(err)
        },
      })

      const payload = JSON.stringify(request) + '\n'
      this.process!.stdin!.write(payload)
    })
  }

  private handleStdout(data: Buffer): void {
    this.buffer += data.toString()
    const lines = this.buffer.split('\n')
    // Keep the last (potentially incomplete) line in the buffer
    this.buffer = lines.pop() ?? ''

    for (const line of lines) {
      const trimmed = line.trim()
      if (!trimmed) continue

      try {
        const response = JSON.parse(trimmed)
        if (response.id && this.pending.has(response.id)) {
          const { resolve, reject } = this.pending.get(response.id)!
          this.pending.delete(response.id)

          if (response.error) {
            reject(new Error(response.error.message ?? 'Unknown error'))
          } else {
            resolve(response.result as CommandResult)
          }
        }
      } catch {
        // Non-JSON line (e.g., debug output) — ignore
      }
    }
  }

  private rejectAll(err: Error): void {
    for (const [, { reject }] of this.pending) {
      reject(err)
    }
    this.pending.clear()
  }
}
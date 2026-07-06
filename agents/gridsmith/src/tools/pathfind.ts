import type { Grid } from '@udos/gridcore'
import { getCell } from '@udos/gridcore'

export interface PathNode {
  x: number
  y: number
  layer: number
}

export interface PathResult {
  path: PathNode[]
  steps: number
  found: boolean
}

function heuristic(a: PathNode, b: PathNode): number {
  return Math.abs(a.x - b.x) + Math.abs(a.y - b.y)
}

function neighbors(node: PathNode, grid: Grid, layer: number): PathNode[] {
  const dirs = [
    { dx: 0, dy: -1 }, // up
    { dx: 0, dy: 1 },  // down
    { dx: -1, dy: 0 }, // left
    { dx: 1, dy: 0 },  // right
  ]

  const result: PathNode[] = []
  for (const { dx, dy } of dirs) {
    const nx = node.x + dx
    const ny = node.y + dy
    if (nx >= 0 && nx < grid.cols && ny >= 0 && ny < grid.rows) {
      const cell = getCell(grid, nx, ny, layer)
      if (cell && cell.char !== '#') {
        result.push({ x: nx, y: ny, layer })
      }
    }
  }
  return result
}

function reconstructPath(cameFrom: Map<string, PathNode>, current: PathNode): PathNode[] {
  const path: PathNode[] = [current]
  let key = `${current.x},${current.y},${current.layer}`
  while (cameFrom.has(key)) {
    current = cameFrom.get(key)!
    key = `${current.x},${current.y},${current.layer}`
    path.unshift(current)
  }
  return path
}

export function findPath(
  grid: Grid,
  startX: number,
  startY: number,
  endX: number,
  endY: number,
  layer: number = 0,
): PathResult {
  const start: PathNode = { x: startX, y: startY, layer }
  const goal: PathNode = { x: endX, y: endY, layer }

  // Check bounds
  if (
    startX < 0 || startX >= grid.cols ||
    startY < 0 || startY >= grid.rows ||
    endX < 0 || endX >= grid.cols ||
    endY < 0 || endY >= grid.rows
  ) {
    return { path: [], steps: 0, found: false }
  }

  const openSet: { node: PathNode; f: number }[] = [{ node: start, f: heuristic(start, goal) }]
  const cameFrom = new Map<string, PathNode>()
  const gScore = new Map<string, number>()
  gScore.set(`${start.x},${start.y},${start.layer}`, 0)

  while (openSet.length > 0) {
    // Sort by f-score (simple priority queue)
    openSet.sort((a, b) => a.f - b.f)
    const current = openSet.shift()!

    if (current.node.x === goal.x && current.node.y === goal.y) {
      const path = reconstructPath(cameFrom, current.node)
      return { path, steps: path.length - 1, found: true }
    }

    const currentKey = `${current.node.x},${current.node.y},${current.node.layer}`
    const currentG = gScore.get(currentKey) ?? Infinity

    for (const neighbor of neighbors(current.node, grid, layer)) {
      const tentG = currentG + 1
      const nKey = `${neighbor.x},${neighbor.y},${neighbor.layer}`
      if (tentG < (gScore.get(nKey) ?? Infinity)) {
        cameFrom.set(nKey, current.node)
        gScore.set(nKey, tentG)
        openSet.push({ node: neighbor, f: tentG + heuristic(neighbor, goal) })
      }
    }
  }

  return { path: [], steps: 0, found: false }
}
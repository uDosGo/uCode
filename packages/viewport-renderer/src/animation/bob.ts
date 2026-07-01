export interface BobState {
  x: number
  y: number
  vx: number
  vy: number
}

export function stepBob(state: BobState, width: number, height: number): BobState {
  let x = state.x + state.vx
  let y = state.y + state.vy
  let vx = state.vx
  let vy = state.vy

  if (x < 0 || x > width) {
    vx *= -1
    x = Math.max(0, Math.min(width, x))
  }

  if (y < 0 || y > height) {
    vy *= -1
    y = Math.max(0, Math.min(height, y))
  }

  return { x, y, vx, vy }
}

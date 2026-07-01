export interface SpriteFrame {
  id: string
  durationMs: number
  payload: unknown
}

export class SpriteAnimator {
  private frames: SpriteFrame[]
  private index = 0

  constructor(frames: SpriteFrame[]) {
    this.frames = frames
  }

  current(): SpriteFrame | null {
    return this.frames.length ? this.frames[this.index] : null
  }

  next(): SpriteFrame | null {
    if (!this.frames.length) return null
    this.index = (this.index + 1) % this.frames.length
    return this.frames[this.index]
  }
}

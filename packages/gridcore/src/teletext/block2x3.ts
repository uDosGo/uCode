export interface Block2x3 {
  topLeft: boolean
  topRight: boolean
  midLeft: boolean
  midRight: boolean
  bottomLeft: boolean
  bottomRight: boolean
}

export function createEmptyBlock2x3(): Block2x3 {
  return {
    topLeft: false,
    topRight: false,
    midLeft: false,
    midRight: false,
    bottomLeft: false,
    bottomRight: false,
  }
}

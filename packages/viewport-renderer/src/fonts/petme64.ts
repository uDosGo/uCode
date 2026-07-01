export interface FontDefinition {
  id: string
  family: string
  source?: string
}

export function loadPETME64(): FontDefinition {
  return {
    id: 'petme64',
    family: 'PetMe64, PetMe128, monospace',
  }
}

export function loadCustomFont(path: string): FontDefinition {
  return {
    id: 'custom',
    family: 'custom-font',
    source: path,
  }
}

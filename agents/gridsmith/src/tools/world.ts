export interface WorldManifest {
  id: string
  name: string
  type: 'earth' | 'dungeon' | 'vault' | 'library'
  seed?: number
  source?: 'generated' | 'basic' | 'amos'
}

export function createWorldManifest(
  id: string,
  name: string,
  type: WorldManifest['type'],
  seed?: number,
  source: WorldManifest['source'] = 'generated',
): WorldManifest {
  return { id, name, type, seed, source }
}
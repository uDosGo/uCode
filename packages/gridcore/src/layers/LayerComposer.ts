export type BlendMode = 'normal' | 'multiply' | 'screen' | 'overlay'

export interface ComposedLayer {
  id: string
  name: string
  zIndex: number
  visible: boolean
  opacity: number
  blendMode: BlendMode
  locked?: boolean
}

export class LayerComposer {
  private layers: ComposedLayer[] = []

  createLayer(input: Omit<ComposedLayer, 'id'>): ComposedLayer {
    const layer: ComposedLayer = { ...input, id: `layer-${Date.now()}-${Math.random().toString(36).slice(2, 6)}` }
    this.layers.push(layer)
    this.layers.sort((a, b) => a.zIndex - b.zIndex)
    return layer
  }

  deleteLayer(layerId: string): void {
    this.layers = this.layers.filter(layer => layer.id !== layerId)
  }

  setLayerVisibility(layerId: string, visible: boolean): void {
    this.layers = this.layers.map(layer => (layer.id === layerId ? { ...layer, visible } : layer))
  }

  setLayerOpacity(layerId: string, opacity: number): void {
    this.layers = this.layers.map(layer =>
      layer.id === layerId ? { ...layer, opacity: Math.max(0, Math.min(opacity, 1)) } : layer,
    )
  }

  reorderLayer(layerId: string, newIndex: number): void {
    const idx = this.layers.findIndex(layer => layer.id === layerId)
    if (idx === -1) return
    const [layer] = this.layers.splice(idx, 1)
    const target = Math.max(0, Math.min(this.layers.length, newIndex))
    this.layers.splice(target, 0, layer)
    this.layers = this.layers.map((entry, index) => ({ ...entry, zIndex: index }))
  }

  mergeLayers(layerId1: string, layerId2: string): ComposedLayer | null {
    const l1 = this.layers.find(layer => layer.id === layerId1)
    const l2 = this.layers.find(layer => layer.id === layerId2)
    if (!l1 || !l2) return null

    const merged: ComposedLayer = {
      id: `merge-${Date.now()}`,
      name: `${l1.name} + ${l2.name}`,
      zIndex: Math.max(l1.zIndex, l2.zIndex),
      visible: l1.visible || l2.visible,
      opacity: Math.max(l1.opacity, l2.opacity),
      blendMode: l2.blendMode,
      locked: false,
    }

    this.layers = this.layers.filter(layer => layer.id !== layerId1 && layer.id !== layerId2)
    this.layers.push(merged)
    this.layers.sort((a, b) => a.zIndex - b.zIndex)
    return merged
  }

  lockLayer(layerId: string): void {
    this.layers = this.layers.map(layer => (layer.id === layerId ? { ...layer, locked: true } : layer))
  }

  unlockLayer(layerId: string): void {
    this.layers = this.layers.map(layer => (layer.id === layerId ? { ...layer, locked: false } : layer))
  }

  list(): ComposedLayer[] {
    return [...this.layers]
  }
}

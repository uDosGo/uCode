import { describe, expect, it } from 'vitest'
import { TeletextPageProvider } from '../src/teletext/page-provider'

describe('TeletextPageProvider', () => {
  const provider = new TeletextPageProvider()

  it('creates a page loader function', async () => {
    const loader = provider.createPageLoader()
    const page = await loader(100)
    expect(page.page).toBe(100)
    expect(page.title).toBe('uCode Main Index')
    expect(page.fasttext.length).toBe(4)
    expect(page.content.length).toBeGreaterThan(0)
  })

  it('resolves main index page 100', () => {
    const page = provider.resolvePage(100)
    expect(page.page).toBe(100)
    expect(page.title).toBe('uCode Main Index')
    expect(page.fasttext.length).toBe(4)
    expect(page.fasttext[0].color).toBe('red')
    expect(page.fasttext[0].page).toBe(101)
  })

  it('resolves news page 101', () => {
    const page = provider.resolvePage(101)
    expect(page.page).toBe(101)
    expect(page.title).toBe('uCode News')
  })

  it('resolves course catalogue 300', () => {
    const page = provider.resolvePage(300)
    expect(page.page).toBe(300)
    expect(page.title).toBe('Course Catalogue')
  })

  it('resolves individual course pages', () => {
    const page = provider.resolvePage(301)
    expect(page.page).toBe(301)
    expect(page.fasttext.length).toBe(4)
  })

  it('resolves vault index 400', () => {
    const page = provider.resolvePage(400)
    expect(page.page).toBe(400)
    expect(page.title).toBe('Vault Configuration')
  })

  it('resolves vault secrets 401', () => {
    const page = provider.resolvePage(401)
    expect(page.page).toBe(401)
    expect(page.title).toBe('Vault Secrets')
    // Content should mention secret keys
    const hasSecretKey = page.content.some(line =>
      line.includes('OPENROUTER_API_KEY') || line.includes('[SET]')
    )
    expect(hasSecretKey).toBe(true)
  })

  it('resolves docs index 500', () => {
    const page = provider.resolvePage(500)
    expect(page.page).toBe(500)
    expect(page.title).toBe('Documentation Index')
  })

  it('resolves doc category pages 501-505', () => {
    for (let i = 501; i <= 505; i++) {
      const page = provider.resolvePage(i)
      expect(page.page).toBe(i)
    }
  })

  it('resolves help page 888', () => {
    const page = provider.resolvePage(888)
    expect(page.page).toBe(888)
    expect(page.title).toBe('Help & About')
  })

  it('resolves full index 199', () => {
    const page = provider.resolvePage(199)
    expect(page.page).toBe(199)
    expect(page.title).toBe('Full Index')
  })

  it('returns not-found for unknown pages', () => {
    const page = provider.resolvePage(999)
    expect(page.page).toBe(999)
    expect(page.title).toBe('Page Not Found')
    expect(page.content[0]).toContain('NOT FOUND')
  })

  it('all pages have fasttext links', () => {
    const pages = [100, 101, 199, 300, 301, 400, 401, 500, 501, 888, 999]
    for (const p of pages) {
      const page = provider.resolvePage(p)
      expect(page.fasttext.length).toBeGreaterThan(0)
    }
  })
})
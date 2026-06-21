'use client'

import { useState, useCallback } from 'react'
import { NavigationSidebar } from '@/components/NavigationSidebar'
import { BlockEditor } from '@/components/BlockEditor'
import { useDocuments } from '@/hooks/useDocument'

export default function Home() {
  const { getDocument, createDocument } = useDocuments()
  const [currentDocumentId, setCurrentDocumentId] = useState<string>('welcome')
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const currentDocument = getDocument(currentDocumentId)

  const handleNewDocument = useCallback(() => {
    const doc = createDocument('Untitled')
    setCurrentDocumentId(doc.id)
  }, [createDocument])

  const handleSelectDocument = useCallback((id: string) => {
    setCurrentDocumentId(id)
  }, [])

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <div
        className={`flex-shrink-0 transition-all duration-200 ${
          sidebarOpen ? 'w-64' : 'w-0 overflow-hidden'
        }`}
      >
        <NavigationSidebar
          currentDocumentId={currentDocumentId}
          onSelectDocument={handleSelectDocument}
          onNewDocument={handleNewDocument}
        />
      </div>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <div className="flex items-center gap-2 px-4 py-2 border-b border-border">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-1.5 rounded-md hover:bg-surface transition-colors"
            title={sidebarOpen ? 'Close sidebar' : 'Open sidebar'}
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          <div className="flex-1" />

          {currentDocument && (
            <button
              onClick={() => {
                // Toggle publish
                // In production, this would trigger web publishing
                alert('Web publishing coming soon!')
              }}
              className="px-3 py-1.5 text-sm rounded-lg bg-primary text-white
                         hover:bg-primary/90 transition-colors"
            >
              {currentDocument.isPublished ? 'Published' : 'Publish'}
            </button>
          )}
        </div>

        {/* Editor */}
        <div className="flex-1 overflow-y-auto">
          {currentDocument ? (
            <BlockEditor document={currentDocument} />
          ) : (
            <div className="flex items-center justify-center h-full text-text-muted">
              <div className="text-center">
                <p className="text-lg mb-2">Select a document or create a new one</p>
                <button
                  onClick={handleNewDocument}
                  className="px-4 py-2 rounded-lg bg-primary text-white
                             hover:bg-primary/90 transition-colors text-sm"
                >
                  + New document
                </button>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

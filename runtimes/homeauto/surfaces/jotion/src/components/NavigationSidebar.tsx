'use client'

import { useState, useCallback } from 'react'
import { useDocuments } from '@/hooks/useDocument'
import { cn, formatDate, truncate } from '@/lib/utils'

type NavigationSidebarProps = {
  currentDocumentId: string | null
  onSelectDocument: (id: string) => void
  onNewDocument: () => void
}

export function NavigationSidebar({
  currentDocumentId,
  onSelectDocument,
  onNewDocument,
}: NavigationSidebarProps) {
  const { getDocuments, searchDocuments, archiveDocument } = useDocuments()
  const [searchQuery, setSearchQuery] = useState('')
  const [showTrash, setShowTrash] = useState(false)
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(['documents'])
  )

  const toggleSection = useCallback((section: string) => {
    setExpandedSections((prev) => {
      const next = new Set(prev)
      if (next.has(section)) {
        next.delete(section)
      } else {
        next.add(section)
      }
      return next
    })
  }, [])

  const documents = searchQuery
    ? searchDocuments(searchQuery)
    : getDocuments(null)

  const trashDocuments = getDocuments('__trash__')

  return (
    <aside className="w-64 h-full flex flex-col bg-surface border-r border-border">
      {/* Header */}
      <div className="p-3 border-b border-border">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-sm font-semibold text-text">uCode3 Workspace</h2>
          <button
            onClick={onNewDocument}
            className="p-1 rounded-md hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
            title="New document"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
          </button>
        </div>

        {/* Search */}
        <div className="relative">
          <svg
            className="absolute left-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-text-muted"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          <input
            type="text"
            placeholder="Search documents..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-8 pr-3 py-1.5 text-sm rounded-lg bg-white dark:bg-gray-800
                       border border-border focus:outline-none focus:ring-2 focus:ring-primary/30
                       placeholder:text-text-muted/50"
          />
        </div>
      </div>

      {/* Document List */}
      <div className="flex-1 overflow-y-auto p-2">
        {/* Documents Section */}
        <div className="mb-2">
          <button
            onClick={() => toggleSection('documents')}
            className="flex items-center gap-1.5 w-full px-2 py-1 text-xs font-medium
                       text-text-muted hover:text-text transition-colors"
          >
            <svg
              className={cn('w-3 h-3 transition-transform', expandedSections.has('documents') && 'rotate-90')}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            Documents
          </button>

          {expandedSections.has('documents') && (
            <div className="mt-1 space-y-0.5">
              {documents.length === 0 ? (
                <p className="px-3 py-2 text-xs text-text-muted">
                  {searchQuery ? 'No documents found' : 'No documents yet'}
                </p>
              ) : (
                documents.map((doc) => (
                  <button
                    key={doc.id}
                    onClick={() => onSelectDocument(doc.id)}
                    className={cn(
                      'sidebar-item w-full text-left',
                      currentDocumentId === doc.id && 'active'
                    )}
                  >
                    <span className="flex-shrink-0">{doc.icon}</span>
                    <span className="flex-1 truncate">{truncate(doc.title, 28)}</span>
                    <span className="text-[10px] text-text-muted flex-shrink-0">
                      {formatDate(doc.updatedAt)}
                    </span>
                  </button>
                ))
              )}
            </div>
          )}
        </div>

        {/* Trash Section */}
        <div>
          <button
            onClick={() => setShowTrash(!showTrash)}
            className="flex items-center gap-1.5 w-full px-2 py-1 text-xs font-medium
                       text-text-muted hover:text-text transition-colors"
          >
            <svg
              className={cn('w-3 h-3 transition-transform', showTrash && 'rotate-90')}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            Trash
            {trashDocuments.length > 0 && (
              <span className="ml-auto text-[10px] text-text-muted">
                {trashDocuments.length}
              </span>
            )}
          </button>

          {showTrash && (
            <div className="mt-1 space-y-0.5">
              {trashDocuments.length === 0 ? (
                <p className="px-3 py-2 text-xs text-text-muted">Trash is empty</p>
              ) : (
                trashDocuments.map((doc) => (
                  <div
                    key={doc.id}
                    className="flex items-center gap-2 px-3 py-1.5 text-sm rounded-lg
                               text-text-muted"
                  >
                    <span>{doc.icon}</span>
                    <span className="flex-1 truncate">{truncate(doc.title, 24)}</span>
                    <button
                      onClick={() => archiveDocument(doc.id)}
                      className="text-xs hover:text-accent transition-colors"
                      title="Delete permanently"
                    >
                      Delete
                    </button>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-border">
        <button
          onClick={() => {
            // Toggle theme
            document.documentElement.classList.toggle('dark')
          }}
          className="sidebar-item w-full text-xs text-text-muted"
        >
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
            />
          </svg>
          Toggle theme
        </button>
      </div>
    </aside>
  )
}

'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import { useDocuments } from '@/hooks/useDocument'
import type { Document } from '@/lib/utils'

type BlockEditorProps = {
  document: Document
}

export function BlockEditor({ document }: BlockEditorProps) {
  const { updateDocument } = useDocuments()
  const [title, setTitle] = useState(document.title)
  const [isEditingTitle, setIsEditingTitle] = useState(false)
  const titleRef = useRef<HTMLTextAreaElement>(null)
  const editorRef = useRef<HTMLDivElement>(null)

  // Auto-resize title textarea
  useEffect(() => {
    if (titleRef.current) {
      titleRef.current.style.height = 'auto'
      titleRef.current.style.height = titleRef.current.scrollHeight + 'px'
    }
  }, [title])

  const handleTitleChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      const newTitle = e.target.value
      setTitle(newTitle)
      updateDocument(document.id, { title: newTitle })
    },
    [document.id, updateDocument]
  )

  const handleTitleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === 'Enter') {
        e.preventDefault()
        setIsEditingTitle(false)
        // Focus the editor
        editorRef.current?.focus()
      }
      if (e.key === 'Escape') {
        setIsEditingTitle(false)
        setTitle(document.title)
      }
    },
    [document.title]
  )

  return (
    <div className="editor-container animate-fade-in">
      {/* Cover Image */}
      {document.coverImage && (
        <div className="relative mb-8">
          <img
            src={document.coverImage}
            alt="Cover"
            className="cover-image"
          />
          <button
            className="absolute top-2 right-2 p-1.5 rounded-lg bg-black/50 text-white
                       opacity-0 hover:opacity-100 transition-opacity text-xs"
            onClick={() => updateDocument(document.id, { coverImage: null })}
          >
            Remove cover
          </button>
        </div>
      )}

      {/* Document Icon */}
      <div className="flex items-center gap-3 mb-4">
        <span className="document-icon text-3xl">{document.icon}</span>
        <button
          className="text-xs text-text-muted hover:text-text transition-colors"
          onClick={() => {
            const icons = ['📄', '📝', '📋', '📌', '📎', '🎯', '💡', '🚀', '⭐', '🔧']
            const currentIndex = icons.indexOf(document.icon)
            const nextIcon = icons[(currentIndex + 1) % icons.length]
            updateDocument(document.id, { icon: nextIcon })
          }}
        >
          Change icon
        </button>
      </div>

      {/* Title */}
      <div className="mb-8">
        {isEditingTitle ? (
          <textarea
            ref={titleRef}
            value={title}
            onChange={handleTitleChange}
            onKeyDown={handleTitleKeyDown}
            onBlur={() => setIsEditingTitle(false)}
            className="w-full text-4xl font-bold bg-transparent border-none outline-none
                       resize-none overflow-hidden text-text placeholder-text-muted/50"
            placeholder="Untitled"
            autoFocus
            rows={1}
          />
        ) : (
          <h1
            className="text-4xl font-bold cursor-text hover:text-text-muted transition-colors"
            onClick={() => setIsEditingTitle(true)}
          >
            {title || 'Untitled'}
          </h1>
        )}
      </div>

      {/* BlockNote Editor Area */}
      <div
        ref={editorRef}
        className="prose prose-slate dark:prose-invert max-w-none min-h-[300px]"
      >
        <div className="text-text-muted text-sm mb-4">
          Start typing or type <kbd className="px-1.5 py-0.5 rounded bg-surface text-xs font-mono">/</kbd> for commands
        </div>

        {/* Block type buttons */}
        <div className="flex flex-wrap gap-2 mb-6">
          {[
            { label: 'Heading 1', type: 'heading1', icon: 'H1' },
            { label: 'Heading 2', type: 'heading2', icon: 'H2' },
            { label: 'Heading 3', type: 'heading3', icon: 'H3' },
            { label: 'Bullet List', type: 'bulleted_list', icon: '•' },
            { label: 'Numbered List', type: 'numbered_list', icon: '1.' },
            { label: 'To-do', type: 'to_do', icon: '☐' },
            { label: 'Code', type: 'code', icon: '</>' },
            { label: 'Quote', type: 'quote', icon: '"' },
            { label: 'Divider', type: 'divider', icon: '—' },
            { label: 'Callout', type: 'callout', icon: '💬' },
          ].map((block) => (
            <button
              key={block.type}
              className="flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-lg
                         border border-border hover:bg-surface transition-colors"
              onClick={() => {
                // Insert block at cursor position
                const selection = window.getSelection()
                if (selection && selection.rangeCount > 0) {
                  const range = selection.getRangeAt(0)
                  const blockElement = document.createElement('div')
                  blockElement.className = `block-${block.type}`
                  blockElement.contentEditable = 'true'
                  blockElement.setAttribute('data-block-type', block.type)
                  blockElement.textContent = block.type === 'divider' ? '───────────────' : ''
                  range.insertNode(blockElement)
                  range.setStartAfter(blockElement)
                  range.collapse(true)
                  selection.removeAllRanges()
                  selection.addRange(range)
                }
              }}
            >
              <span className="text-xs font-mono">{block.icon}</span>
              <span>{block.label}</span>
            </button>
          ))}
        </div>

        {/* Rich text content area */}
        <div
          className="min-h-[400px] focus:outline-none"
          contentEditable
          suppressContentEditableWarning
          onInput={(e) => {
            updateDocument(document.id, {
              content: { type: 'doc', content: [{ text: e.currentTarget.innerHTML }] },
            })
          }}
          dangerouslySetInnerHTML={{
            __html:
              document.content?.content?.[0]?.text ||
              '<p><br></p>',
          }}
        />
      </div>
    </div>
  )
}

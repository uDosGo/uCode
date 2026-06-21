'use client'

import { useState, useCallback, useEffect } from 'react'
import type { Document } from '@/lib/utils'

// In-memory document store (will be replaced with Convex DB)
let documents: Document[] = [
  {
    id: 'welcome',
    title: 'Welcome to uCode3',
    content: { type: 'doc', content: [] },
    icon: '📄',
    coverImage: null,
    isPublished: false,
    parentDocument: null,
    createdAt: new Date(),
    updatedAt: new Date(),
  },
]

const listeners = new Set<() => void>()

function notifyListeners() {
  listeners.forEach((listener) => listener())
}

export function useDocuments() {
  const [, forceUpdate] = useState(0)

  useEffect(() => {
    const listener = () => forceUpdate((n) => n + 1)
    listeners.add(listener)
    return () => listeners.delete(listener)
  }, [])

  const getDocuments = useCallback((parentId: string | null = null): Document[] => {
    return documents.filter((doc) => doc.parentDocument === parentId)
  }, [])

  const getDocument = useCallback((id: string): Document | undefined => {
    return documents.find((doc) => doc.id === id)
  }, [])

  const createDocument = useCallback((title: string, parentId: string | null = null): Document => {
    const doc: Document = {
      id: generateId(),
      title,
      content: { type: 'doc', content: [] },
      icon: '📄',
      coverImage: null,
      isPublished: false,
      parentDocument: parentId,
      createdAt: new Date(),
      updatedAt: new Date(),
    }
    documents.push(doc)
    notifyListeners()
    return doc
  }, [])

  const updateDocument = useCallback((id: string, updates: Partial<Document>) => {
    const index = documents.findIndex((doc) => doc.id === id)
    if (index !== -1) {
      documents[index] = { ...documents[index], ...updates, updatedAt: new Date() }
      notifyListeners()
    }
  }, [])

  const deleteDocument = useCallback((id: string) => {
    documents = documents.filter((doc) => doc.id !== id)
    notifyListeners()
  }, [])

  const archiveDocument = useCallback((id: string) => {
    const doc = documents.find((d) => d.id === id)
    if (doc) {
      doc.parentDocument = '__trash__'
      notifyListeners()
    }
  }, [])

  const searchDocuments = useCallback((query: string): Document[] => {
    if (!query) return documents
    const lower = query.toLowerCase()
    return documents.filter(
      (doc) =>
        doc.title.toLowerCase().includes(lower) ||
        doc.icon.includes(query)
    )
  }, [])

  return {
    documents,
    getDocuments,
    getDocument,
    createDocument,
    updateDocument,
    deleteDocument,
    archiveDocument,
    searchDocuments,
  }
}

function generateId(): string {
  return Math.random().toString(36).substring(2, 11)
}

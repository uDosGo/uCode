import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function generateId(): string {
  return Math.random().toString(36).substring(2, 11)
}

export function formatDate(date: Date): string {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(date)
}

export function truncate(str: string, length: number): string {
  if (str.length <= length) return str
  return str.substring(0, length) + '...'
}

export type Document = {
  id: string
  title: string
  content: any
  icon: string
  coverImage: string | null
  isPublished: boolean
  parentDocument: string | null
  createdAt: Date
  updatedAt: Date
}

export type WorkspaceState = {
  sidebarOpen: boolean
  currentView: 'document' | 'trash' | 'settings'
  searchQuery: string
  theme: 'light' | 'dark'
}

import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Jotion — uCode3 Document Workspace',
  description: 'Notion-style WYSIWYG document editor for uCode3',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen bg-background text-text antialiased">
        {children}
      </body>
    </html>
  )
}

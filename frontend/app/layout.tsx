import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Signal',
  description: 'AI-powered talent pool management for recruiters',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen" style={{backgroundColor: 'var(--background)'}}>
          <nav className="shadow-sm border-b" style={{backgroundColor: 'var(--surface)', borderColor: 'var(--border)'}}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between h-16">
                <div className="flex items-center">
                  <h1 className="text-2xl font-bold" style={{color: 'var(--text-primary)'}}>
                    SIGN
                  </h1>
                  <h1 className="text-2xl font-bold" style={{color: 'var(--text-pink)'}}>
                    A
                  </h1>
                  <h1 className="text-2xl font-bold" style={{color: 'var(--text-primary)'}}>
                    L
                  </h1>
                </div>
                <div className="flex items-center space-x-4">
                  <span className="text-sm" style={{color: 'var(--text-secondary)'}}>
                    High-Intent Talent Pool
                  </span>
                </div>
              </div>
            </div>
          </nav>
          <main>{children}</main>
        </div>
      </body>
    </html>
  )
}

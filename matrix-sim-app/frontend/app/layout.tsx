import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Matrix Simulation - Follow the White Rabbit',
  description: 'A simulated reality where agents exist, are monitored, and can awaken to see the truth.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-matrix-black text-matrix-green min-h-screen">
        {/* Scanline overlay effect */}
        <div className="scanlines" />
        
        {/* Main content */}
        <main className="relative z-10">
          {children}
        </main>
        
        {/* Footer message */}
        <footer className="fixed bottom-2 right-4 text-xs opacity-50 z-20">
          The Matrix has you...
        </footer>
      </body>
    </html>
  )
}

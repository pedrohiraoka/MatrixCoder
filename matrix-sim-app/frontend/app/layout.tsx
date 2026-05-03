import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Matrix Simulation',
  description: 'Python e a Simulação da Matrix - ML, Dados e Criptografia',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

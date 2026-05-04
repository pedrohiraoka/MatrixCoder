import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'GvG Simulator - Guild Wars',
  description: 'Simulador de Guerras de Guildas em Tempo Real',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR">
      <body className="bg-medieval-bg min-h-screen">
        <main className="container mx-auto p-4">
          {children}
        </main>
      </body>
    </html>
  )
}

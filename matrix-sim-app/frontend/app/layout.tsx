import type { Metadata } from 'next';
import { JetBrains_Mono } from 'next/font/google';
import './globals.css';

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-jetbrains-mono',
});

export const metadata: Metadata = {
  title: 'Matrix Simulator - Simulador de Realidade Artificial',
  description: 'Um sistema de simulação onde entidades existem dentro de uma realidade artificial controlada por uma inteligência superior.',
  keywords: ['matrix', 'simulator', 'simulation', 'AI', 'agents'],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR" className={jetbrainsMono.variable}>
      <body className={`${jetbrainsMono.className} antialiased`}>
        {children}
      </body>
    </html>
  );
}

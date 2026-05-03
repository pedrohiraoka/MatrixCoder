'use client'

import { useEffect, useRef } from 'react'

interface MatrixRainProps {
  opacity?: number
}

export default function MatrixRain({ opacity = 0.3 }: MatrixRainProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Set canvas size
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight

    // Matrix characters (katakana + latin + numbers)
    const chars = 'アァカサタナハマヤャラワガザダバパイィキシチニヒミリヰギジヂビピウゥクスツヌフムユュルグズブヅプエェケセテネヘメレヱゲゼデベペオォコソトノホモヨョロヲゴゾドボポヴッン 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    const charArray = chars.split('')

    const fontSize = 14
    const columns = canvas.width / fontSize

    // Array of drops - one per column
    const drops: number[] = []
    for (let i = 0; i < columns; i++) {
      drops[i] = Math.random() * -100 // Start above screen at random positions
    }

    // Draw function
    const draw = () => {
      // Black BG with fade effect
      ctx.fillStyle = `rgba(10, 10, 10, ${opacity})`
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      // Green text
      ctx.fillStyle = '#00FF41'
      ctx.font = `${fontSize}px monospace`

      // Loop over drops
      for (let i = 0; i < drops.length; i++) {
        // Random character
        const char = charArray[Math.floor(Math.random() * charArray.length)]
        
        // Draw the character
        ctx.fillText(char, i * fontSize, drops[i] * fontSize)

        // Reset drop to top randomly after it has crossed screen
        if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
          drops[i] = 0
        }

        // Increment Y coordinate
        drops[i]++
      }
    }

    // Animation loop
    const interval = setInterval(draw, 33)

    // Handle resize
    const handleResize = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }

    window.addEventListener('resize', handleResize)

    return () => {
      clearInterval(interval)
      window.removeEventListener('resize', handleResize)
    }
  }, [opacity])

  return (
    <canvas
      ref={canvasRef}
      id="matrix-canvas"
      className="fixed inset-0 pointer-events-none"
    />
  )
}

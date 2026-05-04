/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        medieval: {
          bg: '#1a1a2e',
          dark: '#16213e',
          accent: '#e94560',
          gold: '#d4af37',
          light: '#f0e6d2'
        }
      },
      fontFamily: {
        fantasy: ['Georgia', 'serif']
      }
    },
  },
  plugins: [],
}

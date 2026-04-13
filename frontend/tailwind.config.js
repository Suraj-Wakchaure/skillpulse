/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          saffron: '#f97316', 
          amber: '#f59e0b',   
          blue: '#3b82f6',    
          dark: '#09090b',    // Almost pure black
          card: '#18181b',    // Deep dark grey for cards
          hover: '#27272a',   // Lighter grey for hover states
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      }
    },
  },
  plugins: [],
}
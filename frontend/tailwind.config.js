/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          900: '#0f172a',
          800: '#1e293b',
          700: '#334155',
        },
        brand: {
          teal: '#0d9488',
          tealLight: '#14b8a6',
          blue: '#0284c7',
          blueLight: '#38bdf8',
        }
      }
    },
  },
  plugins: [],
}

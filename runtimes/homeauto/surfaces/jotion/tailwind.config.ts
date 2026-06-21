import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#2e7d64',
          50: '#e8f5f0',
          100: '#c5e6d8',
          200: '#9ed5be',
          300: '#70c4a2',
          400: '#4db78c',
          500: '#2e7d64',
          600: '#256a54',
          700: '#1c5744',
          800: '#134434',
          900: '#0a3124',
        },
        surface: {
          DEFAULT: '#f7f6f3',
          dark: '#2d2d2d',
        },
        text: {
          DEFAULT: '#37352f',
          muted: '#6b6b6b',
          dark: '#e0e0e0',
          'dark-muted': '#9e9e9e',
        },
        border: {
          DEFAULT: '#e9e9e7',
          dark: '#404040',
        },
        accent: '#eb5757',
      },
      fontFamily: {
        body: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        mono: ['SF Mono', 'Monaco', 'monospace'],
      },
      animation: {
        'fade-in': 'fadeIn 0.2s ease-in-out',
        'slide-in': 'slideIn 0.2s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideIn: {
          '0%': { transform: 'translateX(-10px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}

export default config

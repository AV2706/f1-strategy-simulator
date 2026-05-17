/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        carbon: {
          950: '#040507',
          900: '#080b0d',
          850: '#0c1012',
          800: '#111619',
          700: '#1a2125',
        },
        matte: '#050607',
        ers: {
          DEFAULT: '#19f28a',
          soft: '#9ffccf',
        },
        pit: {
          DEFAULT: '#ffd84d',
          soft: '#ffe89a',
        },
        telemetry: {
          DEFAULT: '#ff5449',
          soft: '#ffb3ad',
        },
      },
      boxShadow: {
        panel: '0 12px 30px rgba(0, 0, 0, 0.35)',
        insetPanel: 'inset 0 1px 0 rgba(255, 255, 255, 0.04)',
      },
      backgroundImage: {
        'shell-gradient': 'linear-gradient(180deg, #080b0d 0%, #050607 100%)',
        'panel-gradient': 'linear-gradient(180deg, rgba(18,22,25,0.96) 0%, rgba(11,14,16,0.98) 100%)',
      },
      fontFamily: {
        sans: [
          'Inter',
          'ui-sans-serif',
          'system-ui',
          'Segoe UI',
          'Roboto',
          'Helvetica Neue',
          'Arial',
        ],
      },
    },
  },
  plugins: [],
}
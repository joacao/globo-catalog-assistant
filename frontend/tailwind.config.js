/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Paleta extraída da logo oficial (gradiente diagonal azul -> violeta -> magenta)
        'globo-blue': '#1D3AE0',
        'globo-violet': '#7B2FE0',
        'globo-magenta': '#C22BD1',
        ink: '#171225',
        paper: '#FBFAFD',
        mist: '#EFEDF6',
      },
      fontFamily: {
        display: ['Fraunces', 'serif'],
        sans: ['Manrope', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      backgroundImage: {
        'globo-gradient': 'linear-gradient(135deg, #1D3AE0 0%, #7B2FE0 55%, #C22BD1 100%)',
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
}
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',   // 🔥 THIS FIXES YOUR ISSUE
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
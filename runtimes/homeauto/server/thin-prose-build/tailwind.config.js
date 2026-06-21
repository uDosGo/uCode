/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["../src/uhome_server/thin_pages.py"],
  theme: {
    extend: {},
  },
  plugins: [require("@tailwindcss/typography")],
};

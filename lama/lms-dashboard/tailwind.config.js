/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/**/*.html",
  ],
  theme: {
    extend: {
      colors: {
        ink: "#14120F",
        paper: "#F5F0E6",
        navy: "#182446",
        "navy-deep": "#0E1730",
        brass: "#C1913E",
        "brass-light": "#E4C287",
        line: "#DAD0BC",
      },
      fontFamily: {
        display: ["var(--font-display)", "serif"],
        sans: ["var(--font-geist-sans)", "sans-serif"],
      },
      backgroundImage: {
        "stitch-line":
          "repeating-linear-gradient(90deg, currentColor 0 6px, transparent 6px 14px)",
      },
    },
  },
  plugins: [],
};

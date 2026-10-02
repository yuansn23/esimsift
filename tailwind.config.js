/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./layouts/**/*.html", "./content/**/*.md"],
  theme: {
    extend: {
      colors: {
        // 中性色：海军蓝灰阶（替代默认 slate，更沉稳）
        ink: {
          50: "#F5F7FA",
          100: "#E9EEF4",
          200: "#D3DDE8",
          300: "#ADBECF",
          400: "#8399B0",
          500: "#647C96",
          600: "#4F647C",
          700: "#415268",
          800: "#2B3A4E",
          900: "#1A2636",
          950: "#0C141F",
        },
        // 主品牌色：深青绿（旅行+信任感）
        brand: {
          50: "#EFFAF7",
          100: "#D6F2EA",
          200: "#AEE5D7",
          300: "#7DD2BD",
          400: "#4AB89E",
          500: "#289C84",
          600: "#1A7E6B",
          700: "#176558",
          800: "#155149",
          900: "#13443E",
          950: "#062723",
        },
        // 强调色：珊瑚橙（CTA、价格、高亮）
        accent: {
          50: "#FFF4EE",
          100: "#FFE5D8",
          200: "#FFC9B0",
          300: "#FFA37E",
          400: "#FF7E4C",
          500: "#FF6329",
          600: "#EF4A12",
          700: "#C73A0C",
          800: "#A1300F",
          900: "#842E13",
          950: "#461307",
        },
      },
      fontFamily: {
        display: ["Sora", "Inter", "system-ui", "sans-serif"],
        sans: ["Inter", "system-ui", "-apple-system", "Segoe UI", "sans-serif"],
      },
      boxShadow: {
        soft: "0 1px 2px rgba(12,20,31,.05), 0 8px 24px -12px rgba(12,20,31,.12)",
        lift: "0 2px 4px rgba(12,20,31,.06), 0 16px 40px -16px rgba(12,20,31,.18)",
        pop: "0 4px 8px rgba(12,20,31,.06), 0 24px 56px -20px rgba(12,20,31,.25)",
        cta: "0 4px 14px -4px rgba(239,74,18,.45)",
      },
      borderRadius: {
        "4xl": "1.75rem",
      },
      backgroundImage: {
        // 首页 hero 渐变底
        "hero-mesh":
          "radial-gradient(60rem 30rem at 85% -10%, rgba(74,184,158,.14), transparent 60%), radial-gradient(50rem 26rem at -10% 110%, rgba(255,99,41,.10), transparent 55%), linear-gradient(180deg, #F5F7FA 0%, #FFFFFF 100%)",
        // 深色区块
        "ink-gradient": "linear-gradient(135deg, #0C141F 0%, #1A2636 100%)",
      },
      typography: (theme) => ({
        DEFAULT: {
          css: {
            "--tw-prose-body": theme("colors.ink.800"),
            "--tw-prose-headings": theme("colors.ink.950"),
            "--tw-prose-links": theme("colors.brand.700"),
            "--tw-prose-bold": theme("colors.ink.950"),
            maxWidth: "none",
          },
        },
      }),
    },
  },
  plugins: [require("@tailwindcss/typography")],
};

/** Design tokens -- single source of truth (spec §9.1/§9.2). Blueberry on
 * Cream Soda are the brand anchors and are not to be substituted. */
export const colors = {
  primary: "#243b8f",
  primaryDark: "#1a2c6b",
  background: "#fff0c9",
  surface: "#FFFFFF",
  surfaceAlt: "#FFF9E6",
  text: "#1B2233",
  textMuted: "#6B7186",
  border: "#E6DFC8",
  success: "#1E8E5A",
  warning: "#C77700",
  danger: "#B3261E",
  info: "#3A6EA5",
  neutral: "#8A8F9E",
} as const;

export const radius = { card: 16, pill: 999 } as const;

export const spacing = { xs: 4, sm: 8, md: 12, lg: 16, xl: 24, xxl: 32 } as const;

export const theme = { colors, radius, spacing };
export type Theme = typeof theme;

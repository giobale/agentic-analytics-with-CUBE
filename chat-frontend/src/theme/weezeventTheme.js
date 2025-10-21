// Weezevent Brand Colors and Theme Configuration
// Inspired by the Weezevent website design system

export const colors = {
  // Primary Brand Colors
  primary: '#0033FF',        // Weezevent electric blue
  primaryDark: '#0029CC',    // Darker blue for hover states
  primaryLight: '#3366FF',   // Lighter blue for accents

  // Neutral Colors
  black: '#000000',          // Pure black for text and logo
  white: '#FFFFFF',          // Pure white
  gray50: '#F9FAFB',         // Very light gray for backgrounds
  gray100: '#F3F4F6',        // Light gray
  gray200: '#E5E7EB',        // Border gray
  gray300: '#D1D5DB',        // Medium gray
  gray400: '#9CA3AF',        // Text secondary
  gray500: '#6B7280',        // Text tertiary
  gray600: '#4B5563',        // Dark gray
  gray700: '#374151',        // Darker gray
  gray800: '#1F2937',        // Almost black
  gray900: '#111827',        // Very dark gray

  // Functional Colors
  success: '#10B981',        // Green for success states
  warning: '#F59E0B',        // Amber for warnings
  error: '#EF4444',          // Red for errors
  info: '#3B82F6',           // Blue for information

  // Semantic UI Colors
  background: '#FFFFFF',      // Main background
  surface: '#F9FAFB',        // Card/surface background
  border: '#E5E7EB',         // Border color
  textPrimary: '#000000',    // Primary text
  textSecondary: '#6B7280',  // Secondary text
  textTertiary: '#9CA3AF',   // Tertiary text
};

export const typography = {
  fontFamily: {
    sans: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    mono: 'ui-monospace, SFMono-Regular, "SF Mono", Consolas, "Liberation Mono", Menlo, monospace',
  },
  fontSize: {
    xs: '12px',
    sm: '14px',
    base: '16px',
    lg: '18px',
    xl: '20px',
    '2xl': '24px',
    '3xl': '30px',
    '4xl': '36px',
    '5xl': '48px',
  },
  fontWeight: {
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
  lineHeight: {
    tight: 1.25,
    normal: 1.5,
    relaxed: 1.75,
  },
};

export const spacing = {
  xs: '4px',
  sm: '8px',
  md: '12px',
  lg: '16px',
  xl: '24px',
  '2xl': '32px',
  '3xl': '48px',
  '4xl': '64px',
};

export const borderRadius = {
  sm: '6px',
  md: '8px',
  lg: '12px',
  xl: '16px',
  '2xl': '24px',
  full: '9999px',
};

export const shadows = {
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
  primary: '0 10px 30px -5px rgba(0, 51, 255, 0.3)',
  primaryLg: '0 20px 40px -10px rgba(0, 51, 255, 0.4)',
};

export const theme = {
  colors,
  typography,
  spacing,
  borderRadius,
  shadows,
};

export default theme;

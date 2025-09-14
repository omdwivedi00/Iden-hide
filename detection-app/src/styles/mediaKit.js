/**
 * Media Kit - Responsive Design Breakpoints and Utilities
 * Provides consistent breakpoints and responsive utilities across the app
 */

// Breakpoint definitions
export const breakpoints = {
  xs: '480px',    // Extra small devices (phones)
  sm: '768px',    // Small devices (tablets)
  md: '1024px',   // Medium devices (small laptops)
  lg: '1280px',   // Large devices (laptops)
  xl: '1536px',   // Extra large devices (desktops)
  xxl: '1920px'   // Ultra wide screens
};

// Media query helpers
export const mediaQueries = {
  xs: `@media (min-width: ${breakpoints.xs})`,
  sm: `@media (min-width: ${breakpoints.sm})`,
  md: `@media (min-width: ${breakpoints.md})`,
  lg: `@media (min-width: ${breakpoints.lg})`,
  xl: `@media (min-width: ${breakpoints.xl})`,
  xxl: `@media (min-width: ${breakpoints.xxl})`,
  
  // Max width queries
  xsMax: `@media (max-width: ${breakpoints.xs})`,
  smMax: `@media (max-width: ${breakpoints.sm})`,
  mdMax: `@media (max-width: ${breakpoints.md})`,
  lgMax: `@media (max-width: ${breakpoints.lg})`,
  xlMax: `@media (max-width: ${breakpoints.xl})`,
  
  // Range queries
  xsToSm: `@media (min-width: ${breakpoints.xs}) and (max-width: ${breakpoints.sm})`,
  smToMd: `@media (min-width: ${breakpoints.sm}) and (max-width: ${breakpoints.md})`,
  mdToLg: `@media (min-width: ${breakpoints.md}) and (max-width: ${breakpoints.lg})`,
  lgToXl: `@media (min-width: ${breakpoints.lg}) and (max-width: ${breakpoints.xl})`,
  xlAndUp: `@media (min-width: ${breakpoints.xl})`,
};

// Container max widths for different screen sizes
export const containerMaxWidths = {
  xs: '100%',
  sm: '100%',
  md: '100%',
  lg: '100%',
  xl: '100%',
  xxl: '100%',
  full: '100%'
};

// Grid system utilities
export const gridSystem = {
  // Number of columns for different breakpoints
  columns: {
    xs: 1,
    sm: 2,
    md: 3,
    lg: 4,
    xl: 5,
    xxl: 6
  },
  
  // Gap sizes
  gaps: {
    xs: '8px',
    sm: '12px',
    md: '16px',
    lg: '20px',
    xl: '24px',
    xxl: '32px'
  }
};

// Responsive font sizes - Compact design for better space utilization
export const fontSizes = {
  xs: {
    h1: '1rem',
    h2: '0.875rem',
    h3: '0.8rem',
    body: '0.75rem',
    small: '0.7rem'
  },
  sm: {
    h1: '1.125rem',
    h2: '1rem',
    h3: '0.9rem',
    body: '0.8rem',
    small: '0.75rem'
  },
  md: {
    h1: '1.25rem',
    h2: '1.125rem',
    h3: '1rem',
    body: '0.875rem',
    small: '0.8rem'
  },
  lg: {
    h1: '1.375rem',
    h2: '1.25rem',
    h3: '1.125rem',
    body: '0.9rem',
    small: '0.875rem'
  },
  xl: {
    h1: '1.5rem',
    h2: '1.375rem',
    h3: '1.25rem',
    body: '1rem',
    small: '0.9rem'
  },
  xxl: {
    h1: '1.625rem',
    h2: '1.5rem',
    h3: '1.375rem',
    body: '1rem',
    small: '0.9rem'
  }
};

// Responsive spacing - Compact design
export const spacing = {
  xs: {
    xs: '2px',
    sm: '4px',
    md: '6px',
    lg: '8px',
    xl: '10px',
    xxl: '12px'
  },
  sm: {
    xs: '3px',
    sm: '6px',
    md: '8px',
    lg: '10px',
    xl: '12px',
    xxl: '16px'
  },
  md: {
    xs: '4px',
    sm: '8px',
    md: '10px',
    lg: '12px',
    xl: '16px',
    xxl: '20px'
  },
  lg: {
    xs: '6px',
    sm: '10px',
    md: '12px',
    lg: '16px',
    xl: '20px',
    xxl: '24px'
  },
  xl: {
    xs: '8px',
    sm: '12px',
    md: '16px',
    lg: '20px',
    xl: '24px',
    xxl: '32px'
  },
  xxl: {
    xs: '10px',
    sm: '16px',
    md: '20px',
    lg: '24px',
    xl: '32px',
    xxl: '40px'
  }
};

// Responsive layout helpers
export const layoutHelpers = {
  // Full width container with responsive max-width
  container: (maxWidth = 'xl') => `
    width: 100%;
    max-width: ${containerMaxWidths[maxWidth]};
    margin: 0 auto;
    padding: 0 1rem;
    
    ${mediaQueries.sm} {
      padding: 0 1.5rem;
    }
    
    ${mediaQueries.lg} {
      padding: 0 2rem;
    }
    
    ${mediaQueries.xl} {
      padding: 0 2.5rem;
    }
  `,
  
  // Responsive grid
  grid: (columns = { xs: 1, sm: 2, md: 3, lg: 4 }) => `
    display: grid;
    gap: ${gridSystem.gaps.xs};
    
    grid-template-columns: repeat(${columns.xs}, 1fr);
    
    ${mediaQueries.sm} {
      grid-template-columns: repeat(${columns.sm || columns.xs}, 1fr);
      gap: ${gridSystem.gaps.sm};
    }
    
    ${mediaQueries.md} {
      grid-template-columns: repeat(${columns.md || columns.sm || columns.xs}, 1fr);
      gap: ${gridSystem.gaps.md};
    }
    
    ${mediaQueries.lg} {
      grid-template-columns: repeat(${columns.lg || columns.md || columns.sm || columns.xs}, 1fr);
      gap: ${gridSystem.gaps.lg};
    }
    
    ${mediaQueries.xl} {
      gap: ${gridSystem.gaps.xl};
    }
    
    ${mediaQueries.xxl} {
      gap: ${gridSystem.gaps.xxl};
    }
  `,
  
  // Responsive flexbox
  flex: (direction = 'row', wrap = 'wrap', justify = 'flex-start', align = 'stretch') => `
    display: flex;
    flex-direction: ${direction};
    flex-wrap: ${wrap};
    justify-content: ${justify};
    align-items: ${align};
    gap: ${gridSystem.gaps.xs};
    
    ${mediaQueries.sm} {
      gap: ${gridSystem.gaps.sm};
    }
    
    ${mediaQueries.md} {
      gap: ${gridSystem.gaps.md};
    }
    
    ${mediaQueries.lg} {
      gap: ${gridSystem.gaps.lg};
    }
    
    ${mediaQueries.xl} {
      gap: ${gridSystem.gaps.xl};
    }
  `
};

export default {
  breakpoints,
  mediaQueries,
  containerMaxWidths,
  gridSystem,
  fontSizes,
  spacing,
  layoutHelpers
};

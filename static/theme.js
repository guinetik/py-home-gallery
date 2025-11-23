/**
 * Theme Management for Py Home Gallery
 * Handles light/dark mode with system preference support
 */

// Theme constants
const THEME_STORAGE_KEY = 'py-home-gallery-theme';
const THEME_LIGHT = 'light';
const THEME_DARK = 'dark';

/**
 * Get the current theme preference
 * Priority: localStorage > system preference > dark (default)
 */
function getThemePreference() {
    // Check localStorage first
    const stored = localStorage.getItem(THEME_STORAGE_KEY);
    if (stored) {
        return stored;
    }

    // Check system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
        return THEME_LIGHT;
    }

    // Default to dark
    return THEME_DARK;
}

/**
 * Apply theme to the document
 */
function applyTheme(theme) {
    if (theme === THEME_LIGHT) {
        document.documentElement.setAttribute('data-theme', 'light');
    } else {
        document.documentElement.removeAttribute('data-theme');
    }

    // Update toggle button icon if it exists
    const toggleBtn = document.getElementById('theme-toggle');
    if (toggleBtn) {
        toggleBtn.textContent = theme === THEME_LIGHT ? '🌙' : '☀️';
        toggleBtn.setAttribute('aria-label', `Switch to ${theme === THEME_LIGHT ? 'dark' : 'light'} mode`);
    }
}

/**
 * Toggle between light and dark themes
 */
function toggleTheme() {
    const currentTheme = getThemePreference();
    const newTheme = currentTheme === THEME_LIGHT ? THEME_DARK : THEME_LIGHT;

    // Save to localStorage
    localStorage.setItem(THEME_STORAGE_KEY, newTheme);

    // Apply the theme
    applyTheme(newTheme);
}

/**
 * Initialize theme on page load
 * Call this ASAP to prevent flash of wrong theme
 */
function initTheme() {
    const theme = getThemePreference();
    applyTheme(theme);
}

/**
 * Listen for system theme changes
 */
function watchSystemTheme() {
    if (window.matchMedia) {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: light)');

        // Only respond to system changes if user hasn't manually set a preference
        mediaQuery.addEventListener('change', (e) => {
            const hasManualPreference = localStorage.getItem(THEME_STORAGE_KEY);
            if (!hasManualPreference) {
                applyTheme(e.matches ? THEME_LIGHT : THEME_DARK);
            }
        });
    }
}

/**
 * Create and inject the theme toggle button
 */
function createThemeToggle() {
    // Check if button already exists
    if (document.getElementById('theme-toggle')) {
        return;
    }

    const button = document.createElement('button');
    button.id = 'theme-toggle';
    button.className = 'theme-toggle';
    button.setAttribute('aria-label', 'Toggle theme');
    button.addEventListener('click', toggleTheme);

    // Try to add to navbar first, otherwise add to body
    const nav = document.querySelector('nav');
    const navButtons = nav?.querySelector('.filter-buttons');

    if (navButtons) {
        // Add to navbar filter buttons
        navButtons.appendChild(button);
    } else if (nav) {
        // Add directly to nav if no filter-buttons container
        nav.appendChild(button);
    } else {
        // Fallback: add to body (for pages without nav)
        document.body.appendChild(button);
    }

    // Set initial icon
    const currentTheme = getThemePreference();
    button.textContent = currentTheme === THEME_LIGHT ? '🌙' : '☀️';
}

// Initialize theme immediately (before DOM loads) to prevent flash
initTheme();

// Setup everything else when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        createThemeToggle();
        watchSystemTheme();
    });
} else {
    // DOM already loaded
    createThemeToggle();
    watchSystemTheme();
}

// Export functions for manual use if needed
window.themeManager = {
    toggle: toggleTheme,
    apply: applyTheme,
    get: getThemePreference
};

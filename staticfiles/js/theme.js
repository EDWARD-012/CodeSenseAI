/**
 * Theme Manager for CodeSense AI.
 * Handles dark/light theme switching with localStorage persistence.
 * Syncs Monaco Editor theme on toggle.
 */
const ThemeManager = (() => {
  const STORAGE_KEY = 'codesense-theme';

  function getPreferred() {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) return saved;
    return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
  }

  function apply(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(STORAGE_KEY, theme);
    // Sync Monaco theme if Editor module is loaded
    if (typeof Editor !== 'undefined' && Editor.updateTheme) {
      Editor.updateTheme(theme);
    }
  }

  function toggle() {
    const current = document.documentElement.getAttribute('data-theme') || 'dark';
    apply(current === 'dark' ? 'light' : 'dark');
  }

  function init() {
    apply(getPreferred());

    const toggleEl = document.getElementById('theme-toggle');
    if (toggleEl) {
      toggleEl.addEventListener('click', toggle);
      toggleEl.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(); }
      });
    }
  }

  return { init, toggle, apply };
})();

// Initialize immediately to prevent flash of wrong theme
ThemeManager.apply(localStorage.getItem('codesense-theme') ||
  (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark'));

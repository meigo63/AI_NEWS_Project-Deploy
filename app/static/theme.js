/**
 * Dark Mode Theme Manager
 * Handles theme persistence, system preference detection, and UI updates
 */
;(function(){
  const THEME_KEY = 'app-theme';
  const root = document.documentElement;
  const toggle = document.getElementById('themeToggle');
  
  /**
   * Apply theme to the entire application
   */
  function applyTheme(theme) {
    if (theme === 'dark') {
      root.setAttribute('data-theme', 'dark');
      document.body.classList.add('bg-dark', 'text-light');
      // Update Bootstrap classes
      document.querySelectorAll('.navbar-light').forEach(el => {
        el.classList.remove('navbar-light');
        el.classList.add('navbar-dark');
      });
    } else {
      root.setAttribute('data-theme', 'light');
      document.body.classList.remove('bg-dark', 'text-light');
      // Update Bootstrap classes
      document.querySelectorAll('.navbar-dark').forEach(el => {
        el.classList.remove('navbar-dark');
        el.classList.add('navbar-light');
      });
    }
  }
  
  /**
   * Get user's preferred theme
   * 1. Check localStorage
   * 2. Check system preference
   * 3. Default to light
   */
  function getPreferredTheme() {
    // Check localStorage
    const stored = localStorage.getItem(THEME_KEY);
    if (stored) return stored;
    
    // Check system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    
    return 'light';
  }
  
  /**
   * Initialize theme on page load
   */
  function initialize() {
    const preferredTheme = getPreferredTheme();
    applyTheme(preferredTheme);
    
    if (toggle) {
      toggle.checked = preferredTheme === 'dark';
    }
  }
  
  /**
   * Handle theme toggle
   */
  if (toggle) {
    toggle.addEventListener('change', function(e) {
      const newTheme = e.target.checked ? 'dark' : 'light';
      localStorage.setItem(THEME_KEY, newTheme);
      applyTheme(newTheme);
    });
  }
  
  /**
   * Listen for system theme changes
   */
  if (window.matchMedia) {
    const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
    darkModeQuery.addListener(function(e) {
      if (!localStorage.getItem(THEME_KEY)) {
        applyTheme(e.matches ? 'dark' : 'light');
        if (toggle) toggle.checked = e.matches;
      }
    });
  }
  
  // Initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
  } else {
    initialize();
  }
})();

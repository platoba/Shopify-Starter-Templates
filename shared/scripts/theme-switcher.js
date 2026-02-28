/**
 * Shopify Starter Templates — Theme Switcher
 * Allows one-click theme switching and persists preference
 */
(function () {
  'use strict';

  const THEMES = ['ocean', 'emerald', 'sunset', 'royal', 'crimson', 'midnight'];
  const STORAGE_KEY = 'sst_theme';

  function setTheme(theme) {
    if (!THEMES.includes(theme)) theme = 'ocean';
    document.documentElement.setAttribute('data-theme', theme);
    try { localStorage.setItem(STORAGE_KEY, theme); } catch {}
  }

  function getTheme() {
    try { return localStorage.getItem(STORAGE_KEY) || 'ocean'; } catch { return 'ocean'; }
  }

  function createSwitcherUI() {
    const switcher = document.getElementById('theme-switcher');
    if (!switcher) return;

    const colors = {
      ocean: '#2563eb', emerald: '#059669', sunset: '#ea580c',
      royal: '#7c3aed', crimson: '#dc2626', midnight: '#6366f1',
    };

    const current = getTheme();
    switcher.innerHTML = THEMES.map(t => `
      <button onclick="window.SST_Theme.set('${t}')"
        title="${t.charAt(0).toUpperCase() + t.slice(1)}"
        class="w-8 h-8 rounded-full border-2 transition-all hover:scale-110 focus:outline-none focus:ring-2 focus:ring-offset-2"
        style="background-color: ${colors[t]}; border-color: ${t === current ? '#111827' : 'transparent'}"
        aria-label="Switch to ${t} theme">
      </button>
    `).join('');
  }

  // Apply saved theme immediately (before paint)
  setTheme(getTheme());

  // Build UI after DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createSwitcherUI);
  } else {
    createSwitcherUI();
  }

  window.SST_Theme = {
    set(theme) { setTheme(theme); createSwitcherUI(); },
    get: getTheme,
    themes: THEMES,
  };
})();

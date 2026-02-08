# Dark Mode Configuration

## Overview

The application now includes a comprehensive dark mode system that works across all pages. Users can toggle between light and dark themes with preference persistence.

---

## Features

✅ **System Preference Detection** - Automatically uses OS dark mode preference on first visit  
✅ **localStorage Persistence** - User preference saved across sessions  
✅ **Smooth Transitions** - 0.3s color transitions between themes  
✅ **Complete Coverage** - All components (cards, forms, tables, alerts, modals, etc.) styled  
✅ **Navbar Integration** - Theme toggle button in the navbar  
✅ **Responsive** - Works on all screen sizes  

---

## How It Works

### Toggle Location
- **Navbar** → Look for the moon icon (☀️/🌙) on the right side
- Click to toggle between light and dark modes

### Preference Storage
- User preference saved in **localStorage** with key `app-theme`
- Persists across browser sessions
- Can be cleared by clearing browser data

### System Integration
- If no saved preference, detects system dark mode setting
- Updates automatically if system theme changes (and no user preference set)

---

## CSS Variables

The dark mode uses CSS custom properties (variables) for easy customization:

### Light Mode
```css
--bg: #ffffff
--fg: #212529
--card-bg: #ffffff
--input-bg: #ffffff
--navbar-bg: #f8f9fa
```

### Dark Mode
```css
--bg: #0d1117
--fg: #e9ecef
--card-bg: #1c2128
--input-bg: #0d1117
--navbar-bg: #161b22
```

---

## Styled Components

All components are fully styled for both themes:

- **Navbar** - Background, text, links
- **Cards** - Background, borders, shadows
- **Forms** - Inputs, selects, placeholders
- **Tables** - Striped rows, hover effects
- **Alerts** - Info, danger, warning, success
- **Buttons** - Primary, secondary, outline variants
- **Badges** - All color variants
- **Modals** - Content, headers, footers
- **Dropdowns** - Menu items, dividers
- **Pagination** - Links, active states
- **List Groups** - Items, active states
- **Scrollbars** - Custom styled for each theme

---

## Technical Details

### JavaScript (theme.js)
- Handles localStorage persistence
- Detects system preference using `prefers-color-scheme`
- Applies theme on page load
- Listens to system theme changes
- Updates Bootstrap navbar classes dynamically

### CSS (style.css)
- 400+ lines of theme-aware styling
- Uses CSS custom properties for easy maintenance
- Smooth transitions on all color changes
- Responsive design patterns

### HTML (base.html)
- Theme toggle in navbar
- Moon icon indicator
- Accessible checkbox input

---

## Browser Support

✅ Chrome/Edge 76+  
✅ Firefox 67+  
✅ Safari 12.1+  
✅ Mobile browsers (iOS Safari 13+, Chrome Mobile)

---

## Customization

### Add Custom Colors

Edit `style.css` and add to the `:root[data-theme='dark']` section:

```css
:root[data-theme='dark']{
  --custom-color: #your-color;
  /* ... other variables ... */
}
```

Then use in your styles:
```css
.my-element {
  color: var(--custom-color);
}
```

### Change Default Theme

In `theme.js`, modify `getPreferredTheme()` function:

```javascript
return 'dark'; // Change default to dark
```

### Disable System Preference

Remove or comment out the system preference detection in `theme.js`:

```javascript
// if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
//   return 'dark';
// }
```

---

## Testing

### Test Dark Mode:
1. Click the moon icon in the navbar
2. Refresh the page (preference should persist)
3. Check all pages: Home, Classify, History, Admin panel
4. Verify cards, forms, tables, alerts all styled correctly

### Test Light Mode:
1. Click the moon icon again
2. Verify all elements switch back to light colors

### Test System Preference:
1. Clear localStorage (DevTools → Application → Storage)
2. Change OS theme in system settings
3. Reload the page (should match OS theme)

---

## Performance

- CSS variables are efficient - no JavaScript processing needed for styling
- Smooth 0.3s transitions don't impact performance
- localStorage is lightweight
- No external theme libraries - pure CSS/JS

---

## Accessibility

- Theme toggle labeled with `title` attribute
- High contrast ratios for readability
- Works with keyboard navigation
- Respects `prefers-color-scheme` media query

---

## Troubleshooting

### Theme not persisting?
- Check if localStorage is enabled
- Clear browser cache and try again
- Check browser DevTools → Application → Storage

### Toggle button not showing?
- Ensure `theme.js` is loaded: Check Network tab in DevTools
- Check console for JavaScript errors

### Some elements not styled?
- Verify `.bg-dark` and `.text-light` classes aren't overriding CSS variables
- Check for inline styles that bypass CSS variables

### Colors look wrong?
- Open DevTools → Elements → Inspect the element
- Check computed styles for correct CSS variables
- Verify `data-theme` attribute is set on `<html>` tag

---

## Future Enhancements

Possible improvements:
- Add more theme options (high contrast, custom colors)
- Implement theme scheduling (auto-switch at sunset/sunrise)
- Add theme per-page override capability
- Store theme preference in user profile (for logged-in users)
- Add animation/transition preferences

---

## Support

For issues with dark mode, check:
1. Browser console for errors
2. Network tab to ensure CSS/JS loaded
3. localStorage data
4. Browser compatibility


# Adding a Logo to Your News AI Application

## Quick Start

I've created a sample logo SVG file (`logo.svg`). Here's how to implement it:

---

## Step 1: Update `base.html` Navbar

Edit `app/templates/base.html` and replace the navbar-brand section (lines 13-16):

**From:**
```html
<a class="navbar-brand" href="/">
  <i class="fas fa-newspaper"></i> NewsAI
</a>
```

**To:**
```html
<a class="navbar-brand" href="/">
  <img src="/static/logo.svg" alt="NewsAI Logo" class="navbar-logo me-2">
  <span class="navbar-brand-text">NewsAI</span>
</a>
```

---

## Step 2: Add Logo CSS Styling

Add this CSS to `app/static/css/style.css` after the `.navbar-light .navbar-toggler` rule (around line 82):

```css
/* Logo Styling */
.navbar-logo {
  height: 40px;
  width: 40px;
  object-fit: contain;
  transition: transform 0.2s ease;
}

.navbar-brand:hover .navbar-logo {
  transform: scale(1.05);
}

.navbar-brand-text {
  font-size: 1.5rem;
  font-weight: 700;
  margin-left: 0.5rem;
}
```

---

## Step 3: Test

1. Restart the app: `python run.py`
2. Navigate to `http://localhost:5000`
3. You should see the logo on the left side of the navbar

---

## Using Your Own Logo

### Option 1: PNG/JPG Logo

1. Save your logo as `logo.png` in `app/static/`
2. Update the HTML:
   ```html
   <img src="/static/logo.png" alt="NewsAI Logo" class="navbar-logo me-2">
   ```

### Option 2: SVG Logo

1. Save your logo as `logo.svg` in `app/static/`
2. Use the HTML above (already done)

### Option 3: Custom Size

If you want a larger or smaller logo, update the CSS:

```css
.navbar-logo {
  height: 50px;  /* Change from 40px to 50px */
  width: 50px;
  object-fit: contain;
  transition: transform 0.2s ease;
}
```

---

## Logo Recommendations

### Dimensions:
- **Ideal Size:** 40×40 pixels (will scale automatically)
- **File Formats:** PNG, JPG, SVG, WEBP
- **File Size:** Under 50 KB (optimize images)

### Design Guidelines:
- **Simple:** Works well at small sizes
- **Square Format:** Best for navbar logos
- **Transparent Background:** PNG with transparency recommended
- **High Contrast:** Visible in both light and dark modes

---

## Dark Mode Logo Support

The current setup works in both light and dark modes. If you want a logo that changes color based on the theme:

### Create Two Logos

1. `logo-light.svg` - For light theme
2. `logo-dark.svg` - For dark theme

### Update HTML

```html
<a class="navbar-brand" href="/">
  <img src="/static/logo.svg" alt="NewsAI Logo" class="navbar-logo me-2" id="themeLogo">
  <span class="navbar-brand-text">NewsAI</span>
</a>
```

### Add JS to `theme.js`

```javascript
// Add this inside the applyTheme() function:
const logoImg = document.getElementById('themeLogo');
if (logoImg) {
  logoImg.src = theme === 'dark' ? '/static/logo-dark.svg' : '/static/logo-light.svg';
}
```

---

## Complete Example

### The Sample Logo

I've created a newspaper icon SVG in `app/static/logo.svg`:
- Blue newspaper icon
- Circular background
- Scales well at any size
- Works in both themes

### Next Steps

1. **Use the sample:** The SVG logo is ready to use immediately
2. **Replace it:** Add your own logo (PNG/JPG/SVG) to `app/static/`
3. **Update HTML:** Follow Step 1 above
4. **Add CSS:** Follow Step 2 above
5. **Restart:** Run `python run.py`

---

## Troubleshooting

### Logo doesn't appear?
- Check file path: `/static/logo.png`
- Verify file exists in `app/static/` folder
- Clear browser cache (Ctrl+Shift+Delete)
- Check browser console for errors (F12)

### Logo looks blurry?
- Use high-resolution image (2x the display size)
- For 40×40 display, use 80×80+ image
- SVG images scale perfectly (use SVG if possible)

### Logo not showing on dark mode?
- Add CSS to make logo work both themes
- Or use separate logos for each theme
- See "Dark Mode Logo Support" above

### Logo distorted?
- Change CSS to match your logo aspect ratio
- Instead of square (40×40), try rectangular (50×30)
- Adjust height/width in CSS

---

## Files Modified/Created

✅ **Created:** `app/static/logo.svg` - Sample newspaper logo  
📝 **To Modify:** `app/templates/base.html` - Navbar section  
📝 **To Modify:** `app/static/css/style.css` - Add logo CSS  

---

## See Also

- [Dark Mode Guide](DARK_MODE_GUIDE.md) - Configure logo for dark mode
- Bootstrap Navbar Docs: https://getbootstrap.com/docs/5.3/components/navbar/
- SVG Creation Tools: https://www.canva.com, https://figma.com


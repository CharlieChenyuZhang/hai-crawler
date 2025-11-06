# Research Poster Visualization

This directory contains a poster-optimized visualization (`poster.html`) designed for printing at standard research poster sizes (typically 36" x 48" or 91cm x 122cm).

## Files

- `poster.html` - Poster-optimized HTML visualization
- `index.html` - Interactive web version
- `generate_figure.html` - Academic paper figure style

## Using the Poster

### Viewing

1. Open `poster.html` in a web browser (Chrome, Firefox, or Safari recommended)
2. The poster will be scaled down for screen viewing (40% scale)
3. All content is optimized for high-resolution printing

### Exporting for Printing

#### Option 1: Browser Print to PDF (Recommended)

1. Open `poster.html` in Chrome or Firefox
2. Press `Ctrl+P` (Windows/Linux) or `Cmd+P` (Mac) to open print dialog
3. **Settings:**
   - **Destination:** Save as PDF
   - **Paper size:** Custom (if available) or use 36" x 48"
   - **Scale:** 100% (or adjust to fit)
   - **Margins:** None or Minimum
   - **Background graphics:** ON (important for colors!)
4. Click "Save" or "Print"
5. The PDF can then be sent to a print shop

#### Option 2: Screenshot/Export Tools

For high-resolution image export:

1. **Chrome DevTools:**
   - Open `poster.html` in Chrome
   - Press `F12` to open DevTools
   - Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
   - Type "Capture screenshot" and select "Capture full size screenshot"
   - This will capture the entire page at full resolution

2. **Browser Extensions:**
   - Use extensions like "Full Page Screen Capture" or "GoFullPage"
   - These can capture high-resolution screenshots of the entire page

3. **Online Tools:**
   - Use services like html2pdf.com or print-friendly.com
   - Upload the HTML or provide the URL

#### Option 3: Programmatic Export (Advanced)

You can use headless browsers to export:

```bash
# Using Puppeteer (Node.js)
npm install puppeteer
node export-poster.js

# Using Playwright (Python)
pip install playwright
python export_poster.py
```

## Poster Specifications

- **Target Size:** 36" x 48" (Portrait orientation)
- **Aspect Ratio:** 3:4
- **Resolution:** 150-300 DPI for printing
- **Color Mode:** RGB (will be converted to CMYK by print shop if needed)

## Customization

### Changing Dimensions

Edit the CSS in `poster.html`:

```css
.poster-container {
    /* For different sizes, adjust padding */
    padding: 60px 80px; /* Adjust for 36"x48" */
}
```

### Updating Content

1. **Title/Subtitle:** Edit the header section
2. **Statistics:** Update numbers in the stats grid
3. **Findings:** Modify the findings-grid section
4. **Colors:** Change CSS color variables

### Font Sizes

All font sizes are optimized for poster readability:
- Title: 72px
- Subtitle: 48px
- Section titles: 36px
- Body text: 18-24px

These scale automatically with the print size.

## Tips for Printing

1. **Test Print:** Print a small test page first to check colors and layout
2. **Bleed:** If your print shop requires bleed, add extra padding
3. **Colors:** Verify colors print correctly (the poster uses gradients)
4. **Fonts:** Use web-safe fonts or embed custom fonts if needed
5. **Resolution:** Ensure export is at least 150 DPI for clear printing

## Print Shop Requirements

Most print shops accept:
- PDF files (recommended)
- High-resolution PNG/JPG images
- Common sizes: 36"x48", 42"x56", 48"x60"

Check with your print shop for:
- File format preferences
- Color profile requirements (RGB vs CMYK)
- Minimum resolution requirements
- Bleed requirements

## Troubleshooting

**Issue:** Poster appears too small in browser
- **Solution:** This is normal! The poster is scaled to 40% for screen viewing. Use print preview or export to see full size.

**Issue:** Colors don't print correctly
- **Solution:** Enable "Background graphics" in print settings. Some browsers disable this by default.

**Issue:** Text is blurry after export
- **Solution:** Use browser print-to-PDF at 100% scale, or use a headless browser with high DPI settings.

**Issue:** Layout is broken
- **Solution:** Ensure you're using a modern browser (Chrome, Firefox, Safari). The poster uses CSS Grid which requires modern browser support.

## Additional Resources

- [Poster Design Best Practices](https://www.nature.com/articles/d41586-018-07519-5)
- [Research Poster Templates](https://www.postersession.com/)
- [Printing Guidelines](https://www.printingcenterusa.com/printing-resources/print-quality-guidelines/)


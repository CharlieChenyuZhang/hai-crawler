# Research Poster Visualization

Interactive HTML/CSS/JavaScript visualization for the research poster: "Building Research-Ready Textual Datasets at Scale: An LLM Case Study on Mindfulness Prompts"

## Files

- `index.html` - Main HTML structure
- `styles.css` - Styling and animations
- `script.js` - Interactive JavaScript features

## Features

### Visual Components

1. **Pipeline Architecture** - Shows the 3-stage process:
   - Stage 1: Query Generation (SerpAPI)
   - Stage 2: Parallel Crawling & Extraction (Firecrawl)
   - Stage 3: Enrichment & Classification (GPT-4)

2. **Dataset Statistics** - Key numbers:
   - 64,242 unique prompts
   - 2,081 domains
   - 1 hour collection time
   - 29 search queries

3. **Topic Distribution** - Visual bars showing:
   - Self-Reflection & Individuality (52.8%)
   - Emotions & Gratitude (5.1%)
   - Other topics (42.1%)

4. **Substantive Insights** - Four key findings with icons

5. **Output Format** - Data structure visualization

6. **Research Implications** - Three main contributions

## Interactive Features

- **Animated statistics** - Numbers count up when scrolled into view
- **Animated topic bars** - Progress bars animate on scroll
- **Clickable pipeline stages** - Click stages to highlight them
- **Hover effects** - Ripple effects on cards
- **Responsive design** - Works on desktop, tablet, and mobile

## Usage

Simply open `index.html` in a web browser. No server or build process required.

For best results:
- Use a modern browser (Chrome, Firefox, Safari, Edge)
- Works best on desktop for poster viewing
- Mobile-responsive for smaller screens

## Customization

### Colors

Edit the CSS variables in `styles.css`:

```css
:root {
    --primary-color: #2563eb;
    --secondary-color: #7c3aed;
    --accent-color: #10b981;
    /* ... */
}
```

### Content

Edit the HTML in `index.html` to update:
- Statistics
- Findings
- Topic percentages
- Any text content

## Browser Compatibility

- Chrome/Edge (recommended)
- Firefox
- Safari
- Mobile browsers (responsive)

## Print/PDF

For poster printing, use browser's "Print to PDF" feature:
1. Open the page in browser
2. Right-click → Print
3. Save as PDF
4. Scale appropriately for poster size


# Research Paper Charts

This directory contains publication-quality data visualizations for your research paper.

## Files

- **`research_charts.html`** - Interactive charts using Chart.js
  - Figure 1: Topic Distribution (Bar chart)
  - Figure 2: Top Verbs (Bar chart)
  - Figure 3: Numerical Scaffolding (Bar chart)
  - Figure 4: Temporal References (Pie chart)

## Usage for Paper Inclusion

### Method 1: Export Individual Charts (Recommended)

1. Open `research_charts.html` in Chrome/Firefox
2. Right-click on each chart canvas element
3. Select "Save image as..." or use browser screenshot
4. Save as PNG (high quality)

### Method 2: Print to PDF

1. Open `research_charts.html` in browser
2. Press `Ctrl+P` (or `Cmd+P` on Mac)
3. Select "Save as PDF"
4. Set margins to "None"
5. Print each chart separately by scrolling

### Method 3: Screenshot with Developer Tools

1. Open `research_charts.html`
2. Press F12 to open Developer Tools
3. Right-click on the canvas element → "Capture node screenshot"
4. This ensures pixel-perfect rendering

## Chart Details

### Figure 1: Topic Distribution
- Shows all 10 clusters from K-Means analysis
- Cluster 1 (Self-Reflection & Individuality) at 52.8%
- Horizontal bar chart for readability

### Figure 2: Top Verbs
- Shows frequency of most common action verbs
- "feel" (7,544), "write" (5,969), "make" (5,515) are top 3
- Illustrates reflective language patterns

### Figure 3: Numerical Scaffolding
- Shows distribution of list-length numbers
- Numbers 3, 5, and 10 most common
- Demonstrates preference for structured reflection

### Figure 4: Temporal References
- Pie chart showing temporal vs. non-temporal prompts
- Only 3.8% contain explicit time frames
- "This week" (30.9%) and "this year" (29.5%) are most common

## LaTeX Integration

For LaTeX papers, you can include the exported images:

```latex
\begin{figure}[h]
    \centering
    \includegraphics[width=0.9\textwidth]{figure1_topic_distribution.png}
    \caption{Distribution of prompt topics across 10 clusters identified through K-Means clustering.}
    \label{fig:topics}
\end{figure}
```

## Customization

### Adjust Colors (for color printing)
Edit the `backgroundColor` arrays in the JavaScript:
- Currently uses blue/steel blue shades
- For black & white: use grayscale values like `rgba(100, 100, 100, 0.8)`

### Adjust Sizes
Modify `aspectRatio` in chart options:
- Lower values = wider charts
- Higher values = taller charts

### Font Sizes
Charts use Times New Roman at various sizes (9-11pt) suitable for papers.

## Notes

- Charts are optimized for print/PDF export
- All data comes from your analysis outputs
- Colors work in both color and grayscale printing
- Font sizes match academic paper standards


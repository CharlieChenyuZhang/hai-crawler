# Camera-Ready Research Paper Figure

## Files

1. **`pipeline_diagram.html`** - Clean pipeline architecture diagram with statistics
2. **`generate_figure.html`** - More detailed version with output format included

## Usage for Paper Inclusion

### Option 1: Direct HTML to PDF

1. Open `generate_figure.html` in Chrome/Firefox
2. Press `Ctrl+P` (or `Cmd+P` on Mac)
3. Select "Save as PDF"
4. Set margins to "None" or "Minimum"
5. Set scale to 100%
6. Save the PDF
7. Include the PDF in your LaTeX document using `\includegraphics{figure.pdf}`

### Option 2: Screenshot Method

1. Open `generate_figure.html` in browser
2. Use browser developer tools (F12)
3. Right-click on the `.paper-figure` element → Capture node screenshot
4. This ensures clean edges and proper scaling

### Option 3: LaTeX Integration (Recommended)

If using LaTeX, you can convert to PDF and include:

```latex
\begin{figure}[h]
    \centering
    \includegraphics[width=\textwidth]{pipeline_diagram.pdf}
    \caption{Three-stage LLM-augmented pipeline for harvesting and classifying mindfulness journaling prompts from the public web.}
    \label{fig:pipeline}
\end{figure}
```

## Figure Specifications

- **Width**: 900px (scalable)
- **Font**: Times New Roman (academic standard)
- **Border**: Clean, minimal
- **Color**: Black & white for print compatibility
- **Format**: Self-contained HTML, converts cleanly to PDF

## Customization

### Edit Text Content
- Open the HTML file
- Modify text in the `<div class="stage-title">` and `<div class="stage-details">` sections
- Update statistics in the metrics bar

### Adjust Size
- Modify `.paper-figure { width: 900px; }` in CSS
- For column width: `width: 480px` (single column)
- For full width: `width: 900px` (double column)

### Change Colors
- The figure uses black/white/gray for print compatibility
- Can be customized in CSS if color printing is available

## Recommended Size for Papers

- **Single column**: 480px width
- **Double column**: 900px width
- **Full page**: 1000px+ width

Adjust the `.paper-figure` width in CSS accordingly.


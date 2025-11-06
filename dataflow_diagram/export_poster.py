#!/usr/bin/env python3
"""
Export research poster to high-resolution PDF or image.

Requirements:
    pip install playwright
    playwright install chromium

Usage:
    python export_poster.py [--format pdf|png] [--output filename]
"""

import argparse
import os
import sys
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Error: playwright not installed. Install with: pip install playwright")
    print("Then run: playwright install chromium")
    sys.exit(1)


def export_poster(format_type='pdf', output_file=None, scale=1.0):
    """Export the poster HTML to PDF or PNG."""
    
    # Get the directory of this script
    script_dir = Path(__file__).parent
    poster_html = script_dir / 'poster.html'
    
    if not poster_html.exists():
        print(f"Error: {poster_html} not found!")
        sys.exit(1)
    
    # Default output filename
    if output_file is None:
        if format_type == 'pdf':
            output_file = script_dir / 'poster_export.pdf'
        else:
            output_file = script_dir / 'poster_export.png'
    
    output_path = Path(output_file)
    
    print(f"Exporting poster to {output_path}...")
    print(f"Format: {format_type.upper()}")
    print(f"Scale: {scale}x")
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Load the HTML file
        html_path = poster_html.absolute().as_uri()
        page.goto(html_path)
        
        # Wait for content to load
        page.wait_for_load_state('networkidle')
        
        if format_type == 'pdf':
            # Export as PDF
            # Standard poster size: 36" x 48" at 150 DPI
            # 36" * 150 = 5400px, 48" * 150 = 7200px
            # But we'll use a more reasonable size for PDF
            page.pdf(
                path=str(output_path),
                format='A0',  # A0 is close to 36"x48"
                print_background=True,
                scale=scale,
                margin={
                    'top': '0',
                    'right': '0',
                    'bottom': '0',
                    'left': '0'
                }
            )
        else:
            # Export as PNG
            # Get full page dimensions
            width = page.evaluate('document.querySelector(".poster-container").scrollWidth')
            height = page.evaluate('document.querySelector(".poster-container").scrollHeight')
            
            # Scale for high resolution (300 DPI equivalent)
            # For 36" x 48" at 300 DPI: 10800 x 14400 pixels
            # But that's very large, so we'll use a more reasonable size
            scaled_width = int(width * scale)
            scaled_height = int(height * scale)
            
            page.set_viewport_size({'width': scaled_width, 'height': scaled_height})
            page.screenshot(
                path=str(output_path),
                full_page=True,
                type='png'
            )
        
        browser.close()
    
    print(f"✓ Successfully exported to {output_path}")
    print(f"  File size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")


def main():
    parser = argparse.ArgumentParser(
        description='Export research poster to PDF or PNG',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python export_poster.py                    # Export as PDF (default)
  python export_poster.py --format png       # Export as PNG
  python export_poster.py --output my_poster.pdf
  python export_poster.py --format png --scale 2.0  # 2x resolution
        """
    )
    
    parser.add_argument(
        '--format',
        choices=['pdf', 'png'],
        default='pdf',
        help='Output format (default: pdf)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output filename (default: poster_export.pdf or poster_export.png)'
    )
    
    parser.add_argument(
        '--scale',
        type=float,
        default=1.0,
        help='Scale factor for export (default: 1.0, use 2.0 for higher resolution)'
    )
    
    args = parser.parse_args()
    
    try:
        export_poster(
            format_type=args.format,
            output_file=args.output,
            scale=args.scale
        )
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()


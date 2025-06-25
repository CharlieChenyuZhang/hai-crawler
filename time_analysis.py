import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Input and output paths
INPUT_CSV = 'filtered_enriched_prompts_iso.csv'
OUTPUT_DIR = os.path.join('analysis_outputs', 'time_analysis')
os.makedirs(OUTPUT_DIR, exist_ok=True)

def parse_date(date_str):
    if pd.isna(date_str) or date_str == 'n/a':
        return None
    for fmt in ('%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d %H:%M:%S', '%Y/%m/%d', '%Y-%m-%dT%H:%M:%S%z'):
        try:
            return datetime.strptime(date_str, fmt)
        except Exception:
            continue
    try:
        return pd.to_datetime(date_str, errors='coerce')
    except Exception:
        return None

def plot_time_distribution(df, time_col, title, filename):
    dates = df[time_col].apply(parse_date)
    dates = dates.dropna()
    date_counts = dates.dt.date.value_counts().sort_index()
    plt.figure(figsize=(12, 6))
    plt.plot(date_counts.index, date_counts.values, marker='o')
    plt.xlabel('Date')
    plt.ylabel('Number of Prompts')
    plt.title(title)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename))
    plt.close()

def plot_year_distribution(df, time_col, title, filename):
    dates = df[time_col].apply(parse_date)
    dates = dates.dropna()
    years = dates.dt.year
    year_counts = years.value_counts().sort_index()
    plt.figure(figsize=(10, 5))
    plt.bar(year_counts.index.astype(str), year_counts.values)
    plt.xlabel('Year')
    plt.ylabel('Number of Prompts')
    plt.title(title)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename))
    plt.close()

def main():
    df = pd.read_csv(INPUT_CSV)
    plot_time_distribution(df, 'published_time', 'Distribution of Published Time (by Date)', 'published_time_distribution.png')
    plot_year_distribution(df, 'published_time', 'Distribution of Published Time (by Year)', 'published_time_by_year.png')
    print(f"Plots saved in {OUTPUT_DIR}")

if __name__ == '__main__':
    main() 
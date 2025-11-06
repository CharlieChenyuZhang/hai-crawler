#!/usr/bin/env python3
"""
t-SNE Visualization for Prompts

This script loads prompts from prompts_with_clusters.csv, vectorizes them using TF-IDF,
applies t-SNE dimensionality reduction, and visualizes the results colored by cluster.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.manifold import TSNE
import argparse
import os

def load_data(csv_path):
    """Load the prompts CSV file."""
    df = pd.read_csv(csv_path)
    if 'prompt' not in df.columns:
        raise ValueError("CSV must contain a 'prompt' column")
    
    # Remove rows with missing prompts
    df = df.dropna(subset=['prompt']).reset_index(drop=True)
    
    # Check if cluster column exists
    has_cluster = 'cluster' in df.columns
    
    return df, has_cluster

def vectorize_prompts(prompts, max_features=5000, max_df=0.8, min_df=5):
    """
    Convert text prompts to TF-IDF vectors.
    
    Parameters:
    - prompts: list of prompt strings
    - max_features: maximum number of features to keep
    - max_df: ignore terms that appear in more than this proportion of documents
    - min_df: ignore terms that appear in fewer than this many documents
    """
    print("Vectorizing prompts using TF-IDF...")
    vectorizer = TfidfVectorizer(
        max_features=max_features,
        max_df=max_df,
        min_df=min_df,
        stop_words='english',
        ngram_range=(1, 2)  # Include unigrams and bigrams
    )
    X = vectorizer.fit_transform(prompts)
    print(f"Vectorized {len(prompts)} prompts into {X.shape[1]} features")
    return X, vectorizer

def apply_tsne(X, n_components=2, perplexity=30, n_iter=1000, random_state=42):
    """
    Apply t-SNE dimensionality reduction.
    
    Parameters:
    - X: sparse or dense matrix of features
    - n_components: number of dimensions (2 for visualization)
    - perplexity: balance between local and global structure (typically 5-50)
    - n_iter: maximum number of iterations
    - random_state: for reproducibility
    """
    print(f"Applying t-SNE (perplexity={perplexity}, n_iter={n_iter})...")
    
    # Adjust perplexity if we have fewer samples than perplexity
    n_samples = X.shape[0]
    if perplexity >= n_samples:
        perplexity = max(5, n_samples - 1)
        print(f"Adjusted perplexity to {perplexity} (sample size: {n_samples})")
    
    tsne = TSNE(
        n_components=n_components,
        perplexity=perplexity,
        n_iter=n_iter,
        random_state=random_state,
        verbose=1
    )
    
    # Convert sparse matrix to dense if needed
    if hasattr(X, 'toarray'):
        X_dense = X.toarray()
    else:
        X_dense = X
    
    X_tsne = tsne.fit_transform(X_dense)
    print("t-SNE completed!")
    return X_tsne

def visualize_tsne(X_tsne, clusters=None, output_path='tsne_visualization.png', 
                   title='t-SNE Visualization of Prompts', figsize=(12, 10)):
    """
    Create a scatter plot of t-SNE results, colored by cluster if available.
    
    Parameters:
    - X_tsne: 2D array from t-SNE
    - clusters: array of cluster labels (optional)
    - output_path: path to save the figure
    - title: plot title
    - figsize: figure size
    """
    plt.figure(figsize=figsize)
    
    if clusters is not None:
        # Color by cluster
        unique_clusters = sorted(clusters.unique()) if hasattr(clusters, 'unique') else sorted(set(clusters))
        n_clusters = len(unique_clusters)
        
        # Use a colormap
        cmap = plt.cm.get_cmap('tab20' if n_clusters <= 20 else 'tab20b')
        colors = [cmap(i / max(1, n_clusters - 1)) for i in range(n_clusters)]
        
        for i, cluster_id in enumerate(unique_clusters):
            mask = clusters == cluster_id
            plt.scatter(
                X_tsne[mask, 0],
                X_tsne[mask, 1],
                c=[colors[i]],
                label=f'Cluster {cluster_id}',
                alpha=0.6,
                s=20
            )
        
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', ncol=1, fontsize=8)
        title += f' (Colored by {n_clusters} Clusters)'
    else:
        # Single color if no clusters
        plt.scatter(X_tsne[:, 0], X_tsne[:, 1], alpha=0.6, s=20, c='blue')
        title += ' (No Cluster Information)'
    
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel('t-SNE Component 1', fontsize=12)
    plt.ylabel('t-SNE Component 2', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Visualization saved to {output_path}")
    
    # Also show the plot
    plt.show()

def main():
    parser = argparse.ArgumentParser(
        description='Apply t-SNE visualization to prompts from CSV file'
    )
    parser.add_argument(
        'csv_path',
        type=str,
        default='analysis_outputs/prompts_with_clusters.csv',
        nargs='?',
        help='Path to the CSV file containing prompts (default: analysis_outputs/prompts_with_clusters.csv)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='analysis_outputs/tsne_visualization.png',
        help='Output path for the visualization (default: analysis_outputs/tsne_visualization.png)'
    )
    parser.add_argument(
        '--perplexity',
        type=int,
        default=30,
        help='t-SNE perplexity parameter (default: 30)'
    )
    parser.add_argument(
        '--n-iter',
        type=int,
        default=1000,
        help='Number of iterations for t-SNE (default: 1000)'
    )
    parser.add_argument(
        '--max-features',
        type=int,
        default=5000,
        help='Maximum number of TF-IDF features (default: 5000)'
    )
    parser.add_argument(
        '--sample-size',
        type=int,
        default=None,
        help='Randomly sample this many prompts (useful for large datasets, default: use all)'
    )
    parser.add_argument(
        '--random-seed',
        type=int,
        default=42,
        help='Random seed for reproducibility (default: 42)'
    )
    
    args = parser.parse_args()
    
    # Set random seed
    np.random.seed(args.random_seed)
    
    # Load data
    print(f"Loading data from {args.csv_path}...")
    df, has_cluster = load_data(args.csv_path)
    print(f"Loaded {len(df)} prompts")
    
    # Sample if requested
    if args.sample_size and args.sample_size < len(df):
        print(f"Sampling {args.sample_size} prompts...")
        df = df.sample(n=args.sample_size, random_state=args.random_seed).reset_index(drop=True)
        print(f"Using {len(df)} prompts for visualization")
    
    # Extract prompts
    prompts = df['prompt'].tolist()
    
    # Vectorize
    X, vectorizer = vectorize_prompts(prompts, max_features=args.max_features)
    
    # Apply t-SNE
    X_tsne = apply_tsne(
        X,
        perplexity=args.perplexity,
        n_iter=args.n_iter,
        random_state=args.random_seed
    )
    
    # Get cluster labels if available
    clusters = df['cluster'] if has_cluster else None
    if clusters is not None:
        print(f"Visualizing with {clusters.nunique()} clusters")
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Visualize
    visualize_tsne(
        X_tsne,
        clusters=clusters,
        output_path=args.output,
        title='t-SNE Visualization of Journaling Prompts'
    )
    
    print("\nDone!")

if __name__ == '__main__':
    main()


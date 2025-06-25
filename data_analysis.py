#!/usr/bin/env python3
"""
analysis_pipeline.py

A combined pipeline to run:
 1. Thematic Clustering
 2. Topic Modeling
 3. Frequent Prompt Analysis
 4. Time-Frame Anchor Detection
 5. Number Mention Counting
 6. Verb Frequency Analysis

Adjust parameters and output paths below or via command-line flags.

FIXME: remember to dedup.
"""

import os
import re
import argparse
import pandas as pd
import numpy as np
from collections import Counter

# sklearn for clustering
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# gensim for LDA
from gensim import corpora, models
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# spaCy for verb extraction
import spacy

# -----------------------------------------------------------------------------
# 0. Load data
# -----------------------------------------------------------------------------
def load_prompts(csv_path):
    df = pd.read_csv(csv_path)
    if 'prompt' not in df.columns:
        raise ValueError("CSV must contain a 'prompt' column")
    return df.dropna(subset=['prompt']).reset_index(drop=True)

# -----------------------------------------------------------------------------
# 1. Thematic Clustering
# -----------------------------------------------------------------------------
def run_clustering(df, n_clusters, out_dir):
    vectorizer = TfidfVectorizer(max_df=0.8, min_df=5, stop_words='english')
    X = vectorizer.fit_transform(df['prompt'])
    km = KMeans(n_clusters=n_clusters, random_state=42)
    df['cluster'] = km.fit_predict(X)

    # save prompts with cluster labels
    out_csv = os.path.join(out_dir, "prompts_with_clusters.csv")
    df.to_csv(out_csv, index=False)
    print(f"[1] Saved clustered prompts → {out_csv}")

    # share distribution
    shares = df['cluster'].value_counts(normalize=True).sort_index() * 100
    with open(os.path.join(out_dir, "cluster_shares.txt"), 'w') as f:
        f.write(f"Cluster shares (% of corpus):\n")
        for i, pct in shares.items():
            f.write(f"  Cluster {i}: {pct:.1f}%\n")

    # representative prompts (closest to centroid)
    order_centroids = km.cluster_centers_.argsort()[:, ::-1]
    terms = vectorizer.get_feature_names_out()
    with open(os.path.join(out_dir, "cluster_representatives.txt"), 'w') as f:
        for i in range(n_clusters):
            centroid = km.cluster_centers_[i]
            dists = np.linalg.norm(X - centroid, axis=1)
            reps = df.loc[np.argsort(dists)[:2], 'prompt'].tolist()
            f.write(f"Cluster {i} examples:\n")
            f.write(f"  1) {reps[0]}\n")
            f.write(f"  2) {reps[1]}\n\n")
    print(f"[1] Saved cluster shares & representatives → {out_dir}")

# -----------------------------------------------------------------------------
# 2. Topic Modeling
# -----------------------------------------------------------------------------
def run_topic_modeling(df, num_topics, num_words, out_dir):
    nltk.download('punkt')
    nltk.download('stopwords')
    stop = set(stopwords.words('english'))

    texts = [
        [w for w in word_tokenize(doc.lower()) if w.isalpha() and w not in stop]
        for doc in df['prompt']
    ]
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]
    lda = models.LdaModel(
        corpus, num_topics=num_topics, id2word=dictionary,
        passes=10, random_state=42
    )

    out_txt = os.path.join(out_dir, "lda_topics.txt")
    with open(out_txt, 'w') as f:
        for idx, topic in lda.print_topics(num_topics=num_topics, num_words=num_words):
            f.write(f"Topic {idx}: {topic}\n")
    print(f"[2] Saved LDA topics → {out_txt}")

# -----------------------------------------------------------------------------
# 3. Frequent Prompt Analysis
# -----------------------------------------------------------------------------
def run_frequency_analysis(df, top_n, out_dir):
    counts = Counter(df['prompt'])
    top = counts.most_common(top_n)
    out_csv = os.path.join(out_dir, "top_prompts.csv")
    pd.DataFrame(top, columns=['prompt','count']).to_csv(out_csv, index=False)
    print(f"[3] Saved top {top_n} prompts → {out_csv}")

# -----------------------------------------------------------------------------
# 4. Time-Frame Anchor Detection
# -----------------------------------------------------------------------------
TIME_REGEX = re.compile(
    r'\b(last|this|next)\s+(week|month|year|day|quarter|fortnight)\b',
    flags=re.IGNORECASE
)

def run_timeframe_analysis(df, out_dir):
    matches = df['prompt'].str.count(TIME_REGEX)
    total, with_frame = len(df), (matches>0).sum()
    perc = with_frame/total*100

    out_txt = os.path.join(out_dir, "timeframe_stats.txt")
    with open(out_txt, 'w') as f:
        f.write(f"{perc:.1f}% of prompts contain an explicit time frame.\n\n")
        # breakdown
        all_frames = df['prompt'].str.findall(TIME_REGEX).explode().dropna()
        frame_counts = all_frames.apply(lambda x: ' '.join(x)).value_counts(normalize=True)*100
        f.write("Top time-frames:\n")
        for frame, pct in frame_counts.head(3).items():
            f.write(f"  {frame}: {pct:.1f}%\n")
    print(f"[4] Saved time-frame stats → {out_txt}")

# -----------------------------------------------------------------------------
# 5. Number Mention Counting
# -----------------------------------------------------------------------------
def run_number_analysis(df, top_n, out_dir):
    nums = re.findall(r'\b(\d+)\b', ' '.join(df['prompt']))
    counts = Counter(nums).most_common(top_n)
    out_csv = os.path.join(out_dir, "top_numbers.csv")
    pd.DataFrame(counts, columns=['number','count']).to_csv(out_csv, index=False)
    print(f"[5] Saved top {top_n} numbers → {out_csv}")

# -----------------------------------------------------------------------------
# 6. Verb Frequency Analysis
# -----------------------------------------------------------------------------
def run_verb_analysis(df, top_n, out_dir):
    nlp = spacy.load("en_core_web_sm") # FIXME: use a _lg model instead
    verb_lemmas = []
    for doc in nlp.pipe(df['prompt'], batch_size=50):
        verb_lemmas.extend([t.lemma_ for t in doc if t.pos_=="VERB"])
    counts = Counter(verb_lemmas).most_common(top_n)
    out_csv = os.path.join(out_dir, "top_verbs.csv")
    pd.DataFrame(counts, columns=['verb','count']).to_csv(out_csv, index=False)
    print(f"[6] Saved top {top_n} verbs → {out_csv}")

# -----------------------------------------------------------------------------
# Main & Argument Parsing
# -----------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Run full prompts analysis pipeline.")
    parser.add_argument("csv", help="Path to filtered_enriched_prompts_subset.csv")
    parser.add_argument("--out", default="analysis_outputs",
                        help="Output directory (will be created if needed)")
    parser.add_argument("--clusters", type=int, default=6, help="Number of clusters")
    parser.add_argument("--topics", type=int, default=6, help="Number of LDA topics")
    parser.add_argument("--topic_words", type=int, default=8, help="Words per LDA topic")
    parser.add_argument("--top_prompts", type=int, default=30, help="How many top prompts")
    parser.add_argument("--top_numbers", type=int, default=10, help="How many top numbers")
    parser.add_argument("--top_verbs", type=int, default=5, help="How many top verbs")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    df = load_prompts(args.csv)

    run_clustering(df, args.clusters, args.out)
    run_topic_modeling(df, args.topics, args.topic_words, args.out)
    run_frequency_analysis(df, args.top_prompts, args.out)
    run_timeframe_analysis(df, args.out)
    run_number_analysis(df, args.top_numbers, args.out)
    run_verb_analysis(df, args.top_verbs, args.out)

    print("✅ All analyses complete.")

if __name__ == "__main__":
    main()

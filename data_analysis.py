#!/usr/bin/env python3
"""
analysis_pipeline.py

A combined pipeline that also generates a final_output.txt
matching the Chenyu Data Analysis Outline JUN 16.
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
from dotenv import load_dotenv
# spaCy for verb extraction
import spacy

from openai import OpenAI
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment. Please add it to your .env file.")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# -----------------------------------------------------------------------------
# 0. Load data
# -----------------------------------------------------------------------------
def load_prompts(csv_path):
    df = pd.read_csv(csv_path)
    if 'prompt' not in df.columns:
        raise ValueError("CSV must contain a 'prompt' column")
    return df.dropna(subset=['prompt']).reset_index(drop=True)

def name_cluster(reps, top_terms):
    """
    reps:  list of 2 rep prompts for the cluster
    top_terms: list of top-3 terms for the cluster
    """
    prompt = (
        "You are clustering user‐generated prompts. "
        "Given these representative examples:\n\n"
        + "\n".join(f"- {ex}" for ex in reps)
        + "\n\nAnd these keywords: "
        + ", ".join(top_terms)
        + "\n\nSuggest a 3–5 word descriptive theme name for this cluster."
    )
    resp = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role":"user","content":prompt}],
        temperature=0.0,
        max_tokens=32,
    )
    return resp.choices[0].message.content.strip().strip('"')

# -----------------------------------------------------------------------------
# 1. Thematic Clustering - K-Means clustering
# -----------------------------------------------------------------------------
def run_clustering(df, n_clusters, out_dir):
    vectorizer = TfidfVectorizer(max_df=0.8, min_df=5, stop_words='english')
    X = vectorizer.fit_transform(df['prompt'])
    km = KMeans(n_clusters=n_clusters, random_state=42)
    labels = km.fit_predict(X)
    df['cluster'] = labels

    # 1. Shares
    shares = (pd.Series(labels)
              .value_counts(normalize=True)
              .sort_index() * 100)

    # 2. Representative prompts
    reps = {}
    for i in range(n_clusters):
        centroid = km.cluster_centers_[i]
        # compute distance from each doc vector to this centroid
        dists = np.linalg.norm(X - centroid, axis=1)
        reps[i] = df.loc[np.argsort(dists)[:2], 'prompt'].tolist()

    # 3. Top terms per cluster → "name"
    terms = vectorizer.get_feature_names_out()
    order = km.cluster_centers_.argsort()[:, ::-1]
    top_terms = {i: [terms[idx] for idx in order[i][:3]] for i in range(n_clusters)}

    # write the existing files too
    df.to_csv(os.path.join(out_dir, "prompts_with_clusters.csv"), index=False)
    with open(os.path.join(out_dir, "cluster_shares.txt"), 'w') as f:
        f.write("Cluster shares (%):\n")
        for i, pct in shares.items():
            f.write(f"  Cluster {i+1}: {pct:.1f}%\n")
    with open(os.path.join(out_dir, "cluster_representatives.txt"), 'w') as f:
        for i in range(n_clusters):
            f.write(f"Cluster {i+1} examples:\n")
            f.write(f"  1) {reps[i][0]}\n")
            f.write(f"  2) {reps[i][1]}\n\n")

    return shares, reps, top_terms, df

# -----------------------------------------------------------------------------
# 2. Topic Modeling
# -----------------------------------------------------------------------------
def run_topic_modeling(df, num_topics, num_words, out_dir):
    nltk.download('punkt')
    nltk.download('stopwords')
    stop = set(stopwords.words('english'))

    texts = [
        [w for w in word_tokenize(doc.lower())
         if w.isalpha() and w not in stop]
        for doc in df['prompt']
    ]
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]
    lda = models.LdaModel(
        corpus, num_topics=num_topics, id2word=dictionary,
        passes=10, random_state=42
    )

    topics = {}
    for idx, topic in lda.print_topics(num_topics=num_topics,
                                       num_words=num_words):
        # parse into a clean list of keywords
        kws = re.findall(r'\"(.*?)\"', topic)
        topics[idx] = kws

    with open(os.path.join(out_dir, "lda_topics.txt"), 'w') as f:
        for idx, kws in topics.items():
            f.write(f"Topic {idx+1}: {', '.join(kws)}\n")

    return topics

# -----------------------------------------------------------------------------
# 3. Frequent Prompt Analysis
# -----------------------------------------------------------------------------
def run_frequency_analysis(df, top_n, out_dir):
    counts = Counter(df['prompt'])
    top = counts.most_common(top_n)
    with open(os.path.join(out_dir, "top_prompts.csv"), 'w') as f:
        f.write("prompt,count\n")
        for p, c in top:
            f.write(f"\"{p}\",{c}\n")
    return top

# -----------------------------------------------------------------------------
# 4. Time-Frame Anchor Detection
# -----------------------------------------------------------------------------
TIME_REGEX = re.compile(
    r'\b(last|this|next)\s+(week|month|year|day|quarter|fortnight)\b',
    flags=re.IGNORECASE
)

def run_timeframe_analysis(df, out_dir):
    matches = df['prompt'].str.count(TIME_REGEX)
    total = len(df)
    with_frame = (matches > 0).sum()
    perc = with_frame / total * 100

    # breakdown
    all_frames = df['prompt'].str.findall(TIME_REGEX) \
                   .explode().dropna() \
                   .apply(lambda x: ' '.join(x))
    frame_counts = (all_frames.value_counts(normalize=True) * 100).head(3)

    with open(os.path.join(out_dir, "timeframe_stats.txt"), 'w') as f:
        f.write(f"{perc:.1f}% of prompts contain an explicit time frame.\n\n")
        f.write("Top time frames:\n")
        for frame, pct in frame_counts.items():
            f.write(f"  {frame}: {pct:.1f}%\n")

    return perc, frame_counts.to_dict()

# -----------------------------------------------------------------------------
# 5. Number Mention Counting
# -----------------------------------------------------------------------------
def run_number_analysis(df, top_n, out_dir):
    nums = re.findall(r'\b(\d+)\b', ' '.join(df['prompt']))
    counts = Counter(nums).most_common(top_n)
    with open(os.path.join(out_dir, "top_numbers.csv"), 'w') as f:
        f.write("number,count\n")
        for num, cnt in counts:
            f.write(f"{num},{cnt}\n")
    return counts

# -----------------------------------------------------------------------------
# 6. Verb Frequency Analysis
# -----------------------------------------------------------------------------
def run_verb_analysis(df, top_n, out_dir):
    nlp = spacy.load("en_core_web_sm")
    verbs = []
    for doc in nlp.pipe(df['prompt'], batch_size=50):
        verbs.extend([t.lemma_ for t in doc if t.pos_ == "VERB"])
    counts = Counter(verbs).most_common(top_n)
    with open(os.path.join(out_dir, "top_verbs.csv"), 'w') as f:
        f.write("verb,count\n")
        for v, c in counts:
            f.write(f"{v},{c}\n")
    return counts

# -----------------------------------------------------------------------------
# Main & Argument Parsing
# -----------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Run full prompts analysis pipeline.")
    parser.add_argument("csv", help="Path to filtered_enriched_prompts_subset.csv")
    parser.add_argument("--out", default="analysis_outputs",
                        help="Output directory (will be created if needed)")
    parser.add_argument("--clusters", type=int, default=6,
                        help="Number of clusters")
    parser.add_argument("--topics", type=int, default=6,
                        help="Number of LDA topics")
    parser.add_argument("--topic_words", type=int, default=8,
                        help="Words per LDA topic")
    parser.add_argument("--top_prompts", type=int, default=30,
                        help="How many top prompts")
    parser.add_argument("--top_numbers", type=int, default=10,
                        help="How many top numbers")
    parser.add_argument("--top_verbs", type=int, default=5,
                        help="How many top verbs")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    df = load_prompts(args.csv)

    # 1. Clustering
    shares, reps, top_terms, df = run_clustering(df, args.clusters, args.out)

    # ─── generate human‐readable names ──────────────────────────────────
    cluster_names = {}
    for i in range(args.clusters):
        # reps[i] is list of two examples, top_terms[i] is list of 3 keywords
        name = name_cluster(reps[i], top_terms[i])
        cluster_names[i] = name

    # 2. Topic Modeling
    topics = run_topic_modeling(df, args.topics, args.topic_words, args.out)

    # 3. Frequency Analysis
    top_prompts = run_frequency_analysis(df, args.top_prompts, args.out)

    # 4. Time-Frame
    timeframe_perc, timeframe_top = run_timeframe_analysis(df, args.out)

    # 5. Numbers
    number_counts = run_number_analysis(df, args.top_numbers, args.out)

    # 6. Verbs
    verb_counts = run_verb_analysis(df, args.top_verbs, args.out)

    # Map each of the top prompts back to its cluster
    prompt_to_cluster = {row['prompt']: row['cluster']+1 for _, row in df.iterrows()}
    top_prompts_with_cluster = [
        (p, c, prompt_to_cluster.get(p, None))
        for p, c in top_prompts
    ]

    # Write the final_output.txt
    final_path = os.path.join(args.out, "final_output.txt")
    with open(final_path, 'w') as f:
        f.write("SECTION 1 – WHAT BIG THEMES SHAPE THE CORPUS?\n")
        f.write(f"1. {args.clusters} clusters emerge.\n")
        f.write("2. Cluster names, descriptions, and shares:\n")
        for i, pct in shares.items():
            f.write(f"  • Cluster {i+1} ({pct:.1f}%): '{cluster_names[i]}' "
                    f"(keywords: {', '.join(top_terms[i])})\n")
        f.write("3. Representative prompts:\n")
        for i, examples in reps.items():
            f.write(f"  • Cluster {i+1} examples: {examples[0]} / {examples[1]}\n")

        f.write("\nSECTION 2 – WHICH TOPICS SURFACE MOST OFTEN?\n")
        for idx, kws in topics.items():
            f.write(f"  • Topic {idx+1}: {', '.join(kws)}\n")

        f.write("\nSECTION 3 – WHICH PROMPTS KEEP COMING BACK?\n")
        for rank, (p, cnt, cl) in enumerate(top_prompts_with_cluster, start=1):
            if rank <= 10:
                f.write(f"  {rank}. '{p}' ({cnt} occurrences; cluster {cl})\n")
        f.write("  (… and up to top 30 as desired …)\n")

        f.write("\nSECTION 4 – WHEN DO PROMPTS PLACE US IN TIME?\n")
        f.write(f"8. {timeframe_perc:.1f}% of prompts contain an explicit time frame.\n")
        runners = list(timeframe_top.items())
        f.write(f"9. Most common: {runners[0][0]} ({runners[0][1]:.1f}%)\n")
        if len(runners) > 1:
            f.write(f"   Runners-up: {runners[1][0]} ({runners[1][1]:.1f}%), "
                    f"{runners[2][0]} ({runners[2][1]:.1f}%)\n")

        f.write("\nSECTION 5 – WHAT NUMBERS SHOW UP THE MOST?\n")
        for num, cnt in number_counts:
            f.write(f"  • {num} ({cnt} occurrences)\n")

        f.write("\nSECTION 6 – WHICH VERBS DRIVE THE ACTION?\n")
        # Most frequent verb
        f.write(f"11. Most frequent verb: {verb_counts[0][0]} ({verb_counts[0][1]} occurrences)\n")
        f.write("12. Next four verbs:\n")
        for v, c in verb_counts[1:5]:
            f.write(f"  • {v} ({c} occurrences)\n")

    print(f"✅ All analyses complete. Final report → {final_path}")

if __name__ == "__main__":
    main()

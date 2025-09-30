import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd

from .config import ISSUE_CONFIGS
from .reddit_client import get_reddit_client
from .data_collection import collect
from .cleaning import clean
from .analysis import extract_keywords, expand_keywords_with_variants, compute_post_sentiment, extract_important_terms, compute_term_sentiment, get_top_topic_keywords_by_frequency, aggregate_topic_keyword_sentiments
from .curation import curate_sources
from .visualization import build_dashboard
from collections import Counter


class AnalyzerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("NGO Social Issue Analyzer (Modular)")
        self.root.geometry("1400x900")

        self.reddit = get_reddit_client()
        self.issue_configs = ISSUE_CONFIGS
        self.df = pd.DataFrame()

        self._build_gui()

    def _build_gui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Control tab
        control_frame = ttk.Frame(self.notebook)
        self.notebook.add(control_frame, text="Control Panel")

        ttk.Label(control_frame, text="Select Social Issue:", font=('Arial', 12, 'bold')).pack(pady=10)
        self.issue_var = tk.StringVar()
        self.issue_combo = ttk.Combobox(control_frame, textvariable=self.issue_var,
                                        values=list(self.issue_configs.keys()), state='readonly', width=40)
        self.issue_combo.pack(pady=5)
        self.issue_combo.bind('<<ComboboxSelected>>', self._on_issue_selected)

        ttk.Label(control_frame, text="Target Subreddits:", font=('Arial', 10, 'bold')).pack(pady=(20, 5))
        self.subreddit_text = scrolledtext.ScrolledText(control_frame, height=8, width=60)
        self.subreddit_text.pack(pady=5)

        ttk.Label(control_frame, text="Data Collection:", font=('Arial', 10, 'bold')).pack(pady=(20, 5))
        ttk.Label(control_frame, text="Posts per subreddit:").pack()
        self.posts_var = tk.IntVar(value=30)
        ttk.Entry(control_frame, textvariable=self.posts_var, width=10).pack()

        ttk.Label(control_frame, text="Time filter:").pack(pady=(10, 0))
        self.time_var = tk.StringVar(value='month')
        time_combo = ttk.Combobox(control_frame, textvariable=self.time_var,
                                  values=['hour', 'day', 'week', 'month', 'year', 'all'], state='readonly', width=15)
        time_combo.pack()

        ttk.Label(control_frame, text="Collection Strategy:", font=('Arial', 10, 'bold')).pack(pady=(15, 5))
        strategy_frame = ttk.Frame(control_frame)
        strategy_frame.pack()
        self.strategy_var = tk.StringVar(value='comprehensive')
        ttk.Radiobutton(strategy_frame, text="Comprehensive (all methods)", variable=self.strategy_var, value='comprehensive').pack(side='left', padx=10)
        ttk.Radiobutton(strategy_frame, text="Fast (hot only)", variable=self.strategy_var, value='fast').pack(side='left', padx=10)

        button_frame = ttk.Frame(control_frame)
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="Collect Data", command=self._collect_data).pack(side='left', padx=5)
        self.analyze_btn = ttk.Button(button_frame, text="Analyze Data", command=self._analyze, state='disabled')
        self.analyze_btn.pack(side='left', padx=5)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(control_frame, variable=self.progress_var, maximum=100, length=400)
        self.progress_bar.pack(pady=10)
        self.status_label = ttk.Label(control_frame, text="Select an issue to begin", foreground='blue')
        self.status_label.pack(pady=5)

        # Data tab
        self.data_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.data_frame, text="Data Overview")
        ttk.Label(self.data_frame, text="Data Summary", font=('Arial', 14, 'bold')).pack(pady=10)
        self.summary_text = scrolledtext.ScrolledText(self.data_frame, height=15, width=100)
        self.summary_text.pack(pady=10, padx=10, fill='both', expand=True)

        # Analysis tab
        self.analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analysis_frame, text="Analysis Results")
        ttk.Label(self.analysis_frame, text="NLP & Statistical Analysis", font=('Arial', 14, 'bold')).pack(pady=10)
        self.analysis_text = scrolledtext.ScrolledText(self.analysis_frame, height=20, width=100)
        self.analysis_text.pack(pady=10, padx=10, fill='both', expand=True)

        # Viz tab with scrolling
        self.viz_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.viz_frame, text="Visualizations")
        
        # Create a canvas and scrollbar for scrolling
        self.viz_canvas = tk.Canvas(self.viz_frame)
        self.viz_scrollbar = ttk.Scrollbar(self.viz_frame, orient="vertical", command=self.viz_canvas.yview)
        self.viz_scrollable_frame = ttk.Frame(self.viz_canvas)
        
        self.viz_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.viz_canvas.configure(scrollregion=self.viz_canvas.bbox("all"))
        )
        
        self.viz_canvas.create_window((0, 0), window=self.viz_scrollable_frame, anchor="nw")
        self.viz_canvas.configure(yscrollcommand=self.viz_scrollbar.set)
        
        # Pack the canvas and scrollbar
        self.viz_canvas.pack(side="left", fill="both", expand=True)
        self.viz_scrollbar.pack(side="right", fill="y")
        
        # Create the matplotlib figure
        self.fig = Figure(figsize=(16, 20), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, self.viz_scrollable_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
        
        # Bind mousewheel to canvas for scrolling
        def _on_mousewheel(event):
            self.viz_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.viz_canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def _on_issue_selected(self, _):
        issue = self.issue_var.get()
        cfg = self.issue_configs.get(issue, {})
        subs = cfg.get('subreddits', [])
        kws = cfg.get('keywords', [])
        self.subreddit_text.delete(1.0, tk.END)
        self.subreddit_text.insert(1.0, f"Subreddits ({len(subs)}):\n")
        self.subreddit_text.insert(tk.END, ", ".join(subs))
        self.subreddit_text.insert(tk.END, f"\n\nKeywords ({len(kws)}):\n")
        self.subreddit_text.insert(tk.END, ", ".join(kws))
        self.status_label.config(text=f"Selected: {issue} - Ready to collect data")

    def _collect_data(self):
        issue = self.issue_var.get()
        if not issue:
            messagebox.showwarning("Missing", "Please select an issue.")
            return
        cfg = self.issue_configs[issue]
        # Step 1: curation - probe and select 10 subs, 20 keywords
        curated_subs, curated_kws, _ = curate_sources(
            self.reddit,
            cfg['subreddits'],
            cfg['keywords'],
            target_sub_count=10,
            target_kw_count=20,
            time_filter=self.time_var.get(),
            probe_limit=15,
        )
        # Update UI to show curated choices
        self.subreddit_text.delete(1.0, tk.END)
        self.subreddit_text.insert(1.0, f"Curated Subreddits ({len(curated_subs)}):\n")
        self.subreddit_text.insert(tk.END, ", ".join(curated_subs))
        self.subreddit_text.insert(tk.END, f"\n\nCurated Keywords ({len(curated_kws)}):\n")
        self.subreddit_text.insert(tk.END, ", ".join(curated_kws))

        subreddits = curated_subs
        keywords = curated_kws
        posts_per_sub = self.posts_var.get()
        time_filter = self.time_var.get()
        strategy = self.strategy_var.get()

        self.status_label.config(text="Collecting data...")
        self.root.update_idletasks()

        df = collect(self.reddit, subreddits, keywords, posts_per_sub, time_filter, strategy)
        if df.empty:
            messagebox.showerror("No Data", "No posts collected. Try adjusting the settings.")
            return

        # Respect timeframe in cleaning
        max_age_days = {
            'hour': 1,
            'day': 1,
            'week': 7,
            'month': 30,
            'year': 365,
            'all': None,
        }.get(time_filter, 30)
        df = clean(df, max_age_days=max_age_days)
        self.df = df
        # Remember timeframe for analysis/visualization
        self.current_time_filter = time_filter
        # NLP: compute keyword-based sentiment analysis
        focus_terms = expand_keywords_with_variants(keywords)
        df['sentiment_polarity'] = (df['title'].fillna('') + ' ' + df['selftext'].fillna('')).apply(compute_post_sentiment)
        df['important_terms'] = (df['title'].fillna('') + ' ' + df['selftext'].fillna('')).apply(lambda t: extract_important_terms(t, focus_terms))
        
        # Compute topic-specific keyword sentiment scores for visualization
        self.keyword_sentiments = aggregate_topic_keyword_sentiments(df, topic='housing_crisis')

        self._render_data_summary()
        self.status_label.config(text=f"Data collected: {len(self.df)} posts from {len(subreddits)} subreddits")
        self.analyze_btn.config(state='normal')
        # Auto-analyze
        self._analyze()

    def _render_data_summary(self):
        if self.df.empty:
            return
        self.summary_text.delete(1.0, tk.END)
        summary = []
        summary.append("DATA COLLECTION SUMMARY")
        summary.append("=" * 50)
        summary.append("")
        summary.append(f"Total Posts Collected: {len(self.df):,}")
        summary.append(f"Unique Subreddits: {self.df['subreddit'].nunique()}")
        summary.append(
            f"Date Range: {self.df['created_utc'].min().strftime('%Y-%m-%d')} to {self.df['created_utc'].max().strftime('%Y-%m-%d')}"
        )
        summary.append("")
        summary.append("SUBREDDIT BREAKDOWN:")
        for sub, count in self.df['subreddit'].value_counts().head(10).items():
            summary.append(f"r/{sub}: {count} posts")
        self.summary_text.insert(1.0, "\n".join(summary))

    def _analyze(self):
        if self.df.empty:
            messagebox.showwarning("No Data", "Please collect data first.")
            return
        results = []
        results.append("ANALYSIS RESULTS")
        results.append("=" * 50)
        results.append("")
        results.append(f"Total Posts: {len(self.df):,}")
        results.append(
            f"Date Range: {(self.df['created_utc'].max() - self.df['created_utc'].min()).days} days"
        )
        results.append(f"Average Score: {self.df['score'].mean():.1f} ± {self.df['score'].std():.1f}")
        results.append(f"Average Comments: {self.df['num_comments'].mean():.1f} ± {self.df['num_comments'].std():.1f}")
        results.append(f"Average Velocity: {self.df['velocity'].mean():.2f} points/hour")
        results.append("")

        # Topic-specific keyword sentiment analysis
        top_keywords = get_top_topic_keywords_by_frequency(self.df, topic='housing_crisis', top_n=20)
        results.append("Top Housing Crisis Keywords with Z-Score Normalized Sentiment:")
        results.append("(Negative scores = negative sentiment, Positive scores = positive sentiment)")
        results.append("")
        for i, (keyword, frequency, normalized_sentiment) in enumerate(top_keywords, 1):
            sentiment_label = "Negative" if normalized_sentiment < 0 else "Positive" if normalized_sentiment > 0 else "Neutral"
            results.append(f"{i:2d}. {keyword}: {frequency} occurrences, {normalized_sentiment:.3f} normalized sentiment ({sentiment_label})")

        self.analysis_text.delete(1.0, tk.END)
        self.analysis_text.insert(1.0, "\n".join(results))

        # Build keyword-based sentiment dashboard
        build_dashboard(self.fig, self.df, keyword_sentiments=getattr(self, 'keyword_sentiments', {}), time_filter=getattr(self, 'current_time_filter', 'month'))
        self.canvas.draw_idle()



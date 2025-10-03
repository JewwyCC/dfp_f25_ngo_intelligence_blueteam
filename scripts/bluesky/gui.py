#!/usr/bin/env python3
"""
Bluesky Social Justice Data Collector - GUI Application
DFP F25 Social Media Blue Team
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import webbrowser
import subprocess
from pathlib import Path
import sys
import os
import pandas as pd
import json
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from main import SocialJusticeCollector, CaffeineManager
from homelessness_keywords import get_all_keywords
from gui_viz import create_narrative_visualizations


class BlueSkyCollectorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Bluesky Social Justice Data Collector")
        self.root.geometry("1200x800")

        self.collector = None
        self.collection_thread = None
        self.is_collecting = False
        self.caffeine_manager = CaffeineManager()

        self._build_gui()

    def _build_gui(self):
        """Build the main GUI interface"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Control Panel Tab
        control_frame = ttk.Frame(self.notebook)
        self.notebook.add(control_frame, text="Control Panel")

        # Title
        ttk.Label(control_frame, text="Bluesky Data Collection",
                 font=('Arial', 14, 'bold')).pack(pady=10)

        # Collection Method
        method_frame = ttk.LabelFrame(control_frame, text="Collection Method", padding=10)
        method_frame.pack(pady=10, padx=20, fill='x')

        self.method_var = tk.StringVar(value='search')
        ttk.Radiobutton(method_frame, text="Search (keyword-based)",
                       variable=self.method_var, value='search').pack(anchor='w')
        ttk.Radiobutton(method_frame, text="Firehose (real-time stream)",
                       variable=self.method_var, value='firehose').pack(anchor='w')
        ttk.Radiobutton(method_frame, text="Both (comprehensive)",
                       variable=self.method_var, value='both').pack(anchor='w')

        # Keywords
        keyword_frame = ttk.LabelFrame(control_frame, text="Keywords", padding=10)
        keyword_frame.pack(pady=10, padx=20, fill='x')

        self.keyword_var = tk.StringVar(value='homelessness')
        ttk.Radiobutton(keyword_frame, text="Homelessness (top 20 keywords)",
                       variable=self.keyword_var, value='homelessness').pack(anchor='w')
        ttk.Radiobutton(keyword_frame, text="All keywords (comprehensive)",
                       variable=self.keyword_var, value='all').pack(anchor='w')
        ttk.Radiobutton(keyword_frame, text="Custom (from keywords.txt)",
                       variable=self.keyword_var, value='custom').pack(anchor='w')

        # Duration
        duration_frame = ttk.LabelFrame(control_frame, text="Collection Duration", padding=10)
        duration_frame.pack(pady=10, padx=20, fill='x')

        ttk.Label(duration_frame, text="Duration (seconds):").pack(side='left', padx=5)
        self.duration_var = tk.IntVar(value=60)
        duration_spinbox = ttk.Spinbox(duration_frame, from_=10, to=3600, increment=10,
                                       textvariable=self.duration_var, width=10)
        duration_spinbox.pack(side='left', padx=5)

        self.duration_label = ttk.Label(duration_frame, text="(1.0 minutes)")
        self.duration_label.pack(side='left', padx=5)
        self.duration_var.trace('w', self._update_duration_label)

        # Sleep Prevention
        sleep_frame = ttk.LabelFrame(control_frame, text="System Settings", padding=10)
        sleep_frame.pack(pady=10, padx=20, fill='x')

        self.prevent_sleep_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(sleep_frame, text="Prevent system sleep during collection",
                       variable=self.prevent_sleep_var).pack(anchor='w')

        # Control Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(pady=20)

        self.start_button = ttk.Button(button_frame, text="Start Collection",
                                       command=self._start_collection)
        self.start_button.pack(side='left', padx=5)

        self.stop_button = ttk.Button(button_frame, text="Stop Collection",
                                      command=self._stop_collection, state='disabled')
        self.stop_button.pack(side='left', padx=5)

        # Progress Bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(control_frame, variable=self.progress_var,
                                           maximum=100, length=600, mode='indeterminate')
        self.progress_bar.pack(pady=10)

        self.status_label = ttk.Label(control_frame, text="Ready to collect data",
                                      foreground='blue', font=('Arial', 10))
        self.status_label.pack(pady=5)

        # Collection Log Tab
        log_frame = ttk.Frame(self.notebook)
        self.notebook.add(log_frame, text="Collection Log")

        ttk.Label(log_frame, text="Real-time Collection Log",
                 font=('Arial', 12, 'bold')).pack(pady=10)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=30, width=120,
                                                  font=('Courier', 9))
        self.log_text.pack(pady=10, padx=10, fill='both', expand=True)

        # Data Summary Tab
        summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(summary_frame, text="Data Summary")

        ttk.Label(summary_frame, text="Collection Summary",
                 font=('Arial', 12, 'bold')).pack(pady=10)

        self.summary_text = scrolledtext.ScrolledText(summary_frame, height=30, width=120)
        self.summary_text.pack(pady=10, padx=10, fill='both', expand=True)

        # Visualization Tab
        viz_frame = ttk.Frame(self.notebook)
        self.notebook.add(viz_frame, text="Visualizations")

        ttk.Label(viz_frame, text="Data Visualizations",
                 font=('Arial', 12, 'bold')).pack(pady=10)

        # Control buttons
        viz_button_frame = ttk.Frame(viz_frame)
        viz_button_frame.pack(pady=10)

        ttk.Button(viz_button_frame, text="Load & Visualize Latest Data",
                  command=self._generate_visualizations).pack(side='left', padx=5)

        # Export options
        export_frame = ttk.Frame(viz_button_frame)
        export_frame.pack(side='left', padx=5)

        ttk.Label(export_frame, text="Export:").pack(side='left', padx=2)
        self.export_data_source = tk.StringVar(value="latest")
        ttk.Radiobutton(export_frame, text="Latest", variable=self.export_data_source,
                       value="latest").pack(side='left')
        ttk.Radiobutton(export_frame, text="All-time", variable=self.export_data_source,
                       value="alltime").pack(side='left')
        ttk.Button(export_frame, text="Export HTML",
                  command=self._export_html_report).pack(side='left', padx=5)

        self.viz_status_label = ttk.Label(viz_frame, text="Click 'Load & Visualize' to see charts", foreground='blue')
        self.viz_status_label.pack(pady=5)

        # Scrollable canvas for visualizations
        self.viz_canvas = tk.Canvas(viz_frame)
        viz_scrollbar = ttk.Scrollbar(viz_frame, orient="vertical", command=self.viz_canvas.yview)
        self.viz_scrollable_frame = ttk.Frame(self.viz_canvas)

        self.viz_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.viz_canvas.configure(scrollregion=self.viz_canvas.bbox("all"))
        )

        self.viz_canvas.create_window((0, 0), window=self.viz_scrollable_frame, anchor="nw")
        self.viz_canvas.configure(yscrollcommand=viz_scrollbar.set)

        self.viz_canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        viz_scrollbar.pack(side="right", fill="y")

        # Bind mousewheel
        def _on_mousewheel(event):
            self.viz_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.viz_canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def _update_duration_label(self, *args):
        """Update duration label when spinbox changes"""
        try:
            seconds = self.duration_var.get()
            minutes = seconds / 60
            self.duration_label.config(text=f"({minutes:.1f} minutes)")
        except (ValueError, tk.TclError):
            self.duration_label.config(text="(invalid)")

    def _log(self, message: str):
        """Add message to log text widget"""
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def _start_collection(self):
        """Start data collection in a separate thread"""
        if self.is_collecting:
            messagebox.showwarning("Warning", "Collection already in progress")
            return

        # Disable start button, enable stop button
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.is_collecting = True

        # Start progress bar
        self.progress_bar.start(10)
        self.status_label.config(text="Collection in progress...", foreground='orange')

        # Clear log
        self.log_text.delete(1.0, tk.END)

        # Start collection thread
        self.collection_thread = threading.Thread(target=self._run_collection, daemon=True)
        self.collection_thread.start()

    def _run_collection(self):
        """Run collection in background thread"""
        try:
            # Get parameters
            method = self.method_var.get()
            keywords = self.keyword_var.get()
            duration = self.duration_var.get()  # Already in seconds
            prevent_sleep = self.prevent_sleep_var.get()

            self._log(f"Starting collection with:")
            self._log(f"  Method: {method}")
            self._log(f"  Keywords: {keywords}")
            self._log(f"  Duration: {duration} seconds ({duration/60:.1f} minutes)")
            self._log(f"  Prevent sleep: {prevent_sleep}")
            self._log("")

            # Create collector (disable signal handlers for GUI thread)
            self.collector = SocialJusticeCollector(
                method=method,
                duration=duration,
                keywords=keywords,
                prevent_sleep=prevent_sleep,
                setup_signals=False
            )

            # Redirect logging to GUI
            import logging

            class GUILogHandler(logging.Handler):
                def __init__(self, callback, root):
                    super().__init__()
                    self.callback = callback
                    self.root = root

                def emit(self, record):
                    msg = self.format(record)
                    self.root.after(0, lambda m=msg: self.callback(m))

            gui_handler = GUILogHandler(self._log, self.root)
            gui_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

            logger = logging.getLogger(__name__)
            logger.addHandler(gui_handler)

            # Import main logger
            from main import logger as main_logger
            main_logger.addHandler(gui_handler)

            # Run collection
            success = self.collector.run_collection()

            if success:
                self._log("")
                self._log("=" * 80)
                self._log("COLLECTION COMPLETED SUCCESSFULLY!")
                self._log("=" * 80)
                self.root.after(0, lambda: self.status_label.config(
                    text="Collection completed successfully!", foreground='green'))
                self._update_summary()
            else:
                self._log("")
                self._log("Collection failed!")
                self.root.after(0, lambda: self.status_label.config(
                    text="Collection failed", foreground='red'))

        except Exception as e:
            error_msg = str(e)
            self._log(f"Error during collection: {error_msg}")
            self.root.after(0, lambda msg=error_msg: self.status_label.config(
                text=f"Error: {msg}", foreground='red'))

        finally:
            # Stop progress bar
            self.root.after(0, self.progress_bar.stop)

            # Re-enable buttons
            self.root.after(0, lambda: self.start_button.config(state='normal'))
            self.root.after(0, lambda: self.stop_button.config(state='disabled'))
            self.is_collecting = False

    def _stop_collection(self):
        """Stop data collection"""
        if not self.is_collecting:
            return

        self._log("Stopping collection...")
        self.status_label.config(text="Stopping collection...", foreground='orange')

        # Signal collection to stop (collector should handle this gracefully)
        if self.collector and self.collector.caffeine_manager:
            self.collector.caffeine_manager.stop_caffeine()

        self.is_collecting = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress_bar.stop()
        self.status_label.config(text="Collection stopped by user", foreground='blue')

    def _update_summary(self):
        """Update summary tab with collection statistics"""
        # Check multiple possible data directories
        output_dir = None
        possible_dirs = [
            Path("../../data/bluesky/alltime_socmed"),
            Path("../../data/bluesky/alltime"),
            Path("data/bluesky/alltime_socmed"),
            Path("data/bluesky/alltime")
        ]
        for dir_path in possible_dirs:
            if dir_path.exists():
                output_dir = dir_path
                break

        if not output_dir or not output_dir.exists():
            self.summary_text.insert(tk.END, "No data collected yet\n")
            return

        # Find latest summary file
        summary_files = sorted(output_dir.glob("*_summary.json"), reverse=True)

        if not summary_files:
            self.summary_text.insert(tk.END, "No summary file found\n")
            return

        import json

        try:
            with open(summary_files[0], 'r') as f:
                summary = json.load(f)

            self.summary_text.delete(1.0, tk.END)
            self.summary_text.insert(tk.END, "COLLECTION SUMMARY\n")
            self.summary_text.insert(tk.END, "=" * 80 + "\n\n")

            # Collection stats
            self.summary_text.insert(tk.END, f"Collection Method: {summary['method']}\n")
            self.summary_text.insert(tk.END, f"Duration: {summary['duration_minutes']} minutes\n")
            self.summary_text.insert(tk.END, f"Timestamp: {summary['collection_timestamp']}\n\n")

            # Collection statistics
            stats = summary['collection_stats']
            self.summary_text.insert(tk.END, "COLLECTION STATISTICS:\n")
            self.summary_text.insert(tk.END, f"  Total posts collected: {stats['total_posts_collected']:,}\n")
            self.summary_text.insert(tk.END, f"  New unique posts: {stats['new_unique_posts']:,}\n")
            self.summary_text.insert(tk.END, f"  Duplicates removed: {stats['duplicates_removed']:,}\n")
            self.summary_text.insert(tk.END, f"  Already existing: {stats['already_existing']:,}\n")
            self.summary_text.insert(tk.END, f"  Collection rate: {stats['collection_rate_per_second']:.2f} posts/second\n\n")

            # Data statistics
            data_stats = summary['data_stats']
            self.summary_text.insert(tk.END, "DATA STATISTICS:\n")
            self.summary_text.insert(tk.END, f"  Posts before collection: {data_stats['posts_before_collection']:,}\n")
            self.summary_text.insert(tk.END, f"  Posts after collection: {data_stats['posts_after_collection']:,}\n")
            self.summary_text.insert(tk.END, f"  New posts added: {data_stats['new_posts_added']:,}\n")
            self.summary_text.insert(tk.END, f"  Posts with location: {data_stats['posts_with_location']:,} ({data_stats['location_percentage']:.1f}%)\n\n")

            # Geographic data
            if 'geographic_data' in summary and summary['geographic_data']['top_locations']:
                self.summary_text.insert(tk.END, "TOP LOCATIONS:\n")
                for location, count in summary['geographic_data']['top_locations'][:5]:
                    self.summary_text.insert(tk.END, f"  {location}: {count} posts\n")

        except Exception as e:
            self.summary_text.insert(tk.END, f"Error reading summary: {e}\n")

    def _generate_visualizations(self):
        """Generate and display visualizations in GUI"""
        self.viz_status_label.config(text="Loading data and generating visualizations...", foreground='orange')
        self.root.update_idletasks()

        try:
            # Clear existing visualizations
            for widget in self.viz_scrollable_frame.winfo_children():
                widget.destroy()

            # Check multiple possible data directories
            output_dir = None
            possible_dirs = [
                Path("../../data/bluesky/alltime_socmed"),
                Path("../../data/bluesky/alltime"),
                Path("data/bluesky/alltime_socmed"),
                Path("data/bluesky/alltime")
            ]
            for dir_path in possible_dirs:
                if dir_path.exists():
                    # Filter out broken symlinks
                    csv_files = [f for f in dir_path.glob("*.csv") if f.exists() and f.is_file()]
                    if csv_files:
                        output_dir = dir_path
                        break

            if not output_dir:
                messagebox.showerror("Error", "No data found. Please collect data first.")
                self.viz_status_label.config(text="No data available", foreground='red')
                return

            # Filter out broken symlinks before sorting
            csv_files = [f for f in output_dir.glob("*.csv") if f.exists() and f.is_file()]
            csv_files = sorted(csv_files, key=lambda p: p.stat().st_mtime, reverse=True)
            if not csv_files:
                messagebox.showerror("Error", "No CSV files found in data directory.")
                self.viz_status_label.config(text="No data files found", foreground='red')
                return

            # Load latest CSV
            df = pd.read_csv(csv_files[0], low_memory=False)
            self.viz_status_label.config(text=f"Loaded {len(df):,} posts from {csv_files[0].name} - generating narrative visualizations...", foreground='blue')
            self.root.update_idletasks()

            # Create narrative visualizations matching HTML structure
            fig = create_narrative_visualizations(df)

            # Embed figure in tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.viz_scrollable_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)

            self.viz_status_label.config(text=f"Visualizations generated successfully! ({len(df):,} posts)", foreground='green')

        except Exception as e:
            self.viz_status_label.config(text=f"Error: {str(e)}", foreground='red')
            messagebox.showerror("Error", f"Error generating visualizations:\n{str(e)}")

    def _export_html_report(self):
        """Export current visualization to HTML"""
        self.viz_status_label.config(text="Exporting HTML report...", foreground='orange')
        self.root.update_idletasks()

        try:
            data_source = self.export_data_source.get()
            output_dir = Path("../../data/bluesky")

            if data_source == "alltime":
                # Use comprehensive alltime data (dedup and union)
                alltime_file = output_dir / "alltime" / "alltime_socmed.csv"
                if not alltime_file.exists():
                    messagebox.showerror("Error", f"All-time data file not found: {alltime_file}")
                    self.viz_status_label.config(text="All-time data not found", foreground='red')
                    return
                selected_file = alltime_file
                data_desc = "All-time (comprehensive)"
            else:
                # Load latest session data - search recursively
                csv_files = [f for f in output_dir.rglob("*.csv") if f.exists() and f.is_file()]

                if not csv_files:
                    messagebox.showerror("Error", "No data files found to export")
                    self.viz_status_label.config(text="No data to export", foreground='red')
                    return

                csv_files = sorted(csv_files, key=lambda p: p.stat().st_mtime, reverse=True)
                selected_file = csv_files[0]
                data_desc = "Latest session"

            df = pd.read_csv(selected_file)

            if df.empty:
                messagebox.showerror("Error", "Data file is empty")
                self.viz_status_label.config(text="Empty data file", foreground='red')
                return

            # Create visualization
            from gui_viz import create_narrative_visualizations
            fig = create_narrative_visualizations(df)

            # Export to HTML
            from matplotlib.backends.backend_agg import FigureCanvasAgg
            import io
            import base64

            # Save figure to base64
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            buf.close()

            # Create HTML
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Bluesky Data Visualization</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Georgia, serif;
            margin: 0;
            padding: 20px;
            background: white;
        }}
        .container {{
            max-width: 1600px;
            margin: 0 auto;
        }}
        h1 {{
            font-size: 28px;
            font-weight: normal;
            color: #121212;
            margin-bottom: 10px;
        }}
        .metadata {{
            color: #666666;
            font-size: 14px;
            margin-bottom: 30px;
        }}
        img {{
            width: 100%;
            height: auto;
            display: block;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Bluesky Social Media Analysis</h1>
        <div class="metadata">
            Data source: {data_desc}<br>
            File: {selected_file.name}<br>
            Total posts: {len(df):,}<br>
            Export date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
        <img src="data:image/png;base64,{img_base64}" alt="Visualization">
    </div>
</body>
</html>"""

            # Save to viz/bluesky/bluesky_py_export.html
            output_path = Path("../../viz/bluesky/bluesky_py_export.html")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(html_content)

            # Open in browser
            webbrowser.open(f'file://{output_path.absolute()}')

            self.viz_status_label.config(text=f"Exported to {output_path.name}", foreground='green')
            messagebox.showinfo("Success", f"HTML report exported:\n{output_path.absolute()}")

        except Exception as e:
            self.viz_status_label.config(text=f"Error: {str(e)}", foreground='red')
            messagebox.showerror("Error", f"Error exporting report:\n{str(e)}")


def main():
    """Launch GUI application"""
    root = tk.Tk()
    app = BlueSkyCollectorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

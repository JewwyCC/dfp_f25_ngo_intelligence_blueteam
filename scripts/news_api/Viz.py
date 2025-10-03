import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
import numpy as np
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')


class Visualizations:
    def __init__(self, df, keyword):
        """
        Initialize with classified articles DataFrame.
        """
        self.df = df.copy()
        self.keyword = keyword

        # Prepare temporal data
        self.df['date'] = pd.to_datetime(self.df['published_at']).dt.date

        # Color scheme
        self.color_map = {
            'LEFT': '#0015BC',
            'CENTER': '#808080',
            'RIGHT': '#FF0000'
        }
        self.political_order = ['LEFT', 'CENTER', 'RIGHT']

        # Get actual labels present in data
        self.actual_labels = df['political_label'].unique()
        print(f"Political labels found in data: {list(self.actual_labels)}")

    def create_daily_line_plot(self, df):
        """
        Fixed line plot with proper color handling using updated matplotlib API.
        """
        fig, ax = plt.subplots(figsize=(14, 6))

        # Prepare data
        df['date'] = pd.to_datetime(df['published_at']).dt.date
        daily_counts = df.groupby(['date', 'political_label']).size().unstack(fill_value=0)

        # Define color mappings
        predefined_colors = {
            # Standard political labels
            'LEFT': '#013364',
            'CENTER': '#cbcaca',
            'RIGHT': '#d30b0d',
        }

        # Get all unique labels in your data
        all_labels = list(daily_counts.columns)

        # Assign colors to each label
        label_colors = {}
        color_index = 0

        for label in all_labels:
            label = label.upper()
            if label in predefined_colors:
                # Use predefined color
                label_colors[label] = predefined_colors[label]

        # Plot each political leaning with its assigned color
        for label in all_labels:
            ax.plot(daily_counts.index, daily_counts[label],
                    label=label,
                    color=label_colors[label],
                    marker='o', markersize=4,
                    linewidth=2, alpha=0.8)

        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Articles', fontsize=12, fontweight='bold')
        ax.set_title(f'Daily Political Coverage Trends: Homelessness', fontsize=14, fontweight='bold')
        ax.legend(title='Political Leaning', bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()

    # # Alternative: Using matplotlib's built-in color lists
    # def create_daily_line_plot_simple(df, keyword):
    #     """
    #     Simpler version using matplotlib's built-in color lists.
    #     """
    #     fig, ax = plt.subplots(figsize=(14, 6))
	#
    #     # Prepare data
    #     df['date'] = pd.to_datetime(df['published_at']).dt.date
    #     daily_counts = df.groupby(['date', 'political_label']).size().unstack(fill_value=0)
	#
    #     # Simple color assignment using matplotlib's color names
    #     # Full list of colors available
    #     simple_colors = [
    #         'blue', 'red', 'green', 'orange', 'purple',
    #         'brown', 'pink', 'gray', 'olive', 'cyan',
    #         'navy', 'teal', 'lime', 'indigo', 'coral'
    #     ]
	#
    #     # Or use hex colors directly
    #     hex_colors = [
    #         '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
    #         '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
    #     ]
	#
    #     # Map labels to colors based on keywords
    #     label_colors = {}
    #     color_idx = 0
	#
    #     for label in daily_counts.columns:
    #         label_lower = label.lower()
	#
    #         # Assign colors based on political leaning
    #         if 'left' in label_lower:
    #             label_colors[label] = '#0015BC'  # Blue for left
    #         elif 'right' in label_lower:
    #             label_colors[label] = '#FF0000'  # Red for right
    #         elif any(word in label_lower for word in ['center', 'neutral', 'balanced']):
    #             label_colors[label] = '#808080'  # Gray for center
    #         else:
    #             # Use color from list
    #             label_colors[label] = hex_colors[color_idx % len(hex_colors)]
    #             color_idx += 1
	#
    #     # Plot lines
    #     for label in daily_counts.columns:
    #         ax.plot(daily_counts.index, daily_counts[label],
    #                 label=label,
    #                 color=label_colors[label],
    #                 marker='o', markersize=4,
    #                 linewidth=2, alpha=0.8)
	#
    #     ax.set_xlabel('Date', fontsize=12, fontweight='bold')
    #     ax.set_ylabel('Number of Articles', fontsize=12, fontweight='bold')
    #     ax.set_title(f'Daily Political Coverage Trends: "{keyword}"', fontsize=14, fontweight='bold')
    #     ax.legend(title='Political Leaning', bbox_to_anchor=(1.05, 1), loc='upper left')
    #     ax.grid(True, alpha=0.3)
	#
    #     plt.xticks(rotation=45, ha='right')
    #     plt.tight_layout()
    #     plt.show()
	#
    # # Alternative: Complete class with flexible color handling
    # class FlexibleTimelineVisualizations:
    #     def __init__(self, df, keyword):
    #         self.df = df.copy()
    #         self.keyword = keyword
    #         self.df['date'] = pd.to_datetime(self.df['published_at']).dt.date
	#
    #         # Get unique labels and assign colors
    #         self.unique_labels = df['political_label'].unique()
    #         self.color_map = self._create_color_map()
	#
    #     def _create_color_map(self):
    #         """
    #         Create a color map for all labels in the data.
    #         """
    #         # Start with predefined colors for common labels
    #         predefined = {
    #             'Left': '#0015BC',
    #             'Left-leaning': '#0015BC',
    #             'Center-Left': '#6495ED',
    #             'Center': '#808080',
    #             'Neutral': '#808080',
    #             'Balanced': '#808080',
    #             'Center-Right': '#FFA500',
    #             'Right': '#FF0000',
    #             'Right-leaning': '#FF0000',
    #             'Negative': '#FF6B6B',
    #             'Positive': '#4ECDC4',
    #         }
	#
    #         # Use tab20 colormap for more color options
    #         cmap = plt.cm.get_cmap('tab20')
	#
    #         color_map = {}
    #         color_idx = 0
	#
    #         for label in self.unique_labels:
    #             # Check for predefined color (case-insensitive)
    #             found = False
    #             for key, color in predefined.items():
    #                 if label.lower() == key.lower():
    #                     color_map[label] = color
    #                     found = True
    #                     break
	#
    #             if not found:
    #                 # Assign from colormap
    #                 color_map[label] = cmap(color_idx % 20)

    def create_normalized_daily_bars(self):
        """
        100% stacked bar chart showing daily proportion changes.
        """
        fig, ax = plt.subplots(figsize=(14, 6))

        # Aggregate by date and political label
        daily_counts = self.df.groupby(['date', 'political_label']).size().unstack(fill_value=0)

        # Normalize to percentages
        daily_pct = daily_counts.div(daily_counts.sum(axis=1), axis=0) * 100

        # Track labels that were actually plotted
        plotted_labels = []

        # Create stacked bar chart
        bottom = np.zeros(len(daily_pct))

        # First plot standard political labels
        for label in self.political_order:
            if label in daily_pct.columns:
                ax.bar(range(len(daily_pct)), daily_pct[label],
                       bottom=bottom, label=label,
                       color=self.color_map.get(label, 'gray'), width=1)
                bottom += daily_pct[label].values
                plotted_labels.append(label)

        # Then plot any additional labels not in standard order
        for label in daily_pct.columns:
            if label not in self.political_order:
                ax.bar(range(len(daily_pct)), daily_pct[label],
                       bottom=bottom, label=label,
                       color='gray', width=1, alpha=0.7)
                bottom += daily_pct[label].values
                plotted_labels.append(label)

        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_ylabel('Percentage of Articles (%)', fontsize=12, fontweight='bold')
        ax.set_title(f'Daily Political Balance: "{self.keyword}"', fontsize=14, fontweight='bold')

        # Only add legend if labels were plotted
        if plotted_labels:
            ax.legend(title='Political Leaning', bbox_to_anchor=(1.05, 1), loc='upper left')

        # Set x-axis labels
        n_ticks = min(10, len(daily_pct))
        tick_positions = np.linspace(0, len(daily_pct) - 1, n_ticks, dtype=int)
        ax.set_xticks(tick_positions)
        ax.set_xticklabels([str(daily_pct.index[i]) for i in tick_positions],
                           rotation=45, ha='right')

        plt.tight_layout()
        plt.show()

    def create_rolling_average_plot(self, window=7):
        """
        Rolling average to show smoothed trends.
        """
        fig, ax = plt.subplots(figsize=(14, 6))

        # Aggregate by date and political label
        daily_counts = self.df.groupby(['date', 'political_label']).size().unstack(fill_value=0)

        # Track what we've plotted
        plotted_any = False

        # Plot each political leaning
        for label in daily_counts.columns:
            color = self.color_map.get(label, 'gray')

            # Calculate rolling average
            rolling_avg = daily_counts[label].rolling(window=window, min_periods=1).mean()

            # Plot the rolling average as a thick line
            line = ax.plot(daily_counts.index, rolling_avg,
                           label=f'{label} ({window}-day avg)',
                           color=color, linewidth=2.5, alpha=0.9)

            # Add the actual daily data as scatter
            scatter = ax.scatter(daily_counts.index, daily_counts[label],
                                 color=color, alpha=0.3, s=20)

            if line:
                plotted_any = True

        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Articles', fontsize=12, fontweight='bold')
        ax.set_title(f'{window}-Day Rolling Average of Political Coverage: "{self.keyword}"',
                     fontsize=14, fontweight='bold')

        # Only add legend if something was plotted
        if plotted_any:
            # Get current handles and labels
            handles, labels = ax.get_legend_handles_labels()
            if handles:  # Only create legend if there are handles
                ax.legend(title='Political Leaning', bbox_to_anchor=(1.05, 1), loc='upper left')

        ax.grid(True, alpha=0.3)

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()

    def create_small_multiples(self):
        """
        Small multiples showing each political leaning separately.
        """
        # Get labels that actually exist in the data
        existing_labels = [l for l in self.political_order if l in self.df['political_label'].values]

        # Add any additional labels not in standard order
        for label in self.df['political_label'].unique():
            if label not in existing_labels:
                existing_labels.append(label)

        if not existing_labels:
            print("No political labels found in data!")
            return

        # Create subplots
        n_plots = len(existing_labels)
        fig, axes = plt.subplots(n_plots, 1, figsize=(14, 2.5 * n_plots),
                                 sharex=True, sharey=True)

        # Handle single subplot case
        if n_plots == 1:
            axes = [axes]

        # Plot each political leaning
        for i, label in enumerate(existing_labels):
            subset = self.df[self.df['political_label'] == label]
            daily_counts = subset.groupby('date').size()

            # Create a complete date range
            date_range = pd.date_range(start=self.df['date'].min(),
                                       end=self.df['date'].max(), freq='D')
            daily_counts = daily_counts.reindex(date_range.date, fill_value=0)

            # Get color
            color = self.color_map.get(label, 'gray')

            # Plot
            axes[i].fill_between(daily_counts.index, daily_counts.values,
                                 alpha=0.6, color=color)
            axes[i].plot(daily_counts.index, daily_counts.values,
                         color=color, linewidth=2)

            axes[i].set_ylabel(label, fontsize=10, fontweight='bold')
            axes[i].grid(True, alpha=0.3)

            # Add average line
            if len(daily_counts) > 0:
                avg = daily_counts.mean()
                axes[i].axhline(y=avg, color='gray', linestyle='--', alpha=0.5)
                axes[i].text(daily_counts.index[-1], avg, f'avg: {avg:.1f}',
                             va='bottom', ha='right', fontsize=8)

        axes[-1].set_xlabel('Date', fontsize=12, fontweight='bold')
        fig.suptitle(f'Political Coverage by Leaning: "{self.keyword}"',
                     fontsize=14, fontweight='bold', y=1.02)

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()

    def create_balance_indicator(self):
        """
        Balance indicator showing left/right balance over time.
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), height_ratios=[3, 1])

        # Define which labels are left/right/center
        left_labels = ['Left', 'Center-Left', 'Left-leaning']
        right_labels = ['Right', 'Center-Right', 'Right-leaning']
        center_labels = ['Center', 'Neutral', 'Balanced']

        # Calculate daily balance
        daily_balance = []

        for date in sorted(self.df['date'].unique()):
            day_df = self.df[self.df['date'] == date]

            # Count articles by political direction
            left = len(day_df[day_df['political_label'].isin(left_labels)])
            right = len(day_df[day_df['political_label'].isin(right_labels)])
            center = len(day_df[day_df['political_label'].isin(center_labels)])

            # Count any other labels as center
            other = len(day_df[~day_df['political_label'].isin(left_labels + right_labels + center_labels)])
            center += other

            # Calculate balance score
            total = left + right + center
            if total > 0:
                balance_score = (right - left) / total
            else:
                balance_score = 0

            daily_balance.append({
                'date': date,
                'balance': balance_score,
                'left': left,
                'right': right,
                'center': center,
                'total': total
            })

        if not daily_balance:
            print("No data to create balance indicator!")
            return

        balance_df = pd.DataFrame(daily_balance)

        # Plot 1: Balance score over time
        ax1.plot(balance_df['date'], balance_df['balance'],
                 color='black', linewidth=2, marker='o', markersize=4)

        # Only add fill if we have data
        if len(balance_df) > 0:
            ax1.fill_between(balance_df['date'], 0, balance_df['balance'],
                             where=(balance_df['balance'] > 0),
                             color='red', alpha=0.3, label='Right-leaning')
            ax1.fill_between(balance_df['date'], 0, balance_df['balance'],
                             where=(balance_df['balance'] < 0),
                             color='blue', alpha=0.3, label='Left-leaning')

        ax1.axhline(y=0, color='gray', linestyle='-', linewidth=1)
        ax1.set_ylabel('Political Balance\n← Left | Right →', fontsize=11, fontweight='bold')
        ax1.set_title(f'Daily Political Balance Indicator: "{self.keyword}"',
                      fontsize=14, fontweight='bold')

        # Check if legend items exist before adding legend
        handles, labels = ax1.get_legend_handles_labels()
        if handles:
            ax1.legend(loc='upper right')

        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(-1, 1)

        # Plot 2: Article volume
        ax2.bar(balance_df['date'], balance_df['total'],
                color='gray', alpha=0.5, width=0.8)
        ax2.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Total\nArticles', fontsize=10)
        ax2.grid(True, alpha=0.3, axis='y')

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()

        # Print balance statistics
        if len(balance_df) > 0:
            avg_balance = balance_df['balance'].mean()
            print(f"\nBalance Statistics:")
            print(f"Average balance: {avg_balance:.3f}")
            print(f"Days with left bias: {len(balance_df[balance_df['balance'] < -0.1])}")
            print(f"Days with right bias: {len(balance_df[balance_df['balance'] > 0.1])}")
            print(f"Balanced days: {len(balance_df[abs(balance_df['balance']) <= 0.1])}")

            if avg_balance < -0.1:
                print("Overall: LEFT-LEANING coverage")
            elif avg_balance > 0.1:
                print("Overall: RIGHT-LEANING coverage")
            else:
                print("Overall: BALANCED coverage")


# Safe wrapper function that checks data before visualizing
def safe_visualize_temporal_patterns(df, keyword):
    """
    Safely create temporal visualizations with data validation.
    """
    # Check if DataFrame has required columns
    required_cols = ['political_label', 'published_at']
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        print(f"Error: Missing required columns: {missing_cols}")
        print(f"Available columns: {list(df.columns)}")
        return

    # Check if DataFrame has data
    if df.empty:
        print("Error: DataFrame is empty!")
        return

    # Create visualizations
    viz = Visualizations(df, keyword)

    # Create each visualization with error handling
    visualizations = [
        ("Daily Trends", viz.create_daily_line_plot(df)),
        # ("Daily Balance", viz.create_normalized_daily_bars),
        # ("Rolling Average", lambda: viz.create_rolling_average_plot(window=7)),
        # ("Small Multiples", viz.create_small_multiples),
        # ("Balance Indicator", viz.create_balance_indicator)
    ]
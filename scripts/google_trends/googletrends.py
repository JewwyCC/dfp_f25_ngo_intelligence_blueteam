#!/usr/bin/env python3
"""
Google Trends Analysis Script

This script analyzes Google Trends data for homelessness-related keywords across different themes 
and geographic regions (national vs state-level). It includes comprehensive data visualization 
and status tracking functionality.

Author: Generated from Jupyter notebook
Date: October 2, 2025
"""

# Standard library imports
import csv
import os
import time
import math
import glob
import pickle
import json
from datetime import datetime, timedelta

# Third-party imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import folium
import geopandas as gpd
import us
from statsmodels.tsa.seasonal import seasonal_decompose

# Google Trends specific imports
from pytrends.request import TrendReq
from pytrends.exceptions import TooManyRequestsError

# Configuration
PYTRENDS_CONFIG = {
    'hl': 'en-US',
    'tz': 360
}

# File paths (relative to script directory)
DATA_FILES = {
    'keyword_theme': 'data python files/keyword_theme.xlsx',
    'help_keywords': 'data python files/help keywords.xlsx',
    'uszips': 'data python files/uszips.csv',
    'shapefile': 'data python files/ne_110m_admin_1_states_provinces/ne_110m_admin_1_states_provinces.shp'
}

# US States list
US_STATES = [
    'AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME',
    'MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA',
    'RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY'
]

class GoogleTrendsAnalyzer:
    """Main class for Google Trends analysis"""
    
    def __init__(self):
        """Initialize the analyzer"""
        self.pytrends = TrendReq(**PYTRENDS_CONFIG)
        self.base_keyword = "what is homelessness"
        
        # Initialize data visualization status tracking
        self.viz_status = {
            'historical_timeline_national': False,
            'historical_timeline_state': False,
            'theme_comparison_chart': False,
            'seasonality_national': False,
            'seasonality_state': False,
            'choropleth_maps': False,
            'data_source_overall': False
        }
        
        # Data storage
        self.theme_kw_map = None
        self.help_theme_kw_map = None
        self.zip_to_state = {}
        self.national_norm = None
        self.state_norm = None
        self.results = {}
        
    def update_viz_status(self, viz_name):
        """Update visualization status and check if all are complete"""
        self.viz_status[viz_name] = True
        print(f"✓ {viz_name} completed")
        
        # Check if all visualizations are complete (excluding overall status)
        viz_keys = [k for k in self.viz_status.keys() if k != 'data_source_overall']
        all_complete = all(self.viz_status[k] for k in viz_keys)
        
        if all_complete:
            self.viz_status['data_source_overall'] = True
            print("🎉 All visualizations completed! Data source is ready.")
        
        return self.viz_status

    def get_loading_status(self):
        """Return current loading status for frontend"""
        viz_keys = [k for k in self.viz_status.keys() if k != 'data_source_overall']
        completed = sum(self.viz_status[k] for k in viz_keys)
        total = len(viz_keys)
        percentage = (completed / total) * 100
        
        return {
            'status': self.viz_status.copy(),
            'progress': {
                'completed': completed,
                'total': total,
                'percentage': percentage
            },
            'overall_ready': self.viz_status['data_source_overall']
        }

    def build_zip_state_map(self, filename):
        """Build mapping from ZIP codes to states"""
        zip_to_state = {}
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                zip_to_state[row['zip']] = row['state_id']
        return zip_to_state

    def get_state(self, zipcode):
        """Get state abbreviation from ZIP code"""
        return self.zip_to_state.get(str(zipcode), 'Unknown')

    def batch_extract(self, theme_kw_map, base_keyword, geo, years=5, batch_size=5, delay=60, max_retries=5):
        """Extract data in batches with retry logic"""
        all_keywords = theme_kw_map['Keyword'].unique().tolist()
        # Remove duplicates, always include base keyword at front
        all_keywords = [base_keyword] + [kw for kw in all_keywords if kw != base_keyword]
        batches = [all_keywords[i:i+batch_size-1] for i in range(0, len(all_keywords), batch_size-1)]
        batches = [[base_keyword] + batch for batch in batches]

        batch_dfs = []
        for batch in batches:
            batch = list(dict.fromkeys(batch))  # remove duplicates within batch
            print(f"Processing batch ({geo}): {batch}")
            for attempt in range(max_retries):
                try:
                    self.pytrends.build_payload(batch, geo=geo, timeframe=f'today {years}-y')
                    batch_data = self.pytrends.interest_over_time()
                    batch_dfs.append(batch_data)
                    break  # Success, break out of retry loop
                except TooManyRequestsError:
                    wait = delay * (attempt + 1)  # exponential backoff
                    print(f"Rate limit hit. Waiting {wait} seconds before retrying...")
                    time.sleep(wait)
            else:
                print(f"Failed to fetch batch after {max_retries} attempts: {batch}")
            time.sleep(delay)  # Always wait between batches

        return batch_dfs

    def normalize_batches(self, batch_dfs, base_keyword):
        """Normalize batches using base keyword"""
        if not batch_dfs:
            return pd.DataFrame()
            
        # Use the max of base_keyword from the first batch as reference
        base_max = batch_dfs[0][base_keyword].max()
        normalized_dfs = []
        for batch_df in batch_dfs:
            theme_max = batch_df[base_keyword].max()
            scaling_factor = base_max / theme_max if theme_max else 1
            norm_df = batch_df * scaling_factor
            normalized_dfs.append(norm_df)
        # Concatenate and average duplicate columns (from overlapping batches)
        all_df = pd.concat(normalized_dfs, axis=1)
        # Remove duplicate columns from overlapping batches
        all_df = all_df.loc[:,~all_df.columns.duplicated()]
        return all_df

    def extract_related_queries(self):
        """Extract top 5 related queries for homelessness"""
        try:
            self.pytrends.build_payload(['homelessness'], timeframe='today 5-y', geo='US')
            related = self.pytrends.related_queries()
            homeless_top = related['homelessness']['top'] if related['homelessness']['top'] is not None else pd.DataFrame()

            if not homeless_top.empty:
                top_queries = homeless_top['query'].tolist()[:5]
                print("Homelessness related queries:", top_queries)
                df = pd.DataFrame(top_queries, columns=["Query"])
                current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
                df.to_excel(f"googletrends_keywords_{current_datetime}.xlsx", index=False)
                return top_queries
            else:
                print("No related queries found for 'homelessness'.")
                return []
        except Exception as e:
            print(f"Error extracting related queries: {e}")
            return []

    def load_data_files(self):
        """Load all required data files"""
        try:
            # Load theme-keyword mapping
            self.theme_kw_map = pd.read_excel(DATA_FILES['keyword_theme'])
            print("✓ Theme-keyword mapping loaded")
            
            # Load help keywords
            self.help_theme_kw_map = pd.read_excel(DATA_FILES['help_keywords'])
            print("✓ Help keywords loaded")
            
            # Build ZIP to state mapping
            self.zip_to_state = self.build_zip_state_map(DATA_FILES['uszips'])
            print("✓ ZIP to state mapping loaded")
            
        except Exception as e:
            print(f"Error loading data files: {e}")
            raise

    def extract_historical_data(self, zipcode='90001'):
        """Extract historical search volume data"""
        state_abbr = self.get_state(zipcode)
        if state_abbr == 'Unknown':
            raise ValueError("State not found for this zipcode.")

        base_national_keyword = self.base_keyword
        base_state_keyword = self.base_keyword

        # Extract National Search Volume
        print("Extracting national data...")
        national_batches = self.batch_extract(self.theme_kw_map, base_national_keyword, geo='US', delay=15)
        
        # Extract State Search Volume
        print(f"Extracting state data for {state_abbr}...")
        state_batches = self.batch_extract(self.theme_kw_map, base_state_keyword, geo=f'US-{state_abbr}', delay=15)

        # Normalize data
        self.national_norm = self.normalize_batches(national_batches, base_national_keyword)
        self.state_norm = self.normalize_batches(state_batches, base_state_keyword)
        
        # Save data
        current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.national_norm.to_excel(f'googletrends_national_{current_datetime}.xlsx', index=False)
        self.state_norm.to_excel(f'googletrends_state_{current_datetime}.xlsx', index=False)
        
        print("✓ Historical data extraction completed")

    def plot_theme_trends(self, norm_df, base_keyword, title):
        """Plot theme trends over time"""
        if norm_df is None or norm_df.empty:
            print(f"No data available for {title}")
            return
            
        # Group by theme using input Excel
        keyword_to_theme = self.theme_kw_map.set_index('Keyword')['Theme'].to_dict()
        trend_by_theme = {}
        for keyword in norm_df.columns:
            if keyword == base_keyword: continue
            theme = keyword_to_theme.get(keyword, 'Unknown')
            if theme not in trend_by_theme:
                trend_by_theme[theme] = []
            trend_by_theme[theme].append(norm_df[keyword])
        
        plt.figure(figsize=(14,8))
        for theme, series_list in trend_by_theme.items():
            # Average across all keywords in theme
            theme_series = pd.concat(series_list, axis=1).mean(axis=1)
            smoothed = theme_series.rolling(window=4, center=True).mean()  # monthly smoothing
            plt.plot(smoothed, label=theme)
        plt.title(title)
        plt.ylabel('Normalized Search Interest')
        plt.legend()
        plt.tight_layout()
        plt.show()

    def compute_theme_scores(self, norm_df, theme_kw_map, base_keyword=None):
        """Compute theme scores for the last year"""
        if norm_df is None or norm_df.empty:
            return {}
            
        # Restrict to last year
        last_date = norm_df.index.max()
        one_year_ago = last_date - timedelta(days=365)
        norm_df_last_year = norm_df.loc[norm_df.index >= one_year_ago]

        theme_scores = {}
        for theme in theme_kw_map['Theme'].unique():
            theme_keywords = theme_kw_map[theme_kw_map['Theme'] == theme]['Keyword'].tolist()
            if base_keyword and base_keyword in theme_keywords:
                theme_keywords.remove(base_keyword)
            theme_keywords = [kw for kw in theme_keywords if kw in norm_df_last_year.columns]
            total_vols = {kw: norm_df_last_year[kw].sum() for kw in theme_keywords}
            top5 = sorted(theme_keywords, key=lambda x: total_vols.get(x, 0), reverse=True)[:5]
            # For each keyword: if median==0, use max; else use median
            values = []
            for kw in top5:
                median = norm_df_last_year[kw].median()
                if median == 0:
                    val = norm_df_last_year[kw].max()
                else:
                    val = median
                values.append(val)
            theme_scores[theme] = sum(values)
        return theme_scores

    def normalize_theme_scores(self, theme_scores):
        """Normalize theme scores to percentages"""
        total = sum(theme_scores.values())
        if total == 0:
            # Avoid division by zero
            return {k: 0 for k in theme_scores}
        return {k: (v / total) * 100 for k, v in theme_scores.items()}

    def plot_grouped_horizontal_bar(self, theme_scores_a, theme_scores_b, group_a_label, group_b_label):
        """Plot grouped horizontal bar chart"""
        themes = list(theme_scores_a.keys())
        scores_a = [theme_scores_a[theme] for theme in themes]
        scores_b = [theme_scores_b.get(theme, 0) for theme in themes]
        y = np.arange(len(themes))
        height = 0.35

        fig, ax = plt.subplots(figsize=(10, 6))
        bars_a = ax.barh(y - height/2, scores_a, height, label=group_a_label, color="#5B9BD5")
        bars_b = ax.barh(y + height/2, scores_b, height, label=group_b_label, color="#ED7D31")

        # Labels
        ax.set_yticks(y)
        ax.set_yticklabels(themes)
        ax.invert_yaxis()
        ax.set_xlabel("Percentage (%)")
        ax.set_title(f"{group_a_label} vs {group_b_label} Theme Scores (Normalized to 100)")
        ax.legend()

        # Value labels on bars
        for bar in bars_a:
            ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, f'{bar.get_width():.1f}%', va='center', color=bar.get_facecolor())
        for bar in bars_b:
            ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, f'{bar.get_width():.1f}%', va='center', color=bar.get_facecolor())

        plt.tight_layout()
        plt.show()

    def plot_seasonality_by_theme(self, df, theme_kw_map, region_name, freq='W', period=52, exclude_cols=['isPartial', 'date']):
        """Plot seasonal decomposition for each theme"""
        if df is None or df.empty:
            print(f"No data available for seasonality analysis: {region_name}")
            return
            
        df = df.copy()
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
        # Prepare theme -> list of keyword columns mapping
        theme2keywords = theme_kw_map.groupby('Theme')['Keyword'].apply(list).to_dict()
        
        for theme, keywords in theme2keywords.items():
            # Filter out any columns missing in df
            theme_cols = [kw for kw in keywords if kw in df.columns and kw not in exclude_cols]
            if not theme_cols:
                print(f"No matching columns for theme '{theme}'")
                continue
            
            # Aggregate search volume for this theme (sum or mean/median, here we use sum)
            agg_trend = df[theme_cols].sum(axis=1)
            agg_trend = agg_trend.asfreq(freq)
            
            # Seasonal decomposition (skip if not enough data)
            try:
                result = seasonal_decompose(agg_trend, model='additive', period=period)
            except ValueError:
                print(f"Not enough data for theme '{theme}' in {region_name}")
                continue
            
            seasonal = result.seasonal.dropna()
            
            plt.figure(figsize=(12, 6))
            plt.plot(seasonal, label=f'{region_name} - {theme}')
            
            # Group by year and annotate peak/dip
            seasonal_series = seasonal.copy()
            seasonal_by_year = seasonal_series.groupby(seasonal_series.index.year)
            
            for year, group in seasonal_by_year:
                peak_idx = group.idxmax()
                dip_idx = group.idxmin()
                peak_month = peak_idx.strftime('%b')
                dip_month = dip_idx.strftime('%b')
                plt.scatter(peak_idx, group.loc[peak_idx], color='green', marker='^', s=100, zorder=5)
                plt.scatter(dip_idx, group.loc[dip_idx], color='red', marker='v', s=100, zorder=5)
                plt.text(peak_idx, group.loc[peak_idx], f'Peak: {peak_month} {year}', color='green', fontsize=9, ha='left', va='bottom')
                plt.text(dip_idx, group.loc[dip_idx], f'Dip: {dip_month} {year}', color='red', fontsize=9, ha='left', va='top')
            
            plt.title(f"Seasonal Pattern for {region_name}: {theme} (Aggregated Search Volume, Peaks & Dips Highlighted)")
            plt.ylabel("Aggregated Search Volume")
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            plt.legend()
            plt.tight_layout()
            plt.show()

    def extract_help_data(self):
        """Extract help vs need help data by state"""
        help_theme_keywords = self.help_theme_kw_map.groupby('Theme')['Keyword'].apply(list).to_dict()
        results = {theme: {} for theme in help_theme_keywords.keys()}

        for theme, keywords in help_theme_keywords.items():
            for i in range(0, len(keywords), 4):   # batch size 4, add base_keyword
                batch = keywords[i:i+4]
                if self.base_keyword not in batch:
                    batch.append(self.base_keyword)
                try:
                    self.pytrends.build_payload(batch, cat=0, timeframe='today 12-m', geo='US', gprop='')
                    # Get interest by region (state-level)
                    data = self.pytrends.interest_by_region(resolution='REGION', inc_low_vol=True, inc_geo_code=False)
                    if not data.empty:
                        # Normalize by base keyword if present
                        if self.base_keyword in data.columns:
                            base_series = data[self.base_keyword].replace(0, 1)
                            for kw in batch:
                                if kw in data.columns:
                                    normalized = data[kw] / base_series
                                    results[theme].setdefault(kw, pd.Series(dtype=float))
                                    # Store as a series indexed by state
                                    results[theme][kw] = normalized
                    time.sleep(10)
                except Exception as e:
                    print(f"Error with batch {batch}: {e}")
        
        self.results = results
        
        # Save results
        current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
        with open(f'googletrends_mapdata_{current_datetime}.pkl', 'wb') as f:
            pickle.dump(results, f)
        
        # Convert to CSV
        rows = []
        for theme in results:
            for keyword in results[theme]:
                series = results[theme][keyword]
                if isinstance(series, pd.Series):
                    for state, value in series.items():
                        rows.append({'Theme': theme, 'Keyword': keyword, 'State': state, 'Value': value})
        df = pd.DataFrame(rows)
        df.to_csv(f'googletrends_help_{current_datetime}.csv', index=False)
        
        print("✓ Help data extraction completed")

    def get_theme_state_avg(self, results):
        """Convert results to state-theme averages"""
        theme_state_values = {}
        for theme, kw_dict in results.items():
            state_values = {}
            for keyword, series in kw_dict.items():
                for state, value in series.items():
                    state_values.setdefault(state, []).append(value)
            # For each state, average across all keywords for this theme
            theme_state_values[theme] = {
                state: float(np.mean(vals)) if vals else np.nan
                for state, vals in state_values.items()
            }
        # Convert to DataFrame (states as index, themes as columns)
        df = pd.DataFrame(theme_state_values)
        return df

    def add_state_names(self, df):
        """Add full state names for merging with geo data"""
        state_abbr_to_name = {s.abbr: s.name for s in us.states.STATES}
        # If index is abbreviation, map it. If not, just add as 'state_name'
        if all(idx in state_abbr_to_name for idx in df.index):
            df['state_name'] = df.index.map(state_abbr_to_name)
        else:
            df['state_name'] = df.index
        return df

    def load_us_states_shapefile(self, shp_file):
        """Load US states shapefile"""
        us_gdf = gpd.read_file(shp_file)
        us_states_gdf = us_gdf[us_gdf['iso_a2'] == 'US'].copy()
        if us_states_gdf.crs is None:
            us_states_gdf = us_states_gdf.set_crs(epsg=4326)
        else:
            us_states_gdf = us_states_gdf.to_crs(epsg=4326)
        return us_states_gdf

    def merge_data(self, us_states_gdf, df_heatmap):
        """Merge geographic and heatmap data"""
        merged = us_states_gdf.merge(df_heatmap, left_on='name', right_on='state_name')
        return merged

    def display_choropleth_maps(self, merged, df_heatmap):
        """Display choropleth maps for each theme"""
        for theme in df_heatmap.columns:
            if theme == 'state_name':
                continue
            merged[theme] = pd.to_numeric(merged[theme], errors='coerce')
            m = folium.Map(location=[37.8, -96], zoom_start=4)
            folium.Choropleth(
                geo_data=merged,
                name='Choropleth',
                data=merged,
                columns=['name', theme],
                key_on='feature.properties.name',
                fill_color='YlOrRd',
                fill_opacity=0.7,
                line_opacity=0.2,
                legend_name=f'{theme} (Mean Search Interest)',
                nan_fill_color='gray'
            ).add_to(m)
            folium.GeoJson(
                merged,
                tooltip=folium.features.GeoJsonTooltip(fields=['name', theme], aliases=['State:', 'Value:'])
            ).add_to(m)
            # Save map instead of displaying (since we're in a script)
            current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
            m.save(f'googletrends_map_{theme}_{current_datetime}.html')
            print(f"✓ Choropleth map saved for theme: {theme}")

    def run_historical_analysis(self, zipcode='90001'):
        """Run complete historical analysis workflow"""
        print("=== Starting Historical Analysis ===")
        
        # Load data files
        self.load_data_files()
        
        # Extract related queries
        self.extract_related_queries()
        
        # Extract historical data
        self.extract_historical_data(zipcode)
        
        if self.national_norm is not None and not self.national_norm.empty:
            # Plot national trends
            self.plot_theme_trends(self.national_norm, self.base_keyword, 'National Theme Search Interest Over Time')
            self.update_viz_status('historical_timeline_national')
            
            # Plot state trends
            state_abbr = self.get_state(zipcode)
            self.plot_theme_trends(self.state_norm, self.base_keyword, f'{state_abbr} Theme Search Interest Over Time')
            self.update_viz_status('historical_timeline_state')
            
            # Theme comparison
            national_theme_scores_raw = self.compute_theme_scores(self.national_norm, self.theme_kw_map, base_keyword=self.base_keyword)
            state_theme_scores_raw = self.compute_theme_scores(self.state_norm, self.theme_kw_map, base_keyword=self.base_keyword)
            
            # Normalize scores
            national_theme_scores = self.normalize_theme_scores(national_theme_scores_raw)
            state_theme_scores = self.normalize_theme_scores(state_theme_scores_raw)
            
            # Plot comparison
            self.plot_grouped_horizontal_bar(national_theme_scores, state_theme_scores, "National", "State")
            self.update_viz_status('theme_comparison_chart')
            
            # Seasonality analysis
            self.plot_seasonality_by_theme(self.national_norm, self.theme_kw_map, region_name='National')
            self.update_viz_status('seasonality_national')
            
            self.plot_seasonality_by_theme(self.state_norm, self.theme_kw_map, region_name='State')
            self.update_viz_status('seasonality_state')
        
        print("=== Historical Analysis Complete ===")

    def run_geographic_analysis(self):
        """Run geographic analysis workflow"""
        print("=== Starting Geographic Analysis ===")
        
        # Extract help data
        self.extract_help_data()
        
        if self.results:
            # Create heatmap data
            df_heatmap = self.get_theme_state_avg(self.results)
            df_heatmap = self.add_state_names(df_heatmap)
            
            # Load geographic data
            us_states_gdf = self.load_us_states_shapefile(DATA_FILES['shapefile'])
            merged = self.merge_data(us_states_gdf, df_heatmap)
            
            # Create maps
            self.display_choropleth_maps(merged, df_heatmap)
            self.update_viz_status('choropleth_maps')
        
        print("=== Geographic Analysis Complete ===")

    def export_status(self):
        """Export status for frontend integration"""
        status = self.get_loading_status()
        current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
        with open(f'googletrends_status_{current_datetime}.json', 'w') as f:
            json.dump(status, f, indent=2)
        
        print(f"✓ Status exported to: googletrends_status_{current_datetime}.json")
        return status

    def run_complete_analysis(self, zipcode='90001'):
        """Run complete analysis pipeline"""
        print("🚀 Starting Google Trends Analysis Pipeline")
        print("=" * 50)
        
        try:
            # Run historical analysis
            self.run_historical_analysis(zipcode)
            
            # Run geographic analysis
            self.run_geographic_analysis()
            
            # Export final status
            final_status = self.export_status()
            
            print("\n" + "=" * 50)
            print("✅ Analysis Complete!")
            print(f"Progress: {final_status['progress']['completed']}/{final_status['progress']['total']} ({final_status['progress']['percentage']:.1f}%)")
            print(f"Overall Ready: {final_status['overall_ready']}")
            
            return final_status
            
        except Exception as e:
            print(f"❌ Error during analysis: {e}")
            raise


def main():
    """Main function to run the analysis"""
    # Configuration
    ZIPCODE = '90001'  # Default zipcode (Los Angeles, CA)
    
    # Initialize analyzer
    analyzer = GoogleTrendsAnalyzer()
    
    # Run complete analysis
    try:
        analyzer.run_complete_analysis(zipcode=ZIPCODE)
        print("\n🎉 Google Trends analysis completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Analysis interrupted by user")
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

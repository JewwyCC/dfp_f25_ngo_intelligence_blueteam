#!/usr/bin/env python3
"""
Generate Demo HTML Maps for Google Trends
This script creates sample HTML choropleth maps for testing the dashboard integration
"""

import folium
import pandas as pd
import numpy as np
import os
from datetime import datetime
from pathlib import Path

def create_demo_choropleth_map(theme_name, output_dir):
    """Create a demo choropleth map for testing"""
    
    # Create sample data for US states
    states_data = {
        'name': ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware',
                'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky',
                'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi',
                'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico',
                'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania',
                'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont',
                'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming'],
        'value': np.random.randint(20, 100, 50)  # Random values between 20-100
    }
    
    df = pd.DataFrame(states_data)
    
    # Create map centered on US
    m = folium.Map(location=[37.8, -96], zoom_start=4, tiles='OpenStreetMap')
    
    # Add choropleth layer
    folium.Choropleth(
        geo_data='https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/us-states.json',
        name='Choropleth',
        data=df,
        columns=['name', 'value'],
        key_on='feature.properties.name',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=f'{theme_name} (Search Interest)',
        nan_fill_color='gray'
    ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Save map
    current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"google_trends_choropleth_{theme_name}_{current_datetime}.html"
    map_file = os.path.join(output_dir, filename)
    
    m.save(map_file)
    print(f"Demo map created: {map_file}")
    return map_file

def main():
    """Generate demo maps for all themes"""
    
    # Define themes
    themes = [
        "General_Information_and_Definitions",
        "Location-specific_search", 
        "Policy_Organisations_and_Solutions",
        "Statistics_Data_and_Scope"
    ]
    
    # Output directory
    output_dir = Path(__file__).parent.parent.parent / "data" / "demo_data" / "demo_session" / "artifacts"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating demo maps in: {output_dir}")
    
    # Create demo maps for each theme
    for theme in themes:
        create_demo_choropleth_map(theme, output_dir)
    
    print("Demo maps generation complete!")

if __name__ == "__main__":
    main()

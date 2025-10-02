# Google Trends Analysis Project

## Overview
This project analyzes Google Trends data for homelessness-related keywords across different themes and geographic regions (national vs state-level). It includes comprehensive data visualization and status tracking functionality.

## Features
- **Historical Timeline Analysis**: Compare search trends between national and state levels
- **Theme-based Analysis**: Break down search interest by different homelessness-related themes
- **Seasonality Analysis**: Identify seasonal patterns in search behavior
- **Geographic Mapping**: Choropleth maps showing state-by-state search interest variations
- **Real-time Status Tracking**: Monitor data visualization completion for frontend integration

## Project Structure
```
Project/
├── googletrends.ipynb          # Main analysis notebook
├── data python files/          # Input data and configuration files
│   ├── keyword_theme.xlsx      # Theme-keyword mapping
│   ├── help keywords.xlsx      # Help-related keywords
│   ├── uszips.csv             # ZIP code to state mapping
│   └── ne_110m_admin_1_states_provinces/  # Shapefile for mapping
├── results.csv                # Historical results (legacy)
├── results.pkl                # Historical results (legacy)
└── README.md                  # This file
```

## Data Sources
- **Google Trends API**: Primary data source via `pytrends` library
- **Keyword Configuration**: Excel files defining themes and search terms
- **Geographic Data**: Shapefiles for US state boundaries

## Key Components

### 1. Data Collection
- Automated batch processing with rate limiting
- Normalization using base keywords
- State-level and national-level data extraction

### 2. Visualizations
- Historical timeline plots
- Theme comparison charts
- Seasonal decomposition analysis
- Interactive choropleth maps

### 3. Status Tracking System
The notebook includes a comprehensive tracking system for monitoring visualization completion:
- Individual visualization status tracking
- Progress percentage calculation
- JSON export for frontend integration
- Automatic completion detection

### 4. File Naming Convention
All output files follow the standardized format: `{datasource}_{datetime}`
- Example: `googletrends_national_20251002_143022.xlsx`

## Setup and Installation

### Prerequisites
```bash
pip install pandas
pip install pytrends==4.9.2
pip install urllib3==1.26.18
pip install openpyxl
pip install matplotlib
pip install folium
pip install geopandas
pip install us
pip install numpy
pip install statsmodels
```

### Configuration
1. Update file paths in the notebook to match your environment
2. Ensure data files are in the correct directory structure
3. Verify API rate limits and adjust delay parameters as needed

## Usage

### Running the Analysis
1. Execute setup cells to install dependencies
2. Run data collection cells (note: may take time due to API rate limits)
3. Generate visualizations
4. Monitor status using the tracking system

### Status Monitoring
```python
# Check loading status
status = get_loading_status()
print(f"Progress: {status['progress']['percentage']:.1f}%")
print(f"Ready: {status['overall_ready']}")
```

## Output Files
- `googletrends_national_{datetime}.xlsx` - National-level data
- `googletrends_state_{datetime}.xlsx` - State-level data
- `googletrends_mapdata_{datetime}.pkl` - Mapping data
- `googletrends_help_{datetime}.csv` - Help-related search data
- `googletrends_status_{datetime}.json` - Status tracking data

## API Considerations
- **Rate Limiting**: Built-in delays to respect Google Trends API limits
- **Error Handling**: Retry logic for failed requests
- **Data Normalization**: Consistent scaling across different time periods and regions

## Future Enhancements
- [ ] Real-time data streaming
- [ ] Additional geographic granularity (county-level)
- [ ] Machine learning trend prediction
- [ ] Interactive dashboard integration
- [ ] Automated report generation

## Contributing
When contributing to this project:
1. Follow the established file naming convention
2. Update the status tracking system for new visualizations
3. Maintain consistent code documentation
4. Test API rate limiting thoroughly

## Notes
- Some cells may show execution errors due to API rate limits or missing data files
- The notebook is designed to handle partial failures gracefully
- Status tracking system provides real-time feedback on completion progress
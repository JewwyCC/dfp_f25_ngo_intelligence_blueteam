# NGO Intelligence Platform

Streamlit dashboard and collection pipeline that merges homelessness-related signals from Google Trends, News API, Reddit, and Bluesky. The app can run entirely on demo data for instant exploration or pull fresh data (credentials and network access required).

## What’s Included

- `ngo_dashboard.py` – Streamlit UX (loading flow + dashboard)
- `master_scraper_data.py` – orchestrates multi-source collection
- `master_scraper_viz.py` – renders PNG/HTML artifacts per session
- `data/demo_data/demo_session` – canonical demo bundle (keep intact)
- `data/master_output` – timestamped runs written here
- `scripts/` – source-specific collectors and helpers

## Quick Start

```bash
git clone <repo>

OR unzip the ngo_intel_bundle.zip

In Terminal:
cd dfp_ngo_module (from your own path, please direct here)
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
./packaging/run_dashboard.sh      # macOS / Linux
packaging\run_dashboard.bat       # Windows

--
streamlit run ngo_dashboard.py
```

Open http://localhost:8501, choose “Load Visualization” for the demo session, or enter a ZIP code to trigger live collection. Bluesky collection requires valid credentials in `auth/bluesky/config/auth.json` and outbound access to `bsky.social`.

## Data & Sessions

- **Demo data**: keep `data/demo_data/demo_session` versioned; loaders fall back here if live collection fails.
- **Live runs**: every collection writes to `data/master_output/session_<timestamp>` with `raw_data/` (CSV/JSON/JSONL) and `artifacts/` images.
- **Cleanup**: stale sessions can be pruned manually; the platform now retains only the latest snapshots in-repo.

## Packaging & Distribution

Use the lightweight scripts in `packaging/` to produce a self-contained archive (embedded venv, demo data, launchers):

```bash
# macOS / Linux
bash packaging/build_bundle.sh

# Windows (PowerShell or cmd)
packaging\build_bundle.bat
```

The scripts create `ngo_intel_bundle/` and `ngo_intel_bundle.zip` beside the repo. Inside the bundle:

```
unzip ngo_intel_bundle.zip
cd ngo_intel_bundle
./scripts/run_dashboard.sh      # macOS / Linux
scripts\run_dashboard.bat       # Windows
```

Both launchers activate the bundled virtual environment and start Streamlit on port 8501.

> Re-run these scripts whenever you cut a new release — they rebuild the embedded venv and refresh `ngo_intel_bundle.zip`.

Need a quick ad-hoc archive?

```bash
zip -r ngo_intel_project.zip dfp_ngo_module -x 'dfp_ngo_module/.venv/*' 'dfp_ngo_module/data/master_output/session_*'
```

## Notes & Troubleshooting

- Collectors expect live credentials and outbound access (News API key, Bluesky app password, etc.).
- Google Trends uses the latest workbook produced by `master_scraper_data.py`; rerun the scraper when you need fresh trends.
- `requirements.txt` stays lean—no inline tutorials—and is safe for `pip install -r requirements.txt`.
- Demo files are intentionally preserved; do not remove `data/demo_data`.

For further automation (CI, tests) rely on the standard Python tooling already listed in `requirements.txt`.
```
│   ├── google_trends/           # Google Trends scraper
│   ├── news_api/                # News API scraper
│   ├── reddit/                  # Reddit scraper
│   └── bluesky/                 # Bluesky scraper
└── auth/                        # Authentication configurations
    └── bluesky/                 # Bluesky API credentials

```

---

## 🔧 Configuration

### API Credentials

1. **News API**: Add your API key to `scripts/news_api/credentials.py`
2. **Reddit**: Configure PRAW credentials in `scripts/reddit/config.py`
3. **Bluesky**: Add authentication to `auth/bluesky/auth.json`

### Environment Variables

```bash
# Optional: Disable HuggingFace tokenizers parallelism warning
export TOKENIZERS_PARALLELISM=false
```

---

## 📈 Usage Examples

### Quick Analysis with Demo Data

1. Launch the dashboard: `./start_platform.sh dashboard`
2. Click "Go To Visualization" to load demo data
3. Explore comprehensive sample visualizations

### Fresh Data Collection

1. Enter a US ZIP code (e.g., "10001" for NYC)
2. Click "Analyze Region"
3. Monitor real-time progress
4. View generated visualizations

### Custom Analysis

1. Navigate to specific sections
2. Filter by themes or time periods
3. Export data or visualizations
4. Share insights and findings

---

## 🐛 Troubleshooting

### Common Issues

**Dashboard won't start**

```bash
# Check dependencies
pip install -r requirements.txt

# Try direct Streamlit
streamlit run ngo_dashboard.py
```

**Data collection fails**

```bash
# Check API credentials
# Verify internet connection
# Check logs in terminal output
```

**Visualizations not loading**

```bash
# Ensure demo data exists in data/demo_data/
# Check file permissions
# Verify Streamlit cache
```

### Performance Tips

- Use demo data for quick exploration
- Google Trends uses demo data for fast loading
- Fresh data collection may take 2-5 minutes
- Clear browser cache if visualizations appear outdated

---

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make changes and test thoroughly
4. Submit a pull request

### Code Style

- Follow Python PEP 8 guidelines
- Use descriptive variable names
- Add docstrings to functions
- Include error handling

---

## 📄 License

This project is developed for educational and research purposes at Carnegie Mellon University.

---

## 🙏 Acknowledgments

- **DFP Blue Team**: Jerry, Kaitlin, Mel, Rizaldy, Shriya
- **Carnegie Mellon University**: DFP F25 Program
- **Open Source Libraries**: Streamlit, Plotly, Pandas, and more

---

## 📞 Support

For questions or issues:

1. Check the troubleshooting section above
2. Review the demo data and examples
3. Check terminal output for detailed error messages
4. Ensure all dependencies are properly installed

---

*Last updated: 9 October 2025*

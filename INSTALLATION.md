# Installation Guide - NGO Intelligence Platform

## Quick Start (Recommended)

### Option 1: Automated Installation (macOS/Linux)

```bash
# Clone the repository (if not already done)
cd dfp_ngo_module

# Make the install script executable
chmod +x install.sh

# Run the installation script
./install.sh
```

This will:
1. Check Python version (requires 3.8+)
2. Create a virtual environment
3. Install all dependencies
4. Verify the installation

### Option 2: Manual Installation (All Platforms)

#### Step 1: Create Virtual Environment

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

#### Step 2: Upgrade pip

```bash
pip install --upgrade pip
```

#### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all ~30 packages (may take 5-10 minutes).

#### Step 4: Verify Installation

```bash
python verify_installation.py
```

You should see all modules marked with ✓ (green checkmark).

---

## Platform-Specific Instructions

### macOS (Apple Silicon - M1/M2/M3)

After installing requirements, optimize PyTorch for Apple Silicon:

```bash
pip install --upgrade torch torchvision torchaudio
```

Or use the nightly build for best performance:

```bash
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cpu
```

### Linux (Ubuntu/Debian)

Install tkinter system package (required for GUI):

```bash
sudo apt-get update
sudo apt-get install python3-tk python3-dev
```

If geopandas installation fails, install system dependencies:

```bash
sudo apt-get install gdal-bin libgdal-dev libspatialindex-dev
```

### Windows

No special steps required! Just follow the manual installation process above.

---

## Troubleshooting Common Issues

### Issue 1: "No module named 'tkinter'"

**Linux users:**
```bash
sudo apt-get install python3-tk
```

**macOS/Windows:** tkinter should be included by default. Reinstall Python if missing.

### Issue 2: PyTorch installation fails

**Slow connection / Large file:**
```bash
pip install --no-cache-dir torch transformers
```

**Apple Silicon:**
```bash
pip install --upgrade torch torchvision torchaudio
```

**CUDA GPU support (NVIDIA):**
Visit https://pytorch.org/get-started/locally/ and select your CUDA version.

### Issue 3: geopandas installation fails

**Option 1:** Use conda instead of pip
```bash
conda install geopandas
```

**Option 2:** Install without build isolation
```bash
pip install geopandas --no-build-isolation
```

**Option 3 (Linux):** Install system dependencies first
```bash
sudo apt-get install gdal-bin libgdal-dev libspatialindex-dev
pip install geopandas
```

### Issue 4: SSL certificate errors

```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### Issue 5: transformers model download fails

Set HuggingFace cache directory:

**macOS/Linux:**
```bash
export HF_HOME=~/.cache/huggingface
```

**Windows:**
```cmd
set HF_HOME=%USERPROFILE%\.cache\huggingface
```

### Issue 6: Out of memory during installation

Install large packages separately with no-cache:

```bash
pip install --no-cache-dir torch
pip install --no-cache-dir transformers
pip install -r requirements.txt
```

---

## Verification

After installation, verify all modules are working:

```bash
python verify_installation.py
```

You should see output like:

```
✓ pandas                       OK
✓ numpy                        OK
✓ requests                     OK
✓ scipy                        OK
✓ atproto                      OK
✓ praw                         OK
...

✅ All dependencies installed successfully!
```

---

## What Gets Installed

### Core Dependencies (~10 packages)
- pandas, numpy, scipy, requests
- Data manipulation and scientific computing

### Scraper-Specific (~8 packages)
- **Bluesky:** atproto
- **Reddit:** praw, textblob
- **News API:** newsapi-python, beautifulsoup4, lxml
- **Google Trends:** pytrends, urllib3

### Visualization (~12 packages)
- matplotlib, seaborn, plotly, wordcloud
- folium, geopandas, openpyxl

### AI/ML (~2 packages, ~2GB)
- torch, transformers
- For political leaning classification

### Dashboard (~2 packages)
- streamlit, flask
- Web-based data dashboards

**Total:** ~30 packages, ~3GB disk space

---

## Minimal Installation (For Testing)

If you only want to test specific modules:

### Bluesky Only
```bash
pip install atproto pandas requests matplotlib wordcloud
```

### Reddit Only
```bash
pip install praw textblob pandas numpy matplotlib scipy wordcloud
```

### News API Only
```bash
pip install newsapi-python beautifulsoup4 pandas requests transformers torch matplotlib wordcloud
```

### Google Trends Only
```bash
pip install pytrends urllib3==1.26.18 pandas openpyxl matplotlib folium geopandas us statsmodels
```

---

## Next Steps

After successful installation:

1. **Configure API credentials:**
   - Bluesky: `auth/bluesky/config/auth.json`
   - Reddit: `scripts/reddit/config.py`
   - News API: `scripts/news_api/credentials.py`

2. **Run test collection:**
   ```bash
   python master_scraper_data.py --duration 600
   ```

3. **Generate visualizations:**
   ```bash
   python master_scraper_viz.py --session session_XXXXXX_XXXXXX
   ```

4. **Launch dashboard:**
   ```bash
   streamlit run ngo_dashboard.py
   ```

---

## Getting Help

If you encounter issues not covered here:

1. Check `requirements.txt` comments for detailed notes
2. Run `python verify_installation.py` for diagnostic info
3. Check Python version: `python --version` (must be 3.8+)
4. Try installing in a fresh virtual environment

**Common fixes:**
- Delete `venv/` and start fresh
- Upgrade pip: `pip install --upgrade pip`
- Clear pip cache: `pip cache purge`
- Use `--no-cache-dir` flag for large packages

---

**Installation time:** 5-15 minutes depending on connection speed  
**Disk space required:** ~3GB (mostly PyTorch and transformers)  
**Python version:** 3.8 or higher (tested on 3.9-3.11)


# 🔧 Setup Instructions
## DFP F25 Social Media Blue Team - Bluesky Collector

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/dfp_f25_socmed_blueteam.git
   cd dfp_f25_socmed_blueteam
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create credentials file:**
   ```bash
   # Create data/config/auth.json with your Bluesky credentials
   {
     "bluesky": {
       "username": "your.email@example.com",
       "password": "your_bluesky_password"
     }
   }
   ```

## 🚀 Quick Start

```bash
# Test collection (30 seconds)
python bluesky_social_justice_collector.py --duration 30

# Production collection (20 minutes)
python bluesky_social_justice_collector.py --duration 1200
```

## 📊 Data Output

- **Session data**: `data/sessions/[session_name]/`
- **Alltime data**: `data/alltime/`
- **Both formats**: JSONL and CSV

## 🔐 Security

- Credentials file (`data/config/auth.json`) is in `.gitignore`
- Never commit authentication information
- Data files are also gitignored for privacy

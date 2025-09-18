# 🐙 GitHub Repository Setup
## DFP F25 Social Media Blue Team

## 📋 Manual GitHub Repository Creation

Since GitHub CLI is not available, please follow these steps:

### 1. Create GitHub Repository

1. Go to [GitHub.com](https://github.com)
2. Click "New repository" (+ icon)
3. **Repository name**: `dfp_f25_socmed_blueteam`
4. **Description**: `Bluesky Social Justice Data Collector - DFP F25 Social Media Blue Team`
5. **Visibility**: Public or Private (your choice)
6. **DO NOT** initialize with README (we already have one)
7. Click "Create repository"

### 2. Push Local Repository

Copy and run these commands in your terminal:

```bash
cd /Users/rzrizaldy/CodeFolder/dfp_f25_socmed_blueteam

# Add GitHub remote (replace 'yourusername' with your GitHub username)
git remote add origin https://github.com/yourusername/dfp_f25_socmed_blueteam.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### 3. Verify Security

✅ **Credentials are safe**: `data/config/auth.json` is in `.gitignore`  
✅ **Data files ignored**: Personal data stays local  
✅ **Template provided**: `auth_template.json` shows required format  

### 4. Repository Contents

Your GitHub repo will contain:
```
dfp_f25_socmed_blueteam/
├── README.md                              # 📖 Main documentation
├── SETUP.md                               # 🔧 Installation guide  
├── bluesky_social_justice_collector.py    # 🔧 Core collector script
├── bluesky_social_justice_analysis.ipynb  # 📓 Analysis notebook
├── requirements.txt                       # 📦 Dependencies
├── data/config/
│   ├── auth_template.json                 # 🔐 Credential template
│   ├── keywords.txt                       # 🎯 Search keywords
│   └── regex_patterns.txt                 # 🔍 Advanced filtering
└── .gitignore                             # 🛡️ Security rules
```

### 5. Clone Instructions for Others

Others can clone and set up with:
```bash
git clone https://github.com/yourusername/dfp_f25_socmed_blueteam.git
cd dfp_f25_socmed_blueteam
pip install -r requirements.txt

# Copy template and add credentials
cp data/config/auth_template.json data/config/auth.json
# Edit data/config/auth.json with Bluesky credentials

# Run collection
python bluesky_social_justice_collector.py --duration 600
```

## 🎯 Repository Features

- **Clean codebase**: Only essential files
- **Security first**: Credentials never committed
- **Ready to run**: Complete setup instructions
- **Rich documentation**: README + SETUP + inline comments
- **Professional structure**: Academic project ready

---

**🚀 Ready for GitHub! Follow steps 1-2 above to publish your repository.**

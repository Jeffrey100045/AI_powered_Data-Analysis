# AI Analytics Platform with Google Drive Integration

## 🚀 Quick Start

### Frontend (Running ✓)
The frontend is already running at: **http://localhost:5173**

### Backend
To start the backend server, you need Python installed. Then run:

```powershell
cd c:\Users\Dell\Desktop\kavi\backend
python main.py
```

Backend will run on: **http://localhost:8889**

---

## ☁️ Google Drive Integration

### Features
- Upload datasets directly to Google Drive
- View cloud file history
- Download and analyze files from Drive
- Secure OAuth2 authentication

### Setup (Optional)
Google Drive integration requires OAuth2 credentials. See [SETUP_GUIDE.md](C:\Users\Dell\.gemini\antigravity\brain\8dcbd8f6-5b44-4957-a002-9da6beaaa35d\SETUP_GUIDE.md) for detailed instructions.

**The app works perfectly without Google Drive integration!**

---

## 📊 Features

- **Data Upload**: CSV/Excel file support
- **AI Filtering**: Natural language data queries
- **Machine Learning**: Automatic predictive modeling
- **Auto Charts**: Smart visualizations
- **PDF Reports**: Comprehensive analysis reports
- **Cloud Storage**: Google Drive integration (optional)

---

## 🔧 Installation

### Backend Dependencies
```powershell
cd backend
python -m pip install -r requirements.txt
```

### Frontend Dependencies (Already Installed ✓)
```powershell
cd frontend
npm install
```

---

## 📝 Usage

1. Open http://localhost:5173 in your browser
2. Log in with Firebase credentials
3. Upload a CSV/Excel file
4. Explore the tabs:
   - **DATA**: Upload and preview
   - **☁️ CLOUD**: Google Drive files
   - **FILTER**: AI-powered filtering
   - **ML**: Machine learning predictions
   - **AUTO CHARTS**: Automatic visualizations
   - **REPORT**: Generate PDF reports

---

## 🆘 Troubleshooting

### Python Not Found
Install Python from https://python.org/downloads/
Make sure to check "Add Python to PATH" during installation.

### Backend Won't Start
Ensure all dependencies are installed:
```powershell
python -m pip install -r requirements.txt
```

### Google Drive Not Working
1. Check that `credentials.json` is configured
2. See SETUP_GUIDE.md for OAuth2 setup
3. The app works without Drive integration

---

## 📂 Project Structure

```
kavi/
├── backend/
│   ├── main.py                    # FastAPI server
│   ├── processing.py              # Data analysis logic
│   ├── reporting.py               # PDF generation
│   ├── google_drive_service.py    # Google Drive integration
│   ├── credentials.json           # OAuth2 credentials (configure this)
│   └── requirements.txt           # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx      # Main dashboard
│   │   │   ├── CloudStorage.jsx   # Google Drive UI
│   │   │   └── Auth.jsx           # Authentication
│   │   ├── App.jsx
│   │   └── api.js
│   └── package.json
```

---

## 🎯 Next Steps

1. ✅ Frontend is running
2. ⚠️ Start the backend server (requires Python)
3. 🔧 Configure Google Drive (optional)
4. 🎉 Start analyzing data!

For detailed setup instructions, see [SETUP_GUIDE.md](C:\Users\Dell\.gemini\antigravity\brain\8dcbd8f6-5b44-4957-a002-9da6beaaa35d\SETUP_GUIDE.md)

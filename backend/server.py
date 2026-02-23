from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil, os, re, io
import pandas as pd
import numpy as np
import google.generativeai as genai
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from google_drive_service import GoogleDriveService

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY: genai.configure(api_key=GEMINI_API_KEY)

class DataAnalyst:
    def __init__(self):
        self.df = None
        self.filtered_df = None
        self.num_cols = []
        self.all_cols = []
        self.ml_results = {}
        self.model = genai.GenerativeModel('gemini-2.0-flash') if GEMINI_API_KEY else None

    def load_data(self, file_path):
        try:
            if file_path.endswith(".csv"): self.df = pd.read_csv(file_path, low_memory=False)
            elif file_path.endswith(".xlsx") or file_path.endswith(".xls"): self.df = pd.read_excel(file_path)
            else: return []
            self.clean_data()
            self.filtered_df = self.df.copy()
            self.num_cols = self.df.select_dtypes(include=np.number).columns.tolist()
            self.all_cols = self.df.columns.tolist()
            preview = self.df.head(20).copy()
            return preview.where(pd.notnull(preview), None).to_dict(orient="records")
        except Exception as e:
            print(f"Load Error: {e}")
            return []

    def clean_data(self):
        if self.df is None: return
        for col in self.df.columns:
            if pd.api.types.is_numeric_dtype(self.df[col]):
                self.df[col] = self.df[col].fillna(self.df[col].median() if not self.df[col].isna().all() else 0)
            else:
                self.df[col] = self.df[col].fillna('Unknown')

    def analyze_chart_with_ai(self, chart_type, x_col, y_col, data):
        if not self.model: return None
        try:
            data_summary = data[:10]
            prompt = f"Analyze this {chart_type} chart. X: {x_col}, Y: {y_col if y_col else 'Frequency'}. Data: {data_summary}. Concise 1-2 sentence insight."
            return self.model.generate_content(prompt).text.strip()
        except: return None

    def get_auto_charts(self):
        if self.df is None: return []
        source = self.filtered_df if self.filtered_df is not None else self.df
        recs = []
        if self.num_cols:
            col = self.num_cols[0]
            counts, bins = np.histogram(source[col].dropna(), bins=10)
            data = [{"name": f"{bins[i]:.1f}", "value": int(counts[i])} for i in range(len(counts))]
            recs.append({"type": "Histogram", "x": str(col), "data": data, "reason": self.analyze_chart_with_ai("Histogram", col, None, data) or f"Distribution of {col}"})
        return recs

    def run_ml(self, target):
        if self.df is None or target not in self.num_cols: return {"error": "Invalid target"}
        try:
            data = self.filtered_df.dropna()
            X = data[self.num_cols].drop(columns=[target])
            y = data[target]
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
            model = LinearRegression().fit(X_train, y_train)
            preds = model.predict(X_test)
            self.ml_results = {"r2": float(r2_score(y_test, preds)), "mse": float(mean_squared_error(y_test, preds)), "model": "Linear Regression"}
            return self.ml_results
        except Exception as e: return {"error": str(e)}

app = FastAPI()
analyst = DataAnalyst()
drive_service = GoogleDriveService()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not os.path.exists("uploads"): os.makedirs("uploads")
    path = os.path.join("uploads", file.filename)
    with open(path, "wb") as b: shutil.copyfileobj(file.file, b)
    preview = analyst.load_data(path)
    return {"message": "Success", "preview": preview, "columns": analyst.all_cols, "auto_charts": analyst.get_auto_charts()}

@app.get("/auto_charts")
async def get_charts(): return {"auto_charts": analyst.get_auto_charts(), "charts": analyst.get_auto_charts()}

@app.get("/session_state")
async def get_state(): return {"active": analyst.df is not None, "preview": [], "columns": analyst.all_cols, "auto_charts": analyst.get_auto_charts()}

@app.get("/drive/status")
async def drive_status(): return {"authenticated": drive_service.is_authenticated()}

@app.post("/drive/auth")
async def drive_auth():
    try:
        drive_service.authenticate()
        return {"success": True}
    except Exception as e: return {"success": False, "error": str(e)}

@app.get("/drive/files")
async def drive_files(): return drive_service.list_files()

@app.get("/")
def home(): return {"status": "Backend running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

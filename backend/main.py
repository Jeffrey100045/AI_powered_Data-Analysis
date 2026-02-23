from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os
import pandas as pd
import numpy as np
import re
import google.generativeai as genai
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from .google_drive_service import GoogleDriveService
from . import reporting
from fastapi.responses import FileResponse


# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

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
            if file_path.endswith(".csv"):
                self.df = pd.read_csv(file_path, low_memory=False)
            elif file_path.endswith(".xlsx") or file_path.endswith(".xls"):
                self.df = pd.read_excel(file_path)
            else:
                return []
            self.clean_data()
            self.filtered_df = self.df.copy()
            self.num_cols = self.df.select_dtypes(include=np.number).columns.tolist()
            self.all_cols = self.df.columns.tolist()
            preview_df = self.df.head(50).copy()
            preview_df = preview_df.where(pd.notnull(preview_df), None)
            return preview_df.to_dict(orient="records")
        except Exception as e:
            print(f"Load Error: {str(e)}")
            return []

    def clean_data(self):
        if self.df is None: return
        
        # 1. Attempt to convert non-numeric columns to numeric if they look like numbers
        for col in self.df.columns:
            if not pd.api.types.is_numeric_dtype(self.df[col]):
                # Skip if mostly empty
                if self.df[col].isna().all(): continue
                
                # Check if first few non-null items look like numbers after cleaning
                sample = self.df[col].dropna().head(10).astype(str)
                # Keep only digits, dots, and minus signs
                cleaned_sample = sample.str.replace(r'[^0-9.\-]', '', regex=True)
                
                try:
                    if not cleaned_sample.empty and cleaned_sample.str.len().gt(0).any():
                        # Validate that it can be numeric
                        pd.to_numeric(cleaned_sample, errors='raise')
                        # Apply to full column
                        self.df[col] = pd.to_numeric(self.df[col].astype(str).str.replace(r'[^0-9.\-]', '', regex=True), errors='coerce')
                except:
                    pass




        # 2. Fill missing values
        for col in self.df.columns:
            if pd.api.types.is_numeric_dtype(self.df[col]):
                self.df[col] = self.df[col].fillna(self.df[col].median() if not self.df[col].isna().all() else 0)
            else:
                self.df[col] = self.df[col].fillna('Unknown')
        
        # 3. Update cached column lists
        self.num_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        self.all_cols = self.df.columns.tolist()

    def get_stats(self):
        if self.df is None: return None
        if not self.num_cols:
            return pd.DataFrame({"Metric": ["Note"], "Value": ["No numeric columns detected for statistical analysis."]})
        return self.df[self.num_cols].describe().round(2)



    def get_real_col(self, target_col):
        if self.df is None: return None
        for actual_col in self.df.columns:
            if actual_col.lower() == target_col.lower():
                return actual_col
        return None

    def apply_ai_filter(self, query):
        if self.df is None: return "❌ Load dataset first"
        self.filtered_df = self.df.copy()
        q = query.lower()
        try:
            if any(term in q for term in ["remove missing", "drop missing", "clean"]):
                self.filtered_df = self.filtered_df.dropna()
            
            patterns = [
                (r"([\w\s]+?)\s*(?:is\s+)?(?:more\s+than|>|greater\s+than)\s*(\d+\.?\d*)", ">"),
                (r"([\w\s]+?)\s*(?:is\s+)?(?:less\s+than|<|smaller\s+than)\s*(\d+\.?\d*)", "<"),
                (r"([\w\s]+?)\s*(?:is\s+)?(?:equal\s+to|=)\s*(\d+\.?\d*)", "=="),
            ]

            for pattern, op in patterns:
                match = re.search(pattern, q)
                if match:
                    col_name, val = match.groups()
                    actual_col = self.get_real_col(col_name.strip())
                    if actual_col:
                        if op == ">": self.filtered_df = self.filtered_df[self.filtered_df[actual_col] > float(val)]
                        elif op == "<": self.filtered_df = self.filtered_df[self.filtered_df[actual_col] < float(val)]
                        elif op == "==": self.filtered_df = self.filtered_df[self.filtered_df[actual_col] == float(val)]

            return self.filtered_df.head(10).to_dict(orient="records")
        except Exception as e:
            return f"❌ Error interpreting query: {str(e)}"

    def run_ml(self, target_col):
        if self.df is None: return {"error": "❌ No data loaded. Please upload a dataset first."}
        if self.filtered_df is None: self.filtered_df = self.df.copy()
        if not target_col or target_col not in self.df.columns:
            return {"error": f"❌ '{target_col}' is not a valid column for prediction."}

        try:
            from sklearn.model_selection import train_test_split
            from sklearn.linear_model import LinearRegression, LogisticRegression
            from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
            from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
            from sklearn.cluster import KMeans
            from sklearn.metrics import r2_score, accuracy_score, mean_squared_error
            from sklearn.preprocessing import LabelEncoder
            import numpy as np

            # Prepare data
            data = self.df.dropna(subset=[target_col])
            if len(data) < 10: return {"error": "❌ Insufficient data for training (min 10 rows required)."}

            # Features: use all numeric columns except target
            X = data.select_dtypes(include=[np.number])
            if target_col in X.columns:
                X = X.drop(columns=[target_col])
            
            if X.empty:
                return {"error": "❌ No numeric feature columns found to use as predictors."}
            
            y = data[target_col]

            # Determine task type
            is_numeric_target = pd.api.types.is_numeric_dtype(y)
            unique_count = y.nunique()
            # If target is non-numeric or has very few unique values compared to total rows -> Classification
            is_classification = not is_numeric_target or (unique_count < 20 and unique_count / len(y) < 0.2)

            comparison = []
            models_to_test = []
            metric_name = ""

            if is_classification:
                le = LabelEncoder()
                y_transformed = le.fit_transform(y.astype(str))
                metric_name = "Accuracy"
                models_to_test = [
                    ("Logistic Regression", LogisticRegression(max_iter=1000)),
                    ("Decision Tree", DecisionTreeClassifier()),
                    ("Random Forest", RandomForestClassifier(n_estimators=100))
                ]
                X_train, X_test, y_train, y_test = train_test_split(X, y_transformed, test_size=0.2, random_state=42)
            else:
                metric_name = "R2 Score"
                models_to_test = [
                    ("Linear Regression", LinearRegression()),
                    ("Decision Tree", DecisionTreeRegressor()),
                    ("Random Forest", RandomForestRegressor(n_estimators=100))
                ]
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # Evaluate each model
            trained_models = {}
            for name, model in models_to_test:
                model.fit(X_train, y_train)
                trained_models[name] = model
                preds = model.predict(X_test)
                score = accuracy_score(y_test, preds) if is_classification else r2_score(y_test, preds)
                comparison.append({"model": name, "score": round(float(score), 4)})

            # Rank models and find winner
            comparison.sort(key=lambda x: x["score"], reverse=True)
            winner = comparison[0]
            
            # Use best model for plot data
            best_model = trained_models[winner["model"]]
            final_preds = best_model.predict(X_test)
            
            plot_data = []
            y_test_list = y_test.tolist() if not isinstance(y_test, np.ndarray) else y_test
            final_preds_list = final_preds.tolist() if not isinstance(final_preds, np.ndarray) else final_preds
            
            for i in range(min(50, len(y_test_list))):
                plot_data.append({
                    "actual": float(y_test_list[i]), 
                    "predicted": float(final_preds_list[i])
                })

            # Add K-Means as requested (unsupervised analysis)
            kmeans = KMeans(n_clusters=min(len(X), 4), n_init=10)
            kmeans_labels = kmeans.fit_predict(X)

            # Generate AI Decision Maker advice
            decision_advice = f"The data for {target_col} shows a clear pattern that we can use to make better decisions. We recommend focusing on the most important columns found in your data to improve your future results. By understanding these trends, you can proactively manage your processes and achieve better outcomes in the coming months."
            if self.model:
                try:
                    advice_prompt = (
                        f"As a helpful business assistant, look at these results for predicting '{target_col}'. "
                        f"The model {winner['model']} is {winner['score']:.2f} accurate. "
                        f"Write a simple, friendly paragraph (3-4 sentences) for a non-technical person. "
                        f"Explain what the business should actually DO next to improve based on this result. "
                        "Use plain, simple English. Do not use markdown, bold, or complex math terms."
                    )
                    res = self.model.generate_content(advice_prompt)
                    if res.text:
                        decision_advice = res.text.strip()
                except:
                    pass

            # Generate enriched narrative description
            narrative = f"Our automated system tested several different models and found that <b>{winner['model']}</b> is the best choice for predicting <b>{target_col}</b>. "
            if self.model:
                try:
                    narrative_prompt = (
                        f"Explain in one simple paragraph (3-4 sentences) why we chose the model '{winner['model']}' to predict '{target_col}'. "
                        f"The model's performance score is {winner['score']:.4f}. "
                        "Tell the user what this means for their data in simple, everyday English. "
                        "Avoid technical jargon like 'R2' or 'Regression'. "
                        "Do not use markdown, but you can use <b> tags for names of columns or models."
                    )
                    res = self.model.generate_content(narrative_prompt)
                    if res.text:
                        narrative = res.text.strip()
                except:
                    narrative += f"This model was chosen because it was the most accurate at finding the connection between your different data columns. High accuracy means you can trust these results to help guide your next steps. The system looked at all available information to ensure we gave you the most reliable calculation possible."

            self.ml_results = {
                "task": "Classification" if is_classification else "Regression",
                "target": target_col,
                "winner": winner,
                "metric": metric_name,
                "comparison": comparison,
                "plot_data": plot_data,
                "unsupervised": f"Clustering (K-Means) identified {len(np.unique(kmeans_labels))} distinct groups in your data.",
                "description": narrative,
                "decision_adviser": decision_advice,
                "features": list(X.columns)
            }
            return self.ml_results




        except Exception as e:
            return {"error": f"❌ ML Error: {str(e)}"}


    def analyze_chart_with_ai(self, chart_type, x_col, y_col, data):
        # 1. Try AI first
        if self.model:
            try:
                data_summary = data[:10] if isinstance(data, list) else []
                prompt = (
                    f"Analyze this {chart_type} chart. "
                    f"X-axis: {x_col}, Y-axis: {y_col if y_col else 'Frequency'}. "
                    f"Sample Data: {data_summary}. "
                    "Provide a detailed descriptive paragraph (3-5 sentences) explaining what the chart shows. "
                    "1. Start by stating exactly what the visual represents. "
                    "2. Highlight statistical extremes (max/min), and any notable patterns. "
                    "3. Conclude with the business implication or insight. "
                    "Write as a continuous paragraph. Do not use markdown, bold tags, or bullet points."
                )
                print(f"DEBUG: Calling Gemini for {chart_type}...")
                response = self.model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                print(f"Gemini Error (Falling back to rules): {str(e)}")

        # 2. Rule-Based Descriptive Fallback (Paragraph format)
        try:
            desc = f"This {chart_type} chart displays the data for {x_col}"
            if y_col: desc += f" in relation to {y_col}"
            desc += ". "
            
            if chart_type in ["Histogram", "Pie"]:
                # High-level stats for 1D
                vals = [d.get("value", 0) for d in data]
                names = [d.get("name", "Unknown") for d in data]
                if vals:
                    idx_max = vals.index(max(vals))
                    idx_min = vals.index(min(vals))
                    desc += f"The highest frequency is observed at '{names[idx_max]}', while the lowest is at '{names[idx_min]}'. "
                    desc += f"This suggests that {names[idx_max]} represents the dominant category or range in the dataset. "
            
            elif chart_type == "Heatmap":
                # Heatmap stats
                pos_corrs = [d.get("value", 0) for d in data if d.get("value", 0) > 0.5 and d.get("x") != d.get("y")]
                neg_corrs = [d.get("value", 0) for d in data if d.get("value", 0) < -0.5]
                desc += "The correlation matrix reveals the linear relationships between all numeric variables. "
                if pos_corrs:
                    desc += f"Highly positive correlations (>{max(pos_corrs) if pos_corrs else 0.5}) indicate variables that move together. "
                if neg_corrs:
                    desc += "Notable negative correlations highlight variables that move in opposite directions. "
                desc += "Identifying these relationships is critical for feature engineering and understanding the key levers that drive your metrics."
            
            elif chart_type in ["Scatter", "Line"]:

                # Relationship stats
                x_vals = [d.get(x_col, 0) for d in data]
                y_vals = [d.get(y_col, 0) for d in data]
                if x_vals and y_vals:
                    max_x = max(x_vals)
                    max_y = y_vals[x_vals.index(max_x)]
                    min_x = min(x_vals)
                    min_y = y_vals[x_vals.index(min_x)]
                    desc += f"The data ranges from a minimum {x_col} value of {min_x} to a maximum of {max_x}. "
                    desc += f"At the highest {x_col}, the {y_col} value is {max_y}. "
                    desc += f"The overall pattern shows how {y_col} fluctuates as {x_col} changes, highlighting potential dependencies between the two variables."
            
            desc += " Understanding these distributions helps in identifying key operational areas that require focus or optimization."
            return desc
        except:
            return f"Visualization of {x_col} and {y_col if y_col else 'frequency'}."


    def get_auto_charts(self):
        if self.df is None: return []
        source_df = self.filtered_df if self.filtered_df is not None else self.df
        recommendations = []
        num_cols = self.num_cols
        cat_cols = [c for c in self.all_cols if c not in num_cols]

        if num_cols:
            col = num_cols[0]
            counts, bins = np.histogram(source_df[col].dropna(), bins=10)
            data = [{"name": f"{bins[i]:.1f}", "value": int(counts[i])} for i in range(len(counts))]
            recommendations.append({
                "type": "Histogram", "x": str(col), "data": data,
                "reason": self.analyze_chart_with_ai("Histogram", col, None, data) or f"Frequency distribution of {col}."
            })
        
        if len(num_cols) >= 2:
            x_col, y_col = num_cols[0], num_cols[1]
            sample_df = source_df.dropna(subset=[x_col, y_col]).head(100)
            data = [{str(x_col): float(row[x_col]), str(y_col): float(row[y_col])} for _, row in sample_df.iterrows()]
            recommendations.append({
                "type": "Scatter", "x": str(x_col), "y": str(y_col), "data": data,
                "reason": self.analyze_chart_with_ai("Scatter", x_col, y_col, data) or f"Correlation between {x_col} and {y_col}."
            })

            line_df = source_df.dropna(subset=[x_col, y_col]).sort_values(by=x_col).head(100)
            data = [{str(x_col): float(row[x_col]), str(y_col): float(row[y_col])} for _, row in line_df.iterrows()]
            recommendations.append({
                "type": "Line", "x": str(x_col), "y": str(y_col), "data": data,
                "reason": self.analyze_chart_with_ai("Line", x_col, y_col, data) or f"Trend of {y_col} across {x_col}."
            })

        if len(num_cols) >= 2:
            # Add Heatmap for correlations

            corr = source_df[num_cols].corr().fillna(0)
            data = []
            for i, row_name in enumerate(corr.index):
                for j, col_name in enumerate(corr.columns):
                    data.append({"x": str(row_name), "y": str(col_name), "value": round(float(corr.iloc[i, j]), 2)})
            
            recommendations.append({
                "type": "Heatmap", 
                "columns": [str(c) for c in corr.columns],
                "data": data,
                "reason": self.analyze_chart_with_ai("Heatmap", "Correlation Matrix", None, data)
            })

        for col in cat_cols[:1]:
            counts = source_df[col].value_counts().head(8)
            if not counts.empty:
                data = [{"name": str(name), "value": int(val)} for name, val in counts.items()]
                recommendations.append({
                    "type": "Pie", "x": str(col), "data": data,
                    "reason": self.analyze_chart_with_ai("Pie", col, None, data) or f"Category breakdown for {col}."
                })
            
        return recommendations


app = FastAPI()
analyst = DataAnalyst()
drive_service = GoogleDriveService()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        print(f"DEBUG: Receiving file: {file.filename}")
        if not os.path.exists("uploads"): 
            os.makedirs("uploads")
            print("DEBUG: Created uploads directory")
            
        file_path = os.path.join("uploads", file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"DEBUG: File saved to {file_path}")
        
        preview = analyst.load_data(file_path)
        print("DEBUG: Data loaded successfully")
        
        charts = analyst.get_auto_charts()
        print(f"DEBUG: Generated {len(charts)} auto charts")
        
        return {"message": "Success", "preview": preview, "columns": analyst.all_cols, "auto_charts": charts}
    except Exception as e:
        error_msg = f"Upload error: {str(e)}"
        print(f"DEBUG: {error_msg}")
        return {"message": "Error", "detail": error_msg}


@app.get("/filter")
async def filter_data(query: str):
    return {"result": analyst.apply_ai_filter(query)}

@app.get("/ml")
async def run_ml_prediction(target: str):
    return {"result": analyst.run_ml(target)}

@app.get("/auto_charts")
async def get_charts():
    return {"auto_charts": analyst.get_auto_charts(), "charts": analyst.get_auto_charts()}

@app.get("/export_csv")
async def export_csv():
    if analyst.df is None:
        return {"message": "Error", "detail": "No data loaded"}
    
    try:
        print("DEBUG: Export report triggered")
        path = "uploads/exported_data.csv" # Use a distinct path if needed, or overwrite
        os.makedirs("uploads", exist_ok=True)
        data_to_export = analyst.filtered_df if analyst.filtered_df is not None else analyst.df
        data_to_export.to_csv(path, index=False)
        
        return FileResponse(path, filename="Exported_Data.csv", media_type="text/csv")
    except Exception as e:
        return {"message": "Error", "detail": str(e)}

@app.get("/export_report")
async def export_report():
    if analyst.df is None:
        return {"message": "Error", "detail": "No data loaded"}
    
    try:
        print("DEBUG: Export report triggered")
        path = "uploads/report.pdf"
        os.makedirs("uploads", exist_ok=True)
        stats = analyst.get_stats()
        ml_results = analyst.ml_results
        ml_text = ml_results.get("description", "No ML analysis performed.") if ml_results else "No ML analysis performed."

        charts = analyst.get_auto_charts()
        
        print(f"DEBUG: Generating PDF with {len(charts)} charts")
        reporting.create_pdf_report(path, stats, ml_text, charts, ml_results)
        print("DEBUG: PDF generated successfully")
        return FileResponse(path, filename="Analysis_Report.pdf", media_type="application/pdf")
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(f"DEBUG: Export error: {error_msg}")
        return {"message": "Error", "detail": str(e), "traceback": error_msg}


@app.get("/session_state")

async def get_state():
    return {
        "active": analyst.df is not None,
        "preview": [],
        "columns": analyst.all_cols,
        "num_cols": analyst.num_cols,
        "ml_results": analyst.ml_results,
        "auto_charts": analyst.get_auto_charts()
    }

# Google Drive Routes
@app.get("/drive/status")
async def drive_status():
    return {"authenticated": drive_service.is_authenticated()}

@app.post("/drive/auth")
async def drive_auth():
    try:
        drive_service.authenticate()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/drive/files")
async def drive_files():
    return drive_service.list_files()

@app.get("/drive/download/{file_id}")
async def drive_download(file_id: str):
    try:
        print(f"DEBUG: Drive download triggered for ID: {file_id}")
        if not os.path.exists("uploads"): 
            os.makedirs("uploads")
            print("DEBUG: Created uploads directory")
            
        file_info = drive_service.get_file_info(file_id)
        if not file_info.get('success'):
            print(f"DEBUG: File info failed: {file_info.get('error')}")
            return {"message": "Error", "detail": "File not found or access denied"}
        
        file_path = os.path.join("uploads", file_info['file']['name'])
        print(f"DEBUG: Downloading to {file_path}")
        download_result = drive_service.download_file(file_id, file_path)
        
        if download_result.get('success'):
            print("DEBUG: File downloaded successfully")
            preview = analyst.load_data(file_path)
            print("DEBUG: Data loaded successfully")
            charts = analyst.get_auto_charts()
            print(f"DEBUG: Generated {len(charts)} auto charts")
            return {"message": "Success", "preview": preview, "columns": analyst.all_cols, "auto_charts": charts}
        else:
            print(f"DEBUG: Download failed: {download_result.get('error')}")
            return {"message": "Error", "detail": download_result.get('error')}
    except Exception as e:
        error_msg = f"Drive download error: {str(e)}"
        print(f"DEBUG: {error_msg}")
        return {"message": "Error", "detail": error_msg}


@app.post("/drive/upload")
async def drive_upload(file: UploadFile = File(...)):
    try:
        print(f"DEBUG: Drive upload receiving file: {file.filename}")
        if not os.path.exists("uploads"): 
            os.makedirs("uploads")
            print("DEBUG: Created uploads directory")
            
        file_path = os.path.join("uploads", file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"DEBUG: File saved locally to {file_path}")
        
        print("DEBUG: Initiating Drive upload...")
        drive_result = drive_service.upload_file(file_path)
        print(f"DEBUG: Drive upload result success: {drive_result.get('success')}")
        
        preview = analyst.load_data(file_path)
        print("DEBUG: Local data loaded successfully")
        
        charts = analyst.get_auto_charts()
        print(f"DEBUG: Generated {len(charts)} auto charts")
        
        return {
            "message": "Success", 
            "preview": preview, 
            "columns": analyst.all_cols, 
            "auto_charts": charts,
            "drive_file": drive_result if drive_result.get('success') else None
        }
    except Exception as e:
        error_msg = f"Drive upload error: {str(e)}"
        print(f"DEBUG: {error_msg}")
        return {"message": "Error", "detail": error_msg}


@app.get("/")
def home(): return {"status": "Backend running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

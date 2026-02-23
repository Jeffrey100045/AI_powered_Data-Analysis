import gradio as gr
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import os
import re

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error, r2_score

from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

# ================= GLOBALS =================
df = None
filtered_df = None
num_cols = []
ml_results_text = ""
ml_plot_path = "ml_pred_vs_actual.png"
REPORT_FILE = "analysis_report.pdf"
pinned_charts = []  # List of paths to pinned chart images
chart_counter = 0

# ================= LOAD DATA =================
def load_file(file):
    global df, filtered_df, num_cols

    if file is None:
        return "❌ No file uploaded", None, gr.update(choices=[]), gr.update(choices=[]), gr.update(choices=[])

    if file.name.endswith(".csv"):
        df = pd.read_csv(file.name)
    else:
        df = pd.read_excel(file.name)

    filtered_df = df.copy()
    num_cols = df.select_dtypes(include=np.number).columns.tolist()
    all_cols = df.columns.tolist()

    return (
        "✅ File loaded successfully",
        filtered_df.head(),
        gr.update(choices=num_cols, value=None), # target_dropdown
        gr.update(choices=all_cols, value=all_cols[0] if all_cols else None), # x_axis
        gr.update(choices=all_cols, value=all_cols[1] if len(all_cols)>1 else None) # y_axis
    )

# ================= AI QUERY FILTER =================
def get_real_col(target_col):
    """Finds the actual column name in the dataframe (case-insensitive)."""
    if df is None: return None
    for actual_col in df.columns:
        if actual_col.lower() == target_col.lower():
            return actual_col
    return None

def ai_query_filter(query):
    global df, filtered_df

    if df is None:
        return "❌ Load dataset first", None

    filtered_df = df.copy()
    q = query.lower()

    try:
        # Pre-processing
        if "remove missing" in q or "drop missing" in q:
            filtered_df = filtered_df.dropna()

        # Regex for filtering patterns
        # Pattern 1: col > val
        match = re.search(r"([\w\s]+)\s*>\s*(\d+\.?\d*)", q)
        if match:
            col_name, val = match.groups()
            actual_col = get_real_col(col_name.strip())
            if actual_col:
                filtered_df = filtered_df[filtered_df[actual_col] > float(val)]
            else:
                return f"❌ Column '{col_name.strip()}' not found", None

        # Pattern 2: col < val
        match = re.search(r"([\w\s]+)\s*<\s*(\d+\.?\d*)", q)
        if match:
            col_name, val = match.groups()
            actual_col = get_real_col(col_name.strip())
            if actual_col:
                filtered_df = filtered_df[filtered_df[actual_col] < float(val)]
            else:
                return f"❌ Column '{col_name.strip()}' not found", None

        # Pattern 3: col between low and high
        match = re.search(r"([\w\s]+)\s*between\s*(\d+\.?\d*)\s*and\s*(\d+\.?\d*)", q)
        if match:
            col_name, low, high = match.groups()
            actual_col = get_real_col(col_name.strip())
            if actual_col:
                filtered_df = filtered_df[
                    (filtered_df[actual_col] >= float(low)) &
                    (filtered_df[actual_col] <= float(high))
                ]
            else:
                return f"❌ Column '{col_name.strip()}' not found", None

        # Pattern 4: top N by col
        match = re.search(r"top\s*(\d+)\s*by\s*([\w\s]+)", q)
        if match:
            n, col_name = match.groups()
            actual_col = get_real_col(col_name.strip())
            if actual_col:
                filtered_df = filtered_df.sort_values(actual_col, ascending=False).head(int(n))
            else:
                return f"❌ Column '{col_name.strip()}' not found", None

        return "✅ AI filter applied successfully", filtered_df.head()

    except Exception as e:
        return f"❌ Error: {str(e)}", None

# ================= CHARTS =================
def generate_custom_chart(chart_type, x_axis, y_axis):
    if filtered_df is None:
        return None
    
    if not x_axis or (chart_type != "Histogram" and not y_axis):
        return None

    data = filtered_df

    try:
        if chart_type == "Histogram":
            fig = px.histogram(data, x=x_axis, title=f"Distribution of {x_axis}")
        elif chart_type == "Scatter":
            fig = px.scatter(data, x=x_axis, y=y_axis, title=f"{x_axis} vs {y_axis}")
        elif chart_type == "Line":
            fig = px.line(data, x=x_axis, y=y_axis, title=f"{y_axis} over {x_axis}")
        elif chart_type == "Bar":
            fig = px.bar(data, x=x_axis, y=y_axis, title=f"{y_axis} by {x_axis}")
        else:
            return None
        return fig
    except Exception:
        return None

def pin_chart_to_report(chart_type, x_axis, y_axis):
    global pinned_charts, chart_counter
    if filtered_df is None:
        return "❌ Load data first"
    
    if not x_axis:
        return "❌ Please select at least the X-Axis"
    if chart_type != "Histogram" and not y_axis:
        return "❌ Please select both X and Y axis for this chart type"

    fig = generate_custom_chart(chart_type, x_axis, y_axis)
    if fig is None:
        return "❌ Could not generate chart. Check if selected columns are valid."

    try:
        chart_counter += 1
        path = f"pinned_chart_{chart_counter}.png"
        fig.write_image(path, engine="kaleido")
        pinned_charts.append(path)
        return f"✅ Chart added to report ({len(pinned_charts)} pinned total)"
    except Exception as e:
        return f"❌ Error saving chart: {str(e)}"

# ================= STATISTICS =================
def generate_statistics():
    if filtered_df is None:
        return None
    return filtered_df[num_cols].describe().round(3).reset_index()

# ================= MACHINE LEARNING =================
def get_ml_explanation(r2):
    """Provides a plain-English explanation of the R2 score."""
    if r2 > 0.8:
        return "✨ Excellent Accuracy: The model is highly reliable. It explains almost all the variations in the data."
    elif r2 > 0.5:
        return "✅ Good Accuracy: The model captures the main trends well, though it has some minor errors."
    elif r2 > 0.2:
        return "⚠️ Moderate Accuracy: The model shows some relationship, but there is a lot of unexplained variation. Use with caution."
    else:
        return "❌ Low Accuracy: The data seems too random or complex for this simple model. The predictions may not be reliable."

def run_ml(target):
    global ml_results_text

    if filtered_df is None or target is None:
        return "❌ Load data and select target column", None

    if len(num_cols) < 2:
        return "❌ Need at least 2 numeric columns", None

    data = filtered_df.dropna()

    X = data[num_cols].drop(columns=[target])
    y = data[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    models = {
        "Linear Regression": LinearRegression(),
        "Decision Tree": DecisionTreeRegressor(max_depth=5, random_state=42)
    }

    best_model, best_preds = None, None
    best_r2 = -1e9
    best_name = ""

    for name, model in models.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        r2 = r2_score(y_test, preds)

        if r2 > best_r2:
            best_r2 = r2
            best_model = model
            best_preds = preds
            best_name = name

    mse = mean_squared_error(y_test, best_preds)
    explanation = get_ml_explanation(best_r2)

    # Simplified text for easier ReportLab parsing
    ml_results_text = f"""📊 Model Performance
- Best Model Found: {best_name}
- Accuracy Score (R2): {best_r2:.4f}
- Error Margin (MSE): {mse:.4f}

💡 What this means for you:
{explanation}

- Features Used: {', '.join(X.columns)}"""

    fig = px.scatter(
        x=y_test,
        y=best_preds,
        labels={"x": "Actual Values", "y": "Predicted Values"},
        title=f"Actual vs Predicted ({best_name})"
    )

    plt.figure(figsize=(6,4))
    plt.scatter(y_test, best_preds)
    plt.plot([y_test.min(), y_test.max()],
             [y_test.min(), y_test.max()], linestyle="--", color="red")
    plt.xlabel("Actual")
    plt.ylabel("Predicted")
    plt.title(f"Performance: {best_name}")
    plt.tight_layout()
    plt.savefig(ml_plot_path)
    plt.close()

    return ml_results_text, fig

# ================= REPORT =================
def format_to_reportlab_xml(text):
    """Converts plain text to ReportLab-safe XML with basic formatting."""
    if not text:
        return "Not available."
    
    # 1. Escape HTML special characters
    from xml.sax.saxutils import escape
    text = escape(text)
    
    # 2. Add formatting carefully
    # Bold the headers and specific sections
    text = text.replace("📊 Model Performance", "<b>📊 Model Performance</b>")
    text = text.replace("💡 What this means for you:", "<b>💡 What this means for you:</b>")
    
    # 3. Handle newlines
    text = text.replace("\n", "<br/>")
            
    return text

def generate_report():
    global pinned_charts
    if filtered_df is None:
        return "❌ Load dataset first", None

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(REPORT_FILE, pagesize=A4)
    story = []

    # Title
    story.append(Paragraph("Automated Data Analysis Report", styles["Title"]))
    story.append(Spacer(1, 12))

    # Statistics Section
    story.append(Paragraph("1. Statistical Overview", styles["Heading2"]))
    stats = filtered_df[num_cols].describe().round(3).reset_index()
    table_data = [stats.columns.tolist()] + stats.values.tolist()
    table = Table(table_data)
    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("ALIGN", (1,1), (-1,-1), "CENTER"),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold")
    ]))
    story.append(table)
    story.append(Spacer(1, 20))

    # ML Section
    story.append(Paragraph("2. Machine Learning Analysis", styles["Heading2"]))
    ml_body = format_to_reportlab_xml(ml_results_text)
    story.append(Paragraph(ml_body, styles["Normal"]))

    if os.path.exists(ml_plot_path):
        try:
            story.append(Spacer(1, 12))
            story.append(Image(ml_plot_path, width=400, height=250))
        except Exception:
            pass

    # Pinned Charts Section
    if pinned_charts:
        story.append(Spacer(1, 20))
        story.append(Paragraph("3. Selected Data Visualizations", styles["Heading2"]))
        for chart_img in pinned_charts:
            if os.path.exists(chart_img):
                try:
                    story.append(Spacer(1, 12))
                    story.append(Image(chart_img, width=450, height=280))
                except Exception as img_err:
                    story.append(Paragraph(f"<i>(Error loading chart: {img_err})</i>", styles["Normal"]))

    try:
        doc.build(story)
        return "✅ Report generated successfully with pinned charts", REPORT_FILE
    except Exception as e:
        return f"❌ PDF Generation Error: {str(e)}", None

# ================= UI =================
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 📊 Intelligent Data Analytics Pro")
    gr.Markdown("Transform your data into insights with AI-powered filtering and ML analysis.")

    with gr.Tab("📂 Data Center"):
        with gr.Row():
            file = gr.File(label="Upload Dataset (CSV/Excel)", scale=2)
            status = gr.Textbox(label="Status", interactive=False)
        preview = gr.Dataframe(label="Data Preview", interactive=False)
        target_dropdown = gr.Dropdown(label="Target column for Prediction (ML)")

    with gr.Tab("🤖 AI Smart Filter"):
        gr.Markdown("### Ask AI to filter your data")
        ai_input = gr.Textbox(
            label="Natural Language Query",
            placeholder="e.g. 'Cost > 100' or 'top 5 by Revenue' or 'drop missing'"
        )
        ai_btn = gr.Button("🔍 Apply Filter", variant="primary")
        ai_status = gr.Textbox(label="Process Log")
        ai_preview = gr.Dataframe(label="Filtered Results Preview")

        ai_btn.click(ai_query_filter, ai_input, [ai_status, ai_preview])

    with gr.Tab("📈 Visual Designer"):
        gr.Markdown("### Create and Pin Charts to your Report")
        with gr.Row():
            chart_type = gr.Dropdown(
                ["Histogram", "Scatter", "Line", "Bar"],
                value="Histogram",
                label="Chart Type"
            )
            x_axis = gr.Dropdown(label="X-Axis")
            y_axis = gr.Dropdown(label="Y-Axis")

        with gr.Row():
            chart_btn = gr.Button("✨ Generate Chart", variant="primary")
            pin_btn = gr.Button("📌 Add to Report", variant="secondary")

        chart_output = gr.Plot()
        pin_status = gr.Textbox(label="Pinning Status")

        chart_btn.click(generate_custom_chart, [chart_type, x_axis, y_axis], chart_output)
        pin_btn.click(pin_chart_to_report, [chart_type, x_axis, y_axis], pin_status)

    with gr.Tab("📊 Statistical Summary"):
        stats_btn = gr.Button("Calculate Stats")
        stats_df = gr.Dataframe()
        stats_btn.click(generate_statistics, outputs=stats_df)

    with gr.Tab("🤖 ML Predictions"):
        gr.Markdown("### Auto-Predictive Modeling")
        ml_btn = gr.Button("🚀 Run Best Model", variant="primary")
        ml_text = gr.Markdown(label="Insightful Results")
        ml_plot = gr.Plot()
        ml_btn.click(run_ml, target_dropdown, [ml_text, ml_plot])

    with gr.Tab("📄 Report Hub"):
        gr.Markdown("### Export Comprehensive PDF Report")
        rep_btn = gr.Button("💾 Generate Final PDF", variant="primary")
        rep_status = gr.Textbox(label="Export Status")
        rep_file = gr.File(label="Download Report")
        rep_btn.click(generate_report, outputs=[rep_status, rep_file])

    # Dynamic column updates
    file.change(load_file, file, [status, preview, target_dropdown, x_axis, y_axis])

demo.launch()

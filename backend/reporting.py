from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io
from xml.sax.saxutils import escape
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def format_to_reportlab_xml(text):
    if not text: return "Not available."
    try:
        text = str(text)
        # Escape for XML but then restore bold/italic/break tags for ReportLab Paragraphs
        text = escape(text)
        text = text.replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
        text = text.replace("&lt;i&gt;", "<i>").replace("&lt;/i&gt;", "</i>")
        text = text.replace("&lt;br/&gt;", "<br/>").replace("\n", "<br/>")
        
        # Handle some common high-unicode characters that might crash ReportLab
        text = text.encode("ascii", "xmlcharrefreplace").decode("ascii")

        # Highlight key sections
        text = text.replace("📊 Model Performance", "<b>📊 Model Performance</b>")
        text = text.replace("💡 What this means for you:", "<b>💡 What this means for you:</b>")
        return text
    except Exception as e:
        print(f"DEBUG: Formatting error: {e}")
        return "Error formatting analysis text."


def create_pdf_report(path, stats_df, ml_text, charts_data=None, ml_results=None):
    try:
        doc = SimpleDocTemplate(path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Title
        story.append(Paragraph("📊 Data Analysis Synthesis Report", styles["Title"]))
        story.append(Spacer(1, 12))

        # Stats
        story.append(Paragraph("1. Statistical Overview", styles["Heading2"]))
        
        if stats_df is not None and not stats_df.empty:
            # Ensure index is part of the table for context (mean, std, etc)
            stats_display = stats_df.reset_index()
            # Convert all values to string and round numbers for compactness
            table_data = [stats_display.columns.tolist()]
            for row in stats_display.values.tolist():
                formatted_row = []
                for item in row:
                    if isinstance(item, (int, float)):
                        formatted_row.append(f"{item:.2f}")
                    else:
                        formatted_row.append(str(item))
                table_data.append(formatted_row)
                
            table = Table(table_data)
            table.setStyle(TableStyle([
                ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
                ("BACKGROUND", (0,0), (-1,0), colors.whitesmoke),
                ("ALIGN", (0,0), (-1,-1), "CENTER"),
                ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                ("FONTSIZE", (0,0), (-1,-1), 6),
                ("BOTTOMPADDING", (0,0), (-1,-1), 2),
                ("TOPPADDING", (0,0), (-1,-1), 2),
            ]))
            story.append(table)
        else:
            story.append(Paragraph("No statistical data available.", styles["Normal"]))
            
        story.append(Spacer(1, 12))

        # Charts Section
        if charts_data:
            story.append(Paragraph("2. Visual Insights", styles["Heading2"]))
            for chart in charts_data:
                if chart and "data" in chart and chart["data"]:
                    try:
                        plt.figure(figsize=(6, 4))
                        if chart["type"] == "Histogram":
                            names = [str(d.get("name", "")) for d in chart["data"]]
                            values = [float(d.get("value", 0)) for d in chart["data"]]
                            plt.bar(names, values, color='skyblue')
                            plt.xticks(rotation=45, ha='right', fontsize=8)
                        elif chart["type"] == "Scatter":
                            x_col, y_col = chart.get("x"), chart.get("y")
                            if x_col and y_col:
                                x = [float(d.get(x_col, 0)) for d in chart["data"]]
                                y = [float(d.get(y_col, 0)) for d in chart["data"]]
                                plt.scatter(x, y, alpha=0.5, color='orange')
                        elif chart["type"] == "Bar":
                            names = [str(d.get("name", "")) for d in chart["data"]]
                            values = [float(d.get("value", 0)) for d in chart["data"]]
                            plt.bar(names, values, color='lightgreen')
                            plt.xticks(rotation=45, ha='right', fontsize=8)
                        elif chart["type"] == "Line":
                            x_col, y_col = chart.get("x"), chart.get("y")
                            if x_col and y_col:
                                x = [float(d.get(x_col, 0)) for d in chart["data"]]
                                y = [float(d.get(y_col, 0)) for d in chart["data"]]
                                plt.plot(x, y, color='purple', marker='o', markersize=4)
                                plt.xticks(rotation=45, ha='right', fontsize=8)
                        elif chart["type"] == "Pie":
                            names = [str(d.get("name", "")) for d in chart["data"]]
                            values = [float(d.get("value", 0)) for d in chart["data"]]
                            plt.pie(values, labels=names, autopct='%1.1f%%', startangle=140)
                            plt.axis('equal')
                        elif chart["type"] == "Heatmap":
                            # Render correlation heatmap
                            try:
                                import numpy as np
                                cols = chart.get("columns", [])
                                points = chart.get("data", [])
                                if cols and points:
                                    matrix = np.zeros((len(cols), len(cols)))
                                    col_to_idx = {col: i for i, col in enumerate(cols)}
                                    for p in points:
                                        if p["x"] in col_to_idx and p["y"] in col_to_idx:
                                            matrix[col_to_idx[p["x"]], col_to_idx[p["y"]]] = p["value"]
                                    
                                    im = plt.imshow(matrix, cmap='RdBu', vmin=-1, vmax=1)
                                    plt.colorbar(im)
                                    plt.xticks(range(len(cols)), cols, rotation=90, fontsize=6)
                                    plt.yticks(range(len(cols)), cols, fontsize=6)
                                    # Add text values to heatmap
                                    for i in range(len(cols)):
                                        for j in range(len(cols)):
                                            plt.text(j, i, f"{matrix[i, j]:.2f}", ha="center", va="center", color="black", fontsize=5)
                                    plt.title("Correlation Heatmap", fontsize=10)
                            except Exception as e:
                                print(f"DEBUG: Heatmap error: {e}")
                        
                        plt.title(f"{chart.get('type', 'Chart')} for {chart.get('x', 'Data')}", fontsize=10)
                        plt.tight_layout(pad=1.0)
                        
                        img_data = io.BytesIO()
                        plt.savefig(img_data, format='png', dpi=72)
                        plt.close()

                        img_data.seek(0)
                        report_img = Image(img_data, width=400, height=250)
                        story.append(report_img)

                        
                        # Trend Message Box
                        reason_text = format_to_reportlab_xml(chart.get("reason", "Automatic visualization."))
                        trend_box = Table([[Paragraph(f"<b>📈 Trend Insight:</b><br/>{reason_text}", styles['Normal'])]], colWidths=[400])
                        trend_box.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
                            ('BORDER', (0, 0), (-1, -1), 1, colors.lightgrey),
                            ('BOX', (0, 0), (-1, -1), 1, colors.lightgrey),
                            ('TOPPADDING', (0, 0), (-1, -1), 8),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                            ('LEFTPADDING', (0, 0), (-1, -1), 12),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                        ]))
                        story.append(trend_box)
                        story.append(Spacer(1, 15))


                    except Exception as e:
                        print(f"Error generating chart {chart.get('type')} for report: {str(e)}")
                        import traceback
                        print(traceback.format_exc())
                        story.append(Paragraph(f"Could not render {chart.get('type')} chart.", styles["Normal"]))


        # 3. Machine Learning Analysis
        story.append(Paragraph("3. Machine Learning Analysis", styles["Heading2"]))
        
        if ml_results and "winner" in ml_results:
            # Results & Insights Header
            story.append(Paragraph("<b>Results & Insights</b>", styles["Normal"]))
            story.append(Spacer(1, 10))

            # Metric Cards (Simulated via Table)
            metric_val = ml_results.get("winner", {}).get("score", 0.0)
            metric_name = ml_results.get("metric", "Score")
            task_type = ml_results.get("task", "ML")
            short_metric = "R2" if task_type == "Regression" else "Acc"
            model_name = ml_results.get("winner", {}).get("model", "Unknown")

            metrics_data = [
                [Paragraph(f"<font size='8' color='grey'>{metric_name} ({short_metric})</font><br/><b><font size='14'>{metric_val:.4f}</font></b>", styles['Normal']),
                 Paragraph(f"<font size='8' color='grey'>Model Used</font><br/><b><font size='12'>{model_name}</font></b>", styles['Normal'])]
            ]
            
            metrics_table = Table(metrics_data, colWidths=[220, 220])
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8F9FA")),
                ('BORDER', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('LEFTPADDING', (0,0), (-1,-1), 15),
            ]))
            story.append(metrics_table)
            story.append(Spacer(1, 15))


            # Narrative Description
            narrative = format_to_reportlab_xml(ml_results.get("description", ""))
            if narrative:
                story.append(Paragraph(narrative, styles["Normal"]))
                story.append(Spacer(1, 15))

            # Decision Advisor Box (Orange themed)
            advisor_text = format_to_reportlab_xml(ml_results.get("decision_adviser", "No specific recommendations available."))
            advisor_box = Table([[Paragraph(f"<b>🎯 Decision Adviser:</b><br/>{advisor_text}", styles['Normal'])]], colWidths=[440])
            advisor_box.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FFF8F0")), # Very light orange
                ('BORDER', (0, 0), (-1, -1), 1, colors.HexColor("#FF9800")), # Orange border
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#FF9800")),
                ('LEFTPADDING', (0, 0), (-1, -1), 15),
                ('RIGHTPADDING', (0, 0), (-1, -1), 15),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            story.append(advisor_box)
            story.append(Spacer(1, 20))

            # Model Performance Benchmarks (Cleaner)
            story.append(Paragraph("<b>Model Performance Benchmarks</b>", styles["Normal"]))
            story.append(Spacer(1, 8))
            comparison_data = [["ALGORITHM", "SCORE", "STATUS"]]
            for res in ml_results.get("comparison", []):
                status = "WINNER" if res["model"] == model_name else "-"
                comparison_data.append([res["model"], f"{res['score']:.4f}", status])
            
            comp_table = Table(comparison_data, colWidths=[240, 100, 100])
            comp_table.setStyle(TableStyle([
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.grey),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('LINEBELOW', (0, 0), (-1, 0), 1, colors.lightgrey),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('ALIGN', (2, 0), (2, -1), 'CENTER'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(comp_table)
            story.append(Spacer(1, 25))




        # Actual vs Predicted Plot
        if ml_results and "plot_data" in ml_results:
            try:
                data = ml_results["plot_data"]
                if data:
                    plt.figure(figsize=(6, 4))
                    actual = [d["actual"] for d in data]
                    predicted = [d["predicted"] for d in data]
                    plt.scatter(actual, predicted, alpha=0.6, color='blue')
                    # Add diagonal line
                    lims = [min(min(actual), min(predicted)), max(max(actual), max(predicted))]
                    plt.plot(lims, lims, 'r--', alpha=0.75, zorder=0)
                    plt.xlabel("Actual", fontsize=8)
                    plt.ylabel("Predicted", fontsize=8)
                    plt.title("Actual vs Predicted Values", fontsize=10)
                    plt.tight_layout(pad=1.0)

                    img_data = io.BytesIO()
                    plt.savefig(img_data, format='png', dpi=72)
                    plt.close()

                    img_data.seek(0)
                    story.append(Image(img_data, width=350, height=220))
                    story.append(Spacer(1, 15))

                    # Data Configuration Box below Chart
                    features_str = ", ".join(ml_results.get("features", ["Numeric columns"]))
                    target_str = ml_results.get("target", "Unknown")
                    
                    config_content = [
                        [Paragraph("<b>📊 Data Usage Analysis</b>", styles['Normal'])],
                        [Paragraph(f"Target Predictive Goal: {target_str}", styles['Normal'])],
                        [Paragraph(f"Input Features: {features_str}", styles['Normal'])]
                    ]
                    
                    config_box = Table(config_content, colWidths=[440])
                    config_box.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F0F4FF")),
                        ('BORDER', (0, 0), (-1, -1), 1, colors.HexColor("#C3DAFE")),
                        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#C3DAFE")),
                        ('TOPPADDING', (0, 0), (-1, -1), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                        ('LEFTPADDING', (0, 0), (-1, -1), 15),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
                    ]))
                    story.append(config_box)
                    story.append(Spacer(1, 15))

            except Exception as e:
                print(f"Error rendering ML plot in report: {str(e)}")

        doc.build(story)

    except Exception as e:
        import traceback
        print(f"FATAL PDF ERROR: {str(e)}")
        print(traceback.format_exc())
        raise e

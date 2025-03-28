
import pandas as pd
from fpdf import FPDF
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime

class ReportGenerator:
    def generate(self, data, report_type):
        if report_type == 'pdf':
            return self._generate_pdf(data)
        elif report_type == 'csv':
            return self._generate_csv(data)
        elif report_type == 'json':
            return self._generate_json(data)
    
    def _generate_pdf(self, data):
        df = pd.DataFrame(data)
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Crowd Analysis Report', ln=True, align='C')
        
        # Summary statistics
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f"Report Generated: {datetime.now()}", ln=True)
        pdf.cell(0, 10, f"Total Records: {len(df)}", ln=True)
        pdf.cell(0, 10, f"Average Count: {df['count'].mean():.2f}", ln=True)
        pdf.cell(0, 10, f"Max Count: {df['count'].max()}", ln=True)
        
        # Generate and save plots
        self._add_plots_to_pdf(df, pdf)
        
        filename = f"reports/crowd_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf.output(filename)
        return filename
    
    def _generate_csv(self, data):
        df = pd.DataFrame(data)
        filename = f"reports/crowd_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False)
        return filename
    
    def _generate_json(self, data):
        filename = f"reports/crowd_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(data, f)
        return filename
    
    def _add_plots_to_pdf(self, df, pdf):
        # Time series plot of crowd count
        fig = px.line(df, x='timestamp', y='count', title='Crowd Count Over Time')
        plot_path = f"reports/temp_plot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        fig.write_image(plot_path)
        pdf.image(plot_path, x=10, y=None, w=190)
        
        # Density heatmap
        fig = go.Figure(data=go.Heatmap(
            z=df['density'].values.reshape(-1, 1),
            x=df['timestamp'],
            colorscale='Viridis'
        ))
        fig.update_layout(title='Crowd Density Heatmap')
        plot_path = f"reports/temp_heatmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        fig.write_image(plot_path)
        pdf.image(plot_path, x=10, y=None, w=190)
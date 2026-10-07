from fpdf import FPDF
from datetime import datetime
import os

def make_report(project, customer, title, inputs, results):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "SAMWATER - Calculation Report", ln=True, align="C")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, f"Date: {datetime.now():%Y-%m-%d %H:%M}", ln=True)
    pdf.cell(0, 8, f"Project: {project}   Customer: {customer}", ln=True)
    pdf.cell(0, 8, f"Module: {title}", ln=True)
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Inputs", ln=True)
    pdf.set_font("Helvetica", "", 10)
    for k, v in inputs.items():
        pdf.cell(0, 6, f"  {k} = {v}", ln=True)
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Results", ln=True)
    pdf.set_font("Helvetica", "", 10)
    for k, v in results.items():
        pdf.cell(0, 6, f"  {k} = {v:.6g}", ln=True)
    out = os.path.join(os.path.expanduser("~"), "Documents",
                       f"SAMWATER_{project or 'report'}.pdf")
    pdf.output(out)
    return out

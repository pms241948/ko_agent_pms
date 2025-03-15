from fpdf import FPDF
from app.models.customer import CustomerCreditInfo

def generate_credit_report(customer_data: CustomerCreditInfo):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"{customer_data.name}님의 신용 분석 보고서", ln=True, align='C')
    pdf.ln(10)

    for key, value in customer_data.dict().items():
        pdf.cell(200, 10, f"{key}: {value}", ln=True)

    filename = f"{customer_data.name}_credit_report.pdf"
    pdf.output(filename)
    
    return filename
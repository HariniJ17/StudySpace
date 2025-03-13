from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import datetime

app = Flask(__name__)

@app.route('/')
def payment_form():
    return render_template('index.html')

@app.route('/generate_invoice', methods=['POST'])
def generate_invoice():
    # Get form data
    name = request.form['name']
    email = request.form['email']
    amount = float(request.form['amount'])
    tax = amount * 0.18  # 18% GST
    total_amount = amount + tax
    date = datetime.datetime.now().strftime("%d/%m/%Y")
    invoice_number = f"INV-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Create PDF buffer
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle("Invoice")

    # Invoice Header
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(200, 750, "INVOICE")
    
    # Company Details
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, 720, "STUDY SPACE")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, 705, "Study space company ")
    pdf.drawString(50, 690, "Pondicherry - 605004, India")

    # Invoice Details
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(400, 720, f"Invoice Number: {invoice_number}")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(400, 705, f"Date: {date}")
    pdf.drawString(400, 690, "GST Number: 06AADCU4187E1ZB")

    # Customer Details
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, 660, "Bill To:")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, 645, f"{name}")
    pdf.drawString(50, 630, f"{email}")

    # Table Header
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, 600, "Item")
    pdf.drawString(300, 600, "Quantity")
    pdf.drawString(400, 600, "Unit Price")
    pdf.drawString(500, 600, "Amount")
    
    pdf.line(50, 595, 550, 595)  # Table Line

    # Invoice Items
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, 570, "Front-end Development Intern")
    pdf.drawString(310, 570, "1")
    pdf.drawString(410, 570, f"₹{amount:.2f}")
    pdf.drawString(510, 570, f"₹{amount:.2f}")

    pdf.line(50, 560, 550, 560)  # Table Line

    # Pricing Details
    pdf.drawString(400, 540, "Subtotal:")
    pdf.drawString(500, 540, f"₹{amount:.2f}")

    pdf.drawString(400, 520, "Tax (18% GST):")
    pdf.drawString(500, 520, f"₹{tax:.2f}")

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(400, 500, "Total:")
    pdf.drawString(500, 500, f"₹{total_amount:.2f}")

    # Footer Notes
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, 470, "This invoice is computer-generated and does not require a signature.")
    pdf.drawString(50, 450, "For support, contact: support@studyspace.com")

    # Save PDF
    pdf.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, attachment_filename="invoice.pdf", mimetype="application/pdf")

if __name__ == '__main__':
    app.run(debug=True)

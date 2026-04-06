from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import base64
import os
from fpdf import FPDF
from datetime import datetime
import traceback

app = Flask(__name__)
CORS(app)

class PDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            self.set_font('Helvetica', 'B', 16)
            self.set_text_color(40, 40, 100)
            self.cell(0, 10, 'PROFESSIONAL RESUME', 0, 1, 'C')
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    try:
        data = request.json
        
        if not data.get('name') or not data.get('name').strip():
            return jsonify({'success': False, 'errors': ['Имя обязательно']}), 400
        if not data.get('surname') or not data.get('surname').strip():
            return jsonify({'success': False, 'errors': ['Фамилия обязательна']}), 400
        
        pdf = PDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=25)
        
        # Имя и фамилия
        pdf.set_font('Helvetica', 'B', 18)
        pdf.cell(0, 10, f"{data['name']} {data['surname']}", 0, 1, 'L')
        pdf.ln(5)
        
        # Контакты
        if data.get('contact'):
            pdf.set_font('Helvetica', 'B', 12)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(0, 8, "CONTACT INFORMATION", 0, 1, 'L')
            pdf.set_font('Helvetica', '', 10)
            pdf.set_text_color(60, 60, 60)
            pdf.multi_cell(0, 6, data['contact'])
            pdf.ln(3)
        
        # Опыт работы
        if data.get('experience'):
            pdf.set_font('Helvetica', 'B', 12)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(0, 8, "WORK EXPERIENCE", 0, 1, 'L')
            pdf.set_font('Helvetica', '', 10)
            pdf.set_text_color(60, 60, 60)
            pdf.multi_cell(0, 6, data['experience'])
            pdf.ln(3)
        
        # Навыки
        if data.get('skills'):
            pdf.set_font('Helvetica', 'B', 12)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(0, 8, "SKILLS", 0, 1, 'L')
            pdf.set_font('Helvetica', '', 10)
            pdf.set_text_color(60, 60, 60)
            for skill in data['skills'].split(','):
                pdf.cell(5)
                pdf.cell(0, 6, f"- {skill.strip()}", 0, 1)
            pdf.ln(3)
        
        # Образование
        if data.get('education'):
            pdf.set_font('Helvetica', 'B', 12)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(0, 8, "EDUCATION", 0, 1, 'L')
            pdf.set_font('Helvetica', '', 10)
            pdf.set_text_color(60, 60, 60)
            pdf.multi_cell(0, 6, data['education'])
            pdf.ln(3)
        
        # Языки
        if data.get('languages'):
            pdf.set_font('Helvetica', 'B', 12)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(0, 8, "LANGUAGES", 0, 1, 'L')
            pdf.set_font('Helvetica', '', 10)
            pdf.set_text_color(60, 60, 60)
            for lang in data['languages'].split(','):
                pdf.cell(5)
                pdf.cell(0, 6, f"- {lang.strip()}", 0, 1)
        
        # Сохраняем PDF
        filename = f"resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf.output(filename)
        
        return send_file(filename, as_attachment=True, download_name="CV.pdf")
        
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'success': False, 'errors': [str(e)]}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
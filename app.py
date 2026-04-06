from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import base64
import os
from fpdf import FPDF
from datetime import datetime
import traceback
from io import BytesIO

app = Flask(__name__)
CORS(app)

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
        self.add_font('DejaVu', 'B', 'DejaVuSansCondensed-Bold.ttf', uni=True)
        
    def header(self):
        self.set_y(15)
        self.set_draw_color(102, 126, 234)
        self.set_line_width(2)
        self.line(20, 20, 190, 20)
        
    def footer(self):
        self.set_y(-20)
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.5)
        self.line(20, self.get_y(), 190, self.get_y())
        self.set_y(-15)
        self.set_font('DejaVu', '', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Создано с помощью CV Builder | Страница {self.page_no()}', 0, 0, 'C')

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
        pdf.set_auto_page_break(auto=True, margin=30)
        
        pdf.set_fill_color(245, 245, 250)
        pdf.rect(20, 20, 55, 270, 'F')
        
        if data.get('photo') and data['photo'].startswith('data:image'):
            try:
                img_data = base64.b64decode(data['photo'].split(',')[1])
                img_path = 'temp_photo.jpg'
                with open(img_path, 'wb') as f:
                    f.write(img_data)
                pdf.image(img_path, x=30, y=35, w=35, h=35)
                pdf.set_draw_color(102, 126, 234)
                pdf.set_line_width(1.5)
                pdf.ellipse(30, 35, 35, 35)
                os.remove(img_path)
            except:
                pass
        
        pdf.set_y(85)
        pdf.set_font('DejaVu', 'B', 14)
        pdf.set_text_color(60, 60, 80)
        pdf.set_x(25)
        pdf.cell(45, 8, f"{data.get('name', '')}", 0, 1, 'C')
        pdf.set_x(25)
        pdf.cell(45, 8, f"{data.get('surname', '')}", 0, 1, 'C')
        
        if data.get('contact'):
            pdf.set_y(110)
            pdf.set_font('DejaVu', 'B', 9)
            pdf.set_text_color(80, 80, 100)
            pdf.set_x(25)
            pdf.cell(45, 6, "КОНТАКТЫ", 0, 1, 'C')
            pdf.set_draw_color(102, 126, 234)
            pdf.set_line_width(0.5)
            pdf.line(30, pdf.get_y(), 65, pdf.get_y())
            pdf.ln(3)
            
            pdf.set_font('DejaVu', '', 8)
            pdf.set_text_color(80, 80, 80)
            contact_lines = data['contact'].split('\n')
            for line in contact_lines[:5]:
                pdf.set_x(25)
                pdf.multi_cell(45, 5, line[:40], 0, 'L')
                pdf.ln(1)
        
        if data.get('skills'):
            pdf.set_font('DejaVu', 'B', 9)
            pdf.set_text_color(80, 80, 100)
            pdf.set_x(25)
            pdf.cell(45, 6, "НАВЫКИ", 0, 1, 'C')
            pdf.set_draw_color(102, 126, 234)
            pdf.line(30, pdf.get_y(), 65, pdf.get_y())
            pdf.ln(3)
            
            pdf.set_font('DejaVu', '', 8)
            pdf.set_text_color(80, 80, 80)
            skills = [s.strip() for s in data['skills'].split(',') if s.strip()]
            for skill in skills[:8]:
                pdf.set_x(28)
                pdf.cell(3, 5, "▹", 0, 0)
                pdf.set_x(35)
                pdf.multi_cell(35, 5, skill[:30], 0, 'L')
                pdf.ln(1)
        
        if data.get('languages'):
            pdf.set_font('DejaVu', 'B', 9)
            pdf.set_text_color(80, 80, 100)
            pdf.set_x(25)
            pdf.cell(45, 6, "ЯЗЫКИ", 0, 1, 'C')
            pdf.set_draw_color(102, 126, 234)
            pdf.line(30, pdf.get_y(), 65, pdf.get_y())
            pdf.ln(3)
            
            pdf.set_font('DejaVu', '', 8)
            pdf.set_text_color(80, 80, 80)
            langs = [l.strip() for l in data['languages'].split(',') if l.strip()]
            for lang in langs[:5]:
                pdf.set_x(28)
                pdf.cell(3, 5, "▹", 0, 0)
                pdf.set_x(35)
                pdf.multi_cell(35, 5, lang[:25], 0, 'L')
                pdf.ln(1)
        
        pdf.set_fill_color(102, 126, 234)
        pdf.rect(85, 20, 105, 4, 'F')
        
        pdf.set_y(30)
        pdf.set_font('DejaVu', 'B', 24)
        pdf.set_text_color(50, 50, 70)
        pdf.set_x(90)
        pdf.cell(0, 12, "ПРОФЕССИОНАЛЬНОЕ", 0, 1, 'L')
        pdf.set_x(90)
        pdf.cell(0, 12, "РЕЗЮМЕ", 0, 1, 'L')
        
        pdf.set_draw_color(102, 126, 234)
        pdf.set_line_width(1)
        pdf.line(90, pdf.get_y() + 2, 190, pdf.get_y() + 2)
        pdf.ln(8)
        
        if data.get('experience'):
            pdf.set_font('DejaVu', 'B', 12)
            pdf.set_text_color(102, 126, 234)
            pdf.set_x(90)
            pdf.cell(0, 8, "💼 ОПЫТ РАБОТЫ", 0, 1, 'L')
            pdf.set_draw_color(102, 126, 234)
            pdf.set_line_width(0.5)
            pdf.line(90, pdf.get_y() + 2, 190, pdf.get_y() + 2)
            pdf.ln(4)
            
            pdf.set_font('DejaVu', '', 10)
            pdf.set_text_color(60, 60, 60)
            pdf.set_x(92)
            experience_text = data['experience']
            for line in experience_text.split('\n'):
                if line.strip():
                    pdf.set_x(92)
                    pdf.multi_cell(93, 6, line.strip(), 0, 'L')
                    pdf.ln(1)
            pdf.ln(4)
        
        if data.get('education'):
            pdf.set_font('DejaVu', 'B', 12)
            pdf.set_text_color(102, 126, 234)
            pdf.set_x(90)
            pdf.cell(0, 8, "🎓 ОБРАЗОВАНИЕ", 0, 1, 'L')
            pdf.set_draw_color(102, 126, 234)
            pdf.line(90, pdf.get_y() + 2, 190, pdf.get_y() + 2)
            pdf.ln(4)
            
            pdf.set_font('DejaVu', '', 10)
            pdf.set_text_color(60, 60, 60)
            pdf.set_x(92)
            education_text = data['education']
            for line in education_text.split('\n'):
                if line.strip():
                    pdf.set_x(92)
                    pdf.multi_cell(93, 6, line.strip(), 0, 'L')
                    pdf.ln(1)
            pdf.ln(4)
        
        if not data.get('experience') and not data.get('education'):
            pdf.set_font('DejaVu', '', 11)
            pdf.set_text_color(120, 120, 140)
            pdf.set_x(90)
            pdf.cell(0, 8, "Заполните информацию о вашем", 0, 1, 'L')
            pdf.set_x(90)
            pdf.cell(0, 8, "опыте работы и образовании", 0, 1, 'L')
            pdf.set_x(90)
            pdf.cell(0, 8, "чтобы сделать резюме полным", 0, 1, 'L')
        
        filename = f"resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf.output(filename)
        
        return send_file(filename, as_attachment=True, download_name="CV.pdf")
        
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'success': False, 'errors': [str(e)]}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

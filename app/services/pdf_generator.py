from fpdf import FPDF
import requests
from io import BytesIO
from PIL import Image
from datetime import datetime

from app.models import design as design_model

# --- NUEVA PALETA DE COLORES MÁS VIVOS ---
COLOR_PRIMARY = (46, 139, 87)    # Un verde mar más vivo
COLOR_SECONDARY = (238, 247, 235)  # Un verde muy claro para fondos
COLOR_TEXT = (50, 50, 50)           # Un gris oscuro en lugar de negro puro
COLOR_GRAY = (150, 150, 150)        # Gris para texto secundario

class PDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 15)
        self.set_text_color(*COLOR_PRIMARY)
        self.cell(0, 10, 'Reporte de Diseño - Jardín AR', 0, 1, 'C')
        self.line(10, 25, self.w - 10, 25)
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(*COLOR_GRAY)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

def generate_design_pdf(design: design_model.Design):
    pdf = PDF()
    pdf.add_page()
    
    # --- Bloque de Título del Diseño ---
    pdf.set_font('Helvetica', 'B', 22)
    pdf.set_text_color(*COLOR_PRIMARY)
    pdf.cell(0, 12, f'{design.name}', 0, 1, 'L')
    
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(*COLOR_GRAY)
    pdf.cell(0, 8, f'Generado el: {datetime.now().strftime("%d de %B de %Y a las %H:%M")}', 0, 1, 'L')
    pdf.ln(15)

    # --- TÍTULO DE LA TABLA ---
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(*COLOR_TEXT)
    pdf.cell(0, 10, 'Lista de Productos', 0, 1, 'L')
    pdf.ln(5)

    # --- Tabla de Items ---
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_fill_color(*COLOR_PRIMARY)
    pdf.set_text_color(255, 255, 255)
    
    col_width_num = 20
    col_width_qty = 40
    col_width_name = pdf.w - pdf.l_margin - pdf.r_margin - col_width_num - col_width_qty
    
    pdf.cell(col_width_num, 10, '#', 1, 0, 'C', fill=True)
    pdf.cell(col_width_name, 10, 'Producto', 1, 0, 'C', fill=True)
    pdf.cell(col_width_qty, 10, 'Cantidad', 1, 1, 'C', fill=True)
    
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(*COLOR_TEXT)
    fill_row = False
    for i, item in enumerate(design.items):
        if fill_row:
            pdf.set_fill_color(*COLOR_SECONDARY)
        else:
            pdf.set_fill_color(255, 255, 255)
            
        pdf.cell(col_width_num, 10, str(i + 1), 1, 0, 'C', fill=True)
        pdf.cell(col_width_name, 10, f'  {item.item_name}', 1, 0, 'L', fill=True)
        pdf.cell(col_width_qty, 10, str(item.quantity), 1, 1, 'C', fill=True)
        fill_row = not fill_row

    # --- Imagen del Diseño (EN UNA NUEVA PÁGINA) ---
    if design.screenshot_url:
        pdf.add_page()
        pdf.set_font('Helvetica', 'B', 16)
        pdf.set_text_color(*COLOR_PRIMARY)
        pdf.cell(0, 10, 'Visualización del Diseño', 0, 1, 'C')
        pdf.ln(5)

        try:
            response = requests.get(design.screenshot_url)
            response.raise_for_status() 
            
            img = Image.open(BytesIO(response.content))
            
            page_width = pdf.w - pdf.l_margin - pdf.r_margin
            page_height = pdf.h - pdf.t_margin - pdf.b_margin - 30 
            img_width, img_height = img.size
            aspect_ratio = float(img_width) / float(img_height)
            final_width = page_width
            final_height = final_width / aspect_ratio
            if final_height > page_height:
                final_height = page_height
                final_width = final_height * aspect_ratio
            x_centered = pdf.l_margin + (page_width - final_width) / 2
            y_centered = pdf.t_margin + 25 + (page_height - final_height) / 2
            
            with BytesIO() as image_buffer:
                img_format = img.format if img.format in ['JPEG', 'PNG', 'GIF'] else 'PNG'
                img.save(image_buffer, format=img_format)
                image_buffer.seek(0)
                pdf.image(image_buffer, x=x_centered, y=y_centered, w=final_width, h=final_height, type=img_format)

        except Exception as e:
            pdf.ln(10)
            pdf.set_font('Arial', 'I', 10)
            pdf.set_text_color(255, 0, 0)
            pdf.cell(0, 10, f"Error al cargar la imagen: {e}", 0, 1, 'C')

    return pdf.output()
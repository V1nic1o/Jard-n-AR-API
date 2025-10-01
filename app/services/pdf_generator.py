from fpdf import FPDF
import requests
from io import BytesIO
from PIL import Image

from app.models import design as design_model

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Diseño de Jardín - Jardín AR', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

def generate_design_pdf(design: design_model.Design):
    pdf = PDF()
    pdf.add_page()
    
    # --- Título del Diseño ---
    pdf.set_font('Arial', 'B', 16)
    # Usamos cell con write_html=True para manejar caracteres especiales como tildes
    pdf.cell(0, 10, f'Nombre del Diseño: {design.name}', 0, 1, 'L')
    pdf.ln(10)

    # --- Imagen del Diseño ---
    if design.screenshot_url:
        try:
            response = requests.get(design.screenshot_url)
            response.raise_for_status() 
            
            img = Image.open(BytesIO(response.content))
            
            page_width = pdf.w - 2 * pdf.l_margin
            img_width, img_height = img.size
            ratio = img_height / img_width
            final_width = page_width
            final_height = final_width * ratio
            
            # FPDF necesita una ruta de archivo o un buffer en memoria
            # Usamos un BytesIO buffer para pasar la imagen sin guardarla en disco
            with BytesIO() as image_buffer:
                # Determinamos el formato de la imagen para guardarlo correctamente
                img_format = img.format if img.format in ['JPEG', 'PNG', 'GIF'] else 'PNG'
                img.save(image_buffer, format=img_format)
                image_buffer.seek(0)
                pdf.image(image_buffer, w=final_width, h=final_height, type=img_format)

            pdf.ln(10)

        except Exception as e:
            pdf.set_font('Arial', 'I', 10)
            pdf.set_text_color(255, 0, 0)
            pdf.cell(0, 10, f"Error al cargar la imagen: {e}", 0, 1)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(10)


    # --- Tabla de Items ---
    pdf.set_font('Arial', 'B', 12)
    
    col_width = pdf.w / 4.5 # Ajustamos el ancho para que quepa bien
    pdf.cell(col_width / 2, 10, '#', 1, 0, 'C')
    pdf.cell(col_width * 2, 10, 'Producto', 1, 0, 'C')
    pdf.cell(col_width, 10, 'Cantidad', 1, 1, 'C')
    
    pdf.set_font('Arial', '', 12)
    for i, item in enumerate(design.items):
        pdf.cell(col_width / 2, 10, str(i + 1), 1, 0, 'C')
        pdf.cell(col_width * 2, 10, item.item_name, 1, 0, 'L')
        pdf.cell(col_width, 10, str(item.quantity), 1, 1, 'C')

    # --- CORRECCIÓN ---
    # pdf.output() ya devuelve los bytes necesarios. No necesitamos .encode()
    return pdf.output()
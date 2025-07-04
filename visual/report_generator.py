# visual/report_generator.py
import matplotlib.pyplot as plt
from fpdf import FPDF
from fpdf.enums import Align
from collections import Counter
import io
import os # Importamos 'os' para manejar rutas de archivo de forma robusta

class PDFReportGenerator(FPDF):
    def header(self):
        self.set_font('DejaVu', 'B', 12)
        self.cell(0, 10, 'Informe de Simulación - Sistema Logístico de Drones', align=Align.C, new_x="LMARGIN", new_y="NEXT")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('DejaVu', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', align=Align.C)

    def chapter_title(self, title):
        self.set_font('DejaVu', 'B', 12)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT", align=Align.L)
        self.ln(5)

    def add_table(self, headers, data):
        self.set_font('DejaVu', 'B', 10)
        col_widths = [self.epw / len(headers)] * len(headers)
        
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 7, header, border=1, align=Align.C)
        self.ln()
        
        self.set_font('DejaVu', '', 9)
        for row in data:
            for i, item in enumerate(row):
                self.cell(col_widths[i], 6, str(item), border=1)
            self.ln()
        self.ln(10)

    def add_matplotlib_chart(self, fig, title):
        self.chapter_title(title)
        
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        
        img_width = self.epw * 0.75
        
        # ## **THIS IS THE CORRECTED LINE** ##
        # The 'align' argument has been removed.
        self.image(buf, w=img_width) 
        
        plt.close(fig)
        self.ln(5)


def generate_report(simulation_data):
    pdf = PDFReportGenerator()
    
    # Use os.path.join to build the font path safely
    font_path_prefix = "visual"
    pdf.add_font("DejaVu", "", os.path.join(font_path_prefix, "DejaVuSans.ttf"))
    pdf.add_font("DejaVu", "B", os.path.join(font_path_prefix, "DejaVuSans-Bold.ttf"))
    pdf.add_font("DejaVu", "I", os.path.join(font_path_prefix, "DejaVuSans-Oblique.ttf"))
    pdf.set_font("DejaVu", "", 12)

    pdf.add_page()

    pdf.chapter_title("Rutas Más Frecuentes")
    if simulation_data['frequent_routes']:
        headers = ["Ruta", "Frecuencia"]
        data = [[str(item) for item in row] for row in simulation_data['frequent_routes']]
        pdf.add_table(headers, data)
    else:
        pdf.cell(0, 10, "No hay rutas completadas para mostrar.")
        pdf.ln()

    pdf.chapter_title("Clientes con Más Pedidos")
    if simulation_data['clients']:
        headers = ["ID Cliente", "Nombre", "Total Pedidos"]
        data = [[c['ID Cliente'], c['Nombre'], c['Total Pedidos']] for c in simulation_data['clients']]
        pdf.add_table(headers, data)
    else:
        pdf.cell(0, 10, "No hay clientes para mostrar.")
        pdf.ln()

    pdf.add_page()
    pdf.chapter_title("Estadísticas del Sistema")

    role_counts = simulation_data['role_counts']
    if role_counts:
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.pie(role_counts.values(), labels=role_counts.keys(), autopct='%1.1f%%', startangle=90)
        ax.set_title("Proporción de Nodos por Rol")
        pdf.add_matplotlib_chart(fig, "Gráfico de Proporción de Nodos")

    dest_counts = simulation_data['destination_counts']
    if dest_counts:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(dest_counts.keys(), dest_counts.values())
        ax.set_title("Nodos de Destino Más Visitados")
        plt.xticks(rotation=45, ha='right')
        pdf.add_matplotlib_chart(fig, "Gráfico de Nodos de Destino")

    pdf.add_page()
    pdf.chapter_title("Listado Completo de Órdenes")
    if simulation_data['orders']:
        headers = ["ID", "Cliente", "Origen", "Destino", "Estado", "Costo"]
        data = [[o['ID Orden'], o['ID Cliente'], o['Origen'], o['Destino'], o['Status'], o['Costo Total']] for o in simulation_data['orders']]
        pdf.add_table(headers, data)

    return pdf.output()
# visual/report_generator.py
import matplotlib.pyplot as plt
from fpdf import FPDF
from collections import Counter
import io

class PDFReportGenerator(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Informe de Simulación - Sistema Logístico de Drones', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(5)

    def add_table(self, headers, data):
        self.set_font('Arial', 'B', 10)
        col_width = self.w / (len(headers) + 0.5)
        for header in headers:
            self.cell(col_width, 7, header, 1, 0, 'C')
        self.ln()
        
        self.set_font('Arial', '', 10)
        for row in data:
            for item in row:
                self.cell(col_width, 6, str(item), 1)
            self.ln()
        self.ln(10)

    def add_matplotlib_chart(self, fig, title):
        self.chapter_title(title)
        
        # Guardar el gráfico en un buffer de memoria en lugar de un archivo
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        
        # Incrustar la imagen en el PDF
        self.image(buf, x=self.get_x(), y=self.get_y(), w=self.w / 2)
        plt.close(fig) # Cerrar la figura para liberar memoria
        self.ln(60)


def generate_report(simulation_data):
    """
    Función principal que crea y retorna el PDF como bytes.
    """
    pdf = PDFReportGenerator()
    pdf.add_page()

    # 1. Tabla de Rutas más Usadas [cite: 76]
    pdf.chapter_title("Rutas Más Frecuentes")
    if simulation_data['frequent_routes']:
        headers = ["Ruta", "Frecuencia"]
        data = simulation_data['frequent_routes']
        pdf.add_table(headers, data)
    else:
        pdf.cell(0, 10, "No hay rutas completadas para mostrar.")
        pdf.ln()

    # 2. Tabla de Clientes más Recurrentes [cite: 74]
    pdf.chapter_title("Clientes con Más Pedidos")
    if simulation_data['clients']:
        headers = ["ID Cliente", "Nombre", "Total Pedidos"]
        data = [[c['ID Cliente'], c['Nombre'], c['Total Pedidos']] for c in simulation_data['clients']]
        pdf.add_table(headers, data)
    else:
        pdf.cell(0, 10, "No hay clientes para mostrar.")
        pdf.ln()

    # 3. Gráficas del sistema [cite: 77]
    pdf.add_page()
    pdf.chapter_title("Estadísticas del Sistema")

    # Gráfico de Torta: Proporción de Nodos
    role_counts = simulation_data['role_counts']
    if role_counts:
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.pie(role_counts.values(), labels=role_counts.keys(), autopct='%1.1f%%', startangle=90)
        ax.set_title("Proporción de Nodos por Rol")
        pdf.add_matplotlib_chart(fig, "Gráfico de Proporción de Nodos")

    # Gráfico de Barras: Nodos destino más visitados
    dest_counts = simulation_data['destination_counts']
    if dest_counts:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(dest_counts.keys(), dest_counts.values())
        ax.set_title("Nodos de Destino Más Visitados")
        plt.xticks(rotation=45, ha='right')
        pdf.add_matplotlib_chart(fig, "Gráfico de Nodos de Destino")

    # 4. Tabla de todas las órdenes [cite: 73]
    pdf.add_page()
    pdf.chapter_title("Listado Completo de Órdenes")
    if simulation_data['orders']:
        headers = ["ID", "Cliente", "Origen", "Destino", "Estado", "Costo"]
        data = [[o['ID Orden'], o['ID Cliente'], o['Origen'], o['Destino'], o['Status'], o['Costo Total']] for o in simulation_data['orders']]
        pdf.add_table(headers, data)

    return pdf.output(dest='S').encode('latin-1')
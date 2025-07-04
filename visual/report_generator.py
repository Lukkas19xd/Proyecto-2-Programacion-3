import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def generate_pdf_report(simulation):
    """
    Genera un informe en PDF con estadísticas clave de la simulación.
    """
    if not simulation:
        return None

    # Crea un directorio para los reportes si no existe
    if not os.path.exists("reports"):
        os.makedirs("reports")

    # Nombre y ruta del archivo PDF
    pdf_path = "reports/simulation_report.pdf"
    
    # Crear el documento PDF
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # --- Título del Informe ---
    title = Paragraph("Informe de Simulación del Sistema de Drones", styles['h1'])
    story.append(title)
    story.append(Spacer(1, 12))

    # --- Resumen General ---
    summary_data = [
        ["Número Total de Nodos:", str(len(simulation.graph.vertices))],
        ["Número Total de Aristas:", str(len(simulation.graph.edges))],
        ["Total de Clientes:", str(len(simulation.clients))],
        ["Total de Órdenes:", str(len(simulation.orders))],
    ]
    summary_table = Table(summary_data, colWidths=[200, 100])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(Paragraph("Resumen General de la Simulación", styles['h2']))
    story.append(summary_table)
    story.append(Spacer(1, 24))

    # --- Rutas Más Frecuentes ---
    story.append(Paragraph("Rutas Más Frecuentes", styles['h2']))
    frequent_routes = simulation.get_frequent_routes()
    if frequent_routes:
        routes_data = [["Ruta", "Frecuencia"]]
        for route, freq in frequent_routes:
            routes_data.append([route, str(freq)])
        
        routes_table = Table(routes_data)
        routes_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        story.append(routes_table)
    else:
        story.append(Paragraph("No hay rutas frecuentes registradas.", styles['Normal']))

    # Generar el PDF
    try:
        doc.build(story)
        return pdf_path
    except Exception as e:
        print(f"Error al generar el PDF: {e}")
        return None
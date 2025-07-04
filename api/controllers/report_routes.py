from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from sim.simulation import Simulation
from visual.report_generator import generate_pdf_report

router = APIRouter()
simulation: Simulation = None

def set_simulation(sim: Simulation):
    global simulation
    simulation = sim

@router.get("/reports/pdf")
def get_pdf_report():
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulación no iniciada.")
    
    # Generar el informe y obtener la ruta del archivo
    pdf_path = generate_pdf_report(simulation)
    
    if not pdf_path:
        raise HTTPException(status_code=500, detail="Error al generar el informe PDF.")
        
    return FileResponse(pdf_path, media_type='application/pdf', filename="informe_rutas.pdf")
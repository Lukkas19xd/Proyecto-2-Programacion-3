# api/controllers/report_routes.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sim.simulation import Simulation
from ..depedencies import get_simulation
from visual.report_generator import generate_report
from collections import Counter
import io

router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)

@router.get("/pdf", response_class=StreamingResponse)
def get_pdf_report(sim: Simulation = Depends(get_simulation)):
    """
    Genera y obtiene el informe PDF resumen del sistema y las órdenes.
    """
    if not sim.graph or not sim.orders:
        raise HTTPException(status_code=404, detail="No hay datos de simulación para generar un informe.")

    # Recolectar todos los datos necesarios para el informe
    delivered_orders = [o for o in sim.orders.values() if o.status == 'Delivered']
    
    simulation_data = {
        'frequent_routes': sim.avl.get_frequent_routes(),
        'clients': sorted([c.to_dict() for c in sim.clients.values()], key=lambda x: x['Total Pedidos'], reverse=True),
        'orders': [o.to_dict() for o in sim.orders.values()],
        'role_counts': Counter(v.role for v in sim.graph.vertices.values()),
        'destination_counts': Counter(o.destination for o in delivered_orders) if delivered_orders else None
    }
    
    # Generar el PDF
    pdf_bytes = generate_report(simulation_data)
    
    # Crear un stream para la respuesta
    pdf_stream = io.BytesIO(pdf_bytes)
    
    return StreamingResponse(
        iter([pdf_stream.read()]),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment;filename=informe_simulacion.pdf"}
    )
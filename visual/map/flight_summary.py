import streamlit as st

def show_flight_summary(route, distance):
    """
    Muestra un resumen del vuelo, incluyendo la ruta, la distancia total y el costo energético.

    Args:
        route (list): Una lista de nodos que representan la ruta.
        distance (float): La distancia total de la ruta.
    """
    if route:
        st.subheader("Resumen de Vuelo")
        
        # Formatear la ruta para mostrarla como una cadena de texto
        route_str = " -> ".join(map(str, route))
        st.write(f"**Ruta:** {route_str}")
        
        st.write(f"**Distancia Total:** {distance:.2f} unidades")
        
        # Asumiendo que el costo es igual a la distancia para este ejemplo
        st.write(f"**Costo Energético:** {distance:.2f} unidades de batería")
        
        # Validar si la ruta excede la autonomía del dron
        autonomy_limit = 50  # Límite de autonomía del dron [cite: 36]
        if distance > autonomy_limit:
            st.warning("La ruta excede la autonomía máxima del dron y requerirá paradas de recarga.")
        else:
            st.success("La ruta se encuentra dentro de la autonomía del dron.")
    else:
        st.info("No se ha calculado ninguna ruta todavía.")
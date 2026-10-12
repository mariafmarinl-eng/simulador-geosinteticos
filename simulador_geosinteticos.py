import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, Rectangle
from matplotlib.lines import Line2D

# ------------------------------------------------------------
# SIMULADOR EDUCATIVO DE GEOSINTÉTICOS Y ESTABILIDAD DE TALUDES
# Ejecutar con: streamlit run simulador_geosinteticos.py
# Dependencias: streamlit, numpy, matplotlib
# ------------------------------------------------------------

st.set_page_config(
    page_title="GeoRefuerzo | Simulador de taludes",
    page_icon="⛰️",
    layout="wide"
)

# Paleta
SUELO = "#C99A6B"
SUELO_CLARO = "#E8D2B8"
REFUERZO = "#168B65"
FALLA = "#D94841"
AGUA = "#3186C8"
TEXTO = "#263238"

st.title("⛰️ GeoRefuerzo: simulador de taludes y geosintéticos")
st.markdown(
    "Explora cómo la geometría del talud, el agua y el refuerzo pueden influir "
    "en el comportamiento de un terreno. **Modelo visual educativo, no apto para diseño de obra.**"
)

with st.sidebar:
    st.header("🎛️ Parámetros del terreno")
    angulo = st.slider("Inclinación del talud (°)", 20, 60, 35, 1)
    altura = st.slider("Altura del talud (m)", 4, 20, 10, 1)
    cohesion = st.slider("Cohesión del suelo (kPa)", 2, 35, 12, 1)
    phi = st.slider("Ángulo de fricción interna (°)", 18, 40, 28, 1)
    gamma = st.slider("Peso unitario del suelo (kN/m³)", 16.0, 22.0, 19.0, 0.5)
    agua_pct = st.slider("Nivel de agua dentro del talud (%)", 0, 100, 30, 5)
    capas = st.slider("Número de capas de geosintético", 0, 6, 3, 1)
    aporte = st.slider("Aporte ilustrativo por capa (kPa)", 0.0, 8.0, 3.0, 0.5)
    deformacion_max = st.slider("Deformación máxima mostrada (%)", 2, 20, 12, 1)

# Cálculo ilustrativo de tendencia:
# No es un análisis de equilibrio límite de falla circular.
beta = np.radians(angulo)
phi_rad = np.radians(phi)
m = agua_pct / 100.0
sigma_n = gamma * altura * np.cos(beta) ** 2
tau_drive = gamma * altura * np.sin(beta) * np.cos(beta)
presion_agua = m * 9.81 * altura * np.cos(beta) ** 2 * 0.35
resistencia_suelo = cohesion + max(sigma_n - presion_agua, 0) * np.tan(phi_rad)
resistencia_refuerzo = capas * aporte
fs_sin = resistencia_suelo / max(tau_drive, 0.01)
fs_con = (resistencia_suelo + resistencia_refuerzo) / max(tau_drive, 0.01)

# Limitar el rango visual del indicador para que no domine la pantalla
fs_sin_visual = float(np.clip(fs_sin, 0, 3))
fs_con_visual = float(np.clip(fs_con, 0, 3))

# Métricas
m1, m2, m3, m4 = st.columns(4)
m1.metric("Inclinación", f"{angulo}°")
m2.metric("Capas de refuerzo", f"{capas}")
m3.metric("FS ilustrativo · sin refuerzo", f"{fs_sin:.2f}")
m4.metric(
    "FS ilustrativo · con refuerzo",
    f"{fs_con:.2f}",
    delta=f"{fs_con - fs_sin:+.2f}"
)

st.caption(
    "El indicador FS se calcula con una expresión simplificada para mostrar tendencias. "
    "No representa un cálculo validado de falla circular ni debe usarse para decidir la seguridad de un talud."
)

tab1, tab2, tab3 = st.tabs([
    "🪨 Perfil del talud",
    "📈 Esfuerzo–deformación",
    "🔬 Interacción suelo–geosintético"
])

with tab1:
    st.subheader("Corte transversal del terreno")
    st.write(
        "La línea roja representa una superficie de falla circular esquemática. "
        "Las líneas verdes son capas de refuerzo; la zona azul representa agua de forma conceptual."
    )

    fig, ax = plt.subplots(figsize=(11, 5.7))
    ax.set_facecolor("#F7FAFC")

    # Geometría esquemática del talud: plataforma, cara inclinada y pie.
    run = altura / np.tan(beta)
    x_left = 0
    x_crest = 5.0
    x_toe = x_crest + run
    x_right = x_toe + 5.0
    y_base = 0
    y_top = altura

    # Base de suelo
    soil_poly = Polygon(
        [(x_left, y_base), (x_right, y_base), (x_right, y_top),
         (x_crest, y_top), (x_toe, y_base)],
        closed=True, facecolor=SUELO_CLARO, edgecolor="#806344",
        linewidth=1.5, alpha=0.95
    )
    ax.add_patch(soil_poly)

    # Cara inclinada y superficie
    ax.plot([x_left, x_crest, x_toe, x_right],
            [y_top, y_top, y_base, y_base],
            color="#6D4C35", linewidth=2.2)

    # Capas estratificadas
    for y in np.arange(1.5, altura, 2.0):
        x_at_slope = x_crest + (y_top - y) / np.tan(beta)
        ax.plot([x_left, x_at_slope, x_right], [y, y, y],
                color="#B88A5C", linewidth=0.8, alpha=0.7)

    # Agua conceptual: nivel relativo en el macizo, con recorte visual sencillo
    if agua_pct > 0:
        y_water = altura * m
        x_water_end = min(x_toe, x_crest + (altura - y_water) / np.tan(beta))
        if y_water < altura:
            water_poly = Polygon(
                [(x_crest, y_water), (x_water_end, y_water),
                 (x_toe, 0), (x_crest, 0)],
                closed=True, facecolor=AGUA, edgecolor="none", alpha=0.18
            )
            ax.add_patch(water_poly)
            ax.plot([x_crest, x_water_end], [y_water, y_water],
                    color=AGUA, linestyle="--", linewidth=2)
            ax.text(x_crest + 0.2, max(0.25, y_water + 0.25),
                    "Nivel de agua (esquema)", color=AGUA, fontsize=9)

    # Refuerzos representados como líneas que penetran el terreno
    for i in range(capas):
        y = altura * (0.18 + 0.68 * (i + 1) / (capas + 1))
        x_end = x_crest + max(0.4, (altura - y) / np.tan(beta))
        ax.plot([x_crest - 0.1, min(x_end, x_toe - 0.15)],
                [y, y], color=REFUERZO, linewidth=3.0,
                solid_capstyle="round")
        ax.text(x_crest + 0.2, y + 0.15, f"Refuerzo {i+1}",
                color=REFUERZO, fontsize=8)

    # Superficie circular esquemática: se dibuja un arco ajustado al perfil.
    # Es ilustrativo, no una búsqueda calculada de la superficie crítica.
    center_x = x_crest + run * 0.55
    center_y = altura * 0.65
    radius = max(run * 0.72, altura * 0.65)
    theta = np.linspace(np.radians(205), np.radians(335), 240)
    arc_x = center_x + radius * np.cos(theta)
    arc_y = center_y + radius * np.sin(theta)
    mask = (arc_x >= x_crest - 0.2) & (arc_x <= x_toe + 0.4) & (arc_y >= -0.1) & (arc_y <= altura + 0.2)
    if np.sum(mask) > 2:
        ax.plot(arc_x[mask], arc_y[mask], color=FALLA, linewidth=2.5,
                linestyle="-", label="Superficie de falla esquemática")

    # Flecha de movimiento
    ax.annotate(
        "Movimiento potencial",
        xy=(x_crest + run * 0.70, altura * 0.35),
        xytext=(x_crest + run * 0.28, altura * 0.68),
        arrowprops=dict(arrowstyle="->", color=FALLA, lw=2),
        color=FALLA, fontsize=10, fontweight="bold"
    )

    ax.text(x_left + 0.2, altura + 0.35, "Corona", fontsize=9, color=TEXTO)
    ax.text(x_toe + 0.2, 0.35, "Pie del talud", fontsize=9, color=TEXTO)
    ax.set_xlim(x_left - 0.5, x_right + 1)
    ax.set_ylim(-0.5, altura + 1.3)
    ax.set_xlabel("Distancia horizontal (m) — esquema")
    ax.set_ylabel("Altura (m)")
    ax.set_title("Talud con capas de geosintético y superficie de falla conceptual")
    ax.grid(alpha=0.18)
    ax.legend(handles=[
        Line2D([0], [0], color=FALLA, lw=2.5, label="Falla esquemática"),
        Line2D([0], [0], color=REFUERZO, lw=3, label="Geosintético"),
        Line2D([0], [0], color=AGUA, lw=2, linestyle="--", label="Nivel de agua")
    ], loc="upper right")
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    st.info(
        "Prueba subir el nivel de agua y la inclinación, y luego añade capas de refuerzo. "
        "Observa cómo cambian los indicadores y recuerda que la geometría de la falla dibujada es ilustrativa."
    )

with tab2:
    st.subheader("Curvas conceptuales de esfuerzo–deformación")
    st.write(
        "Estas curvas son sintéticas para explicar la idea: un refuerzo bien movilizado puede "
        "cambiar la rigidez y la resistencia aparente del sistema. No son datos experimentales."
    )

    eps = np.linspace(0, deformacion_max, 250)  # deformación en %
    # Curva base y curva reforzada, con parámetros que cambian visualmente con el refuerzo.
    escala_sin = 1.0
    escala_con = 1.0 + min(capas * 0.10, 0.60)
    rigidez_sin = 7.0
    rigidez_con = rigidez_sin * (1 + min(capas * 0.12, 0.75))
    sigma_sin = escala_sin * (cohesion + 18 * (1 - np.exp(-eps / (rigidez_sin + 0.01))))
    sigma_con = escala_con * (cohesion + 18 * (1 - np.exp(-eps / (rigidez_con + 0.01))))

    fig2, ax2 = plt.subplots(figsize=(9, 4.8))
    ax2.plot(eps, sigma_sin, linewidth=2.5, color="#D97736", label="Suelo sin refuerzo")
    ax2.plot(eps, sigma_con, linewidth=2.5, color=REFUERZO, label="Sistema reforzado (conceptual)")
    ax2.set_xlabel("Deformación (%)")
    ax2.set_ylabel("Esfuerzo (kPa, escala ilustrativa)")
    ax2.set_title("Comparación conceptual de respuesta mecánica")
    ax2.grid(alpha=0.25)
    ax2.legend()
    st.pyplot(fig2, use_container_width=True)
    plt.close(fig2)

    st.caption(
        "No interpretes la separación entre curvas como un porcentaje real de mejora. "
        "Para obtener resultados cuantitativos se necesitan ensayos del suelo y del geosintético."
    )

with tab3:
    st.subheader("¿Cómo interactúan el suelo y el geosintético?")
    col_a, col_b = st.columns([1.15, 1])

    with col_a:
        fig3, ax3 = plt.subplots(figsize=(7, 4.7))
        ax3.set_xlim(0, 10)
        ax3.set_ylim(0, 6)
        ax3.set_facecolor("#FBF8F2")

        # Matriz de suelo
        ax3.add_patch(Rectangle((0.5, 1.0), 9.0, 4.0,
                                facecolor="#D8B58B", edgecolor="#8C6B48", alpha=0.55))
        rng = np.random.default_rng(7)
        for _ in range(75):
            px = rng.uniform(0.7, 9.3)
            py = rng.uniform(1.2, 4.8)
            ax3.add_patch(Circle((px, py), rng.uniform(0.035, 0.09),
                                 facecolor="#8D6E63", edgecolor="none", alpha=0.55))

        # Geomalla como barras y nervaduras
        y_grid = 2.8
        ax3.plot([0.8, 9.2], [y_grid, y_grid], color=REFUERZO, lw=3)
        for x in np.arange(1.0, 9.1, 0.55):
            ax3.plot([x, x], [y_grid - 0.28, y_grid + 0.28], color=REFUERZO, lw=2)

        # Flechas de extracción e interacción
        ax3.annotate("Fuerza de extracción", xy=(8.5, 2.8), xytext=(5.6, 5.45),
                     arrowprops=dict(arrowstyle="->", lw=2, color=FALLA),
                     color=FALLA, fontsize=10, fontweight="bold")
        for x in [2.0, 3.7, 5.4, 7.1]:
            ax3.annotate("", xy=(x, 2.8), xytext=(x, 3.45),
                         arrowprops=dict(arrowstyle="->", lw=1.4, color="#2457A6"))
        ax3.text(0.8, 1.25, "Partículas de suelo", color="#6D4C35", fontsize=9)
        ax3.text(0.8, 2.25, "Geomalla", color=REFUERZO, fontsize=9, fontweight="bold")
        ax3.set_title("Esquema de interacción y extracción")
        ax3.axis("off")
        st.pyplot(fig3, use_container_width=True)
        plt.close(fig3)

    with col_b:
        st.markdown("#### Mecanismos principales")
        st.markdown(
            "- **Fricción:** resistencia al deslizamiento relativo en la interfaz.\n"
            "- **Trabazón mecánica:** las partículas se enganchan en las aberturas de la geomalla.\n"
            "- **Resistencia a la tracción:** el geosintético toma parte de la carga cuando se deforma.\n"
            "- **Anclaje:** longitud suficiente dentro del suelo para movilizar resistencia."
        )
        st.warning(
            "La capacidad real depende del tipo de suelo, tamaño de partículas, geometría del geosintético, "
            "confinamiento, instalación y condiciones de agua."
        )

st.divider()
st.subheader("🧠 Lectura rápida del escenario")
if fs_sin < 1.0:
    st.error("El indicador simplificado sin refuerzo queda por debajo de 1.0. En este modelo conceptual, la resistencia calculada no alcanza la demanda.")
elif fs_sin < 1.3:
    st.warning("El indicador simplificado sin refuerzo está en un rango bajo para fines ilustrativos. No equivale a un criterio de aceptación de diseño.")
else:
    st.success("El indicador simplificado sin refuerzo es mayor que 1.3 en este escenario ilustrativo. Esto NO demuestra que el talud sea seguro.")

if fs_con > fs_sin:
    st.markdown(
        f"Con los parámetros elegidos, el indicador ilustrativo aumenta de **{fs_sin:.2f}** a "
        f"**{fs_con:.2f}** al incluir el aporte conceptual de las capas de refuerzo."
    )
else:
    st.markdown("Con estos parámetros no se observa un aumento del indicador.")

st.markdown("### Conclusiones")
st.markdown(
    "1. El aumento de la inclinación incrementa la demanda de resistencia en este modelo simplificado.\n"
    "2. El agua puede reducir la resistencia efectiva y favorecer la inestabilidad.\n"
    "3. Los geosintéticos pueden ayudar a reforzar o separar capas cuando se seleccionan y diseñan correctamente.\n"
    "4. Un proyecto real requiere investigación geotécnica, drenaje, análisis de equilibrio límite y verificación normativa."
)

st.caption(
    "Proyecto académico para exposición. La falla circular y las curvas son esquemáticas; "
    "el factor de seguridad mostrado es un indicador pedagógico simplificado, no un resultado de diseño."
)

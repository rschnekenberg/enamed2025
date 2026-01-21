import streamlit as st
import pandas as pd
import plotly.express as px
import re
from unidecode import unidecode

# -------------------------
# Page config (visual)
# -------------------------
st.set_page_config(
    page_title="ENADE Medicina 2025",
    page_icon="📊",
    layout="wide"
)

st.title("ENADE Medicina 2025")
st.markdown(
    """
    **Explorador interativo dos cursos de Medicina**  
    Relação entre *tamanho da turma* e *percentual de concluintes com proficiência*.
    """
)

# -------------------------
# Load data
# -------------------------
df_raw = pd.read_excel("conceito-enade-2025-medicina.xlsx")

# Keep a copy with original names (Portuguese)
df = df_raw.copy()

# -------------------------
# Clean column names (internal use only)
# -------------------------
def clean_col(s):
    s = unidecode(str(s)).strip().lower()
    s = re.sub(r"[*º°]", "", s)
    s = re.sub(r"[^\w]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s

df.columns = [clean_col(c) for c in df.columns]

# -------------------------
# Main plot
# -------------------------
fig = px.scatter(
    df,
    x="no_de_concluintes_participantes",
    y="percentual_de_concluintes_participantes_igual_ou_acima_da_proficiencia",
    hover_name=df_raw["Nome da IES*"],  # ORIGINAL Portuguese name
    hover_data={
        "no_de_concluintes_participantes": True,
        "percentual_de_concluintes_participantes_igual_ou_acima_da_proficiencia": True,
        "sigla_da_uf": True,
        "conceito_enade_faixa": True
    },
    labels={
        "no_de_concluintes_participantes": "Nº de Concluintes Participantes",
        "percentual_de_concluintes_participantes_igual_ou_acima_da_proficiencia":
            "Percentual de Concluintes com Proficiência",
        "sigla_da_uf": "UF",
        "conceito_enade_faixa": "Conceito ENADE"
    },
    title="Tamanho da turma vs Proficiência – ENADE Medicina 2025",
    color="conceito_enade_faixa",
    color_continuous_scale="Viridis",
    height=650,
    width=650
)

# Force square aspect ratio
fig.update_yaxes(scaleanchor="x", scaleratio=1)

# Improve aesthetics
fig.update_traces(
    marker=dict(size=10, opacity=0.7, line=dict(width=0.5, color="black"))
)

fig.update_layout(
    title_x=0.5,
    template="plotly_white",
    legend_title="Conceito ENADE",
    margin=dict(l=40, r=40, t=80, b=40)
)

st.plotly_chart(fig, use_container_width=False)

# -------------------------
# Footer
# -------------------------
st.markdown("---")
st.caption(
    "Fonte: INEP / ENADE 2025 – Cursos de Medicina. "
    "Aplicação desenvolvida em Python (Streamlit + Plotly)."
)

import streamlit as st
import pandas as pd
import plotly.express as px
import json

# -------------------------
# Page config
# -------------------------
st.set_page_config(
    page_title="ENADE Medicina 2025",
    page_icon="📊",
    layout="wide"
)

# -------------------------
# Load and prepare data
# -------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("conceito-enade-2025-medicina.xlsx")
    # Rename columns for easier access
    df = df.rename(columns={
        'Nome da IES*': 'nome_ies',
        'Sigla da IES*': 'sigla_ies',
        'Município do Curso': 'municipio',
        'Sigla da UF': 'uf',
        'Categoria Administrativa': 'categoria',
        'Nº de Concluintes Inscritos': 'n_inscritos',
        'Nº  de Concluintes Participantes': 'n_participantes',
        'Percentual de Concluintes Participantes Igual ou Acima da Proficiência ': 'pct_proficiencia',
        'Conceito Enade (Faixa)': 'conceito_enade',
        'Organização Acadêmica': 'org_academica',
        'Código do Curso': 'cod_curso'
    })
    # Convert proficiency to percentage for display
    df['pct_proficiencia_display'] = df['pct_proficiencia'] * 100
    # Calculate abstenção (percentage who did NOT participate)
    df['abstencao'] = ((df['n_inscritos'] - df['n_participantes']) / df['n_inscritos'] * 100).round(1)
    # Make conceito_enade categorical with proper ordering
    df['conceito_enade'] = df['conceito_enade'].astype(str)
    # Drop rows with missing essential data
    df = df.dropna(subset=['n_participantes', 'pct_proficiencia'])
    return df

@st.cache_data
def load_coordinates():
    """Load pre-computed coordinates from JSON file."""
    try:
        with open('coordinates.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def add_coordinates(df, coords):
    """Add lat/lon coordinates to dataframe."""
    df = df.copy()
    df['lat'] = df.apply(
        lambda row: coords.get(f"{row['municipio']}, {row['uf']}", {}).get('lat'),
        axis=1
    )
    df['lon'] = df.apply(
        lambda row: coords.get(f"{row['municipio']}, {row['uf']}", {}).get('lon'),
        axis=1
    )
    return df

df = load_data()
coords = load_coordinates()

# -------------------------
# Header
# -------------------------
st.title("📊 ENADE Medicina 2025")
st.markdown(
    """
    **Explorador interativo dos cursos de Medicina**
    Dados do Exame Nacional de Desempenho dos Estudantes (ENADE) 2025.
    """
)

st.divider()

# =========================================
# SECTION 1: Interactive Scatter Plot
# =========================================
st.header("1. Número de Alunos Concluintes vs Proficiência")
st.markdown("Explore a relação entre o número de concluintes participantes e o percentual com proficiência.")

# Filters in columns
col_filters1, col_filters2, col_filters3 = st.columns(3)

with col_filters1:
    # UF filter
    uf_options = sorted(df['uf'].dropna().unique().tolist())
    selected_ufs = st.multiselect(
        "Filtrar por UF",
        options=uf_options,
        default=[],
        placeholder="Todas as UFs",
        key="scatter_uf"
    )

with col_filters2:
    # Administrative category filter
    cat_options = sorted(df['categoria'].dropna().unique().tolist())
    selected_cats = st.multiselect(
        "Filtrar por Categoria Administrativa",
        options=cat_options,
        default=[],
        placeholder="Todas as categorias",
        key="scatter_cat"
    )

with col_filters3:
    # Color by selector
    color_options = {
        "UF": "uf",
        "Categoria Administrativa": "categoria",
        "Conceito ENADE": "conceito_enade"
    }
    color_by = st.selectbox(
        "Colorir pontos por",
        options=list(color_options.keys()),
        index=0
    )

# Participant range slider
min_part = int(df['n_participantes'].min())
max_part = int(df['n_participantes'].max())
participant_range = st.slider(
    "Filtrar por número de participantes",
    min_value=min_part,
    max_value=max_part,
    value=(min_part, max_part)
)

# Apply filters
df_filtered = df.copy()

if selected_ufs:
    df_filtered = df_filtered[df_filtered['uf'].isin(selected_ufs)]

if selected_cats:
    df_filtered = df_filtered[df_filtered['categoria'].isin(selected_cats)]

df_filtered = df_filtered[
    (df_filtered['n_participantes'] >= participant_range[0]) &
    (df_filtered['n_participantes'] <= participant_range[1])
]

# Show count
st.caption(f"Mostrando {len(df_filtered)} de {len(df)} cursos")

# Create scatter plot
if len(df_filtered) > 0:
    # Determine if color should be categorical
    color_col = color_options[color_by]

    # For Conceito ENADE, sort categories properly
    if color_by == "Conceito ENADE":
        # Get unique values and sort them
        conceito_order = sorted(df_filtered['conceito_enade'].dropna().unique(),
                               key=lambda x: (x == 'nan', x))
        fig_scatter = px.scatter(
            df_filtered,
            x="n_participantes",
            y="pct_proficiencia_display",
            color=color_col,
            category_orders={"conceito_enade": conceito_order},
            hover_name="nome_ies",
            hover_data={
                "n_participantes": True,
                "n_inscritos": True,
                "abstencao": True,
                "pct_proficiencia_display": ":.1f",
                "uf": True,
                "municipio": True,
                "categoria": True,
                "conceito_enade": True,
            },
            labels={
                "n_participantes": "Nº de Concluintes Participantes",
                "n_inscritos": "Nº de Concluintes Inscritos",
                "abstencao": "Abstenção (%)",
                "pct_proficiencia_display": "Proficientes (%)",
                "uf": "UF",
                "municipio": "Município",
                "categoria": "Categoria Administrativa",
                "conceito_enade": "Conceito ENADE"
            },
            title="Número de Alunos Concluintes vs Percentual com Proficiência",
            height=600
        )
    else:
        fig_scatter = px.scatter(
            df_filtered,
            x="n_participantes",
            y="pct_proficiencia_display",
            color=color_col,
            hover_name="nome_ies",
            hover_data={
                "n_participantes": True,
                "n_inscritos": True,
                "abstencao": True,
                "pct_proficiencia_display": ":.1f",
                "uf": True,
                "municipio": True,
                "categoria": True,
                "conceito_enade": True,
                color_col: False  # Hide duplicate
            },
            labels={
                "n_participantes": "Nº de Concluintes Participantes",
                "n_inscritos": "Nº de Concluintes Inscritos",
                "abstencao": "Abstenção (%)",
                "pct_proficiencia_display": "Proficientes (%)",
                "uf": "UF",
                "municipio": "Município",
                "categoria": "Categoria Administrativa",
                "conceito_enade": "Conceito ENADE"
            },
            title="Número de Alunos Concluintes vs Percentual com Proficiência",
            height=600
        )

    fig_scatter.update_traces(
        marker=dict(size=8, opacity=0.7, line=dict(width=0.5, color="white"))
    )

    fig_scatter.update_layout(
        title_x=0.5,
        template="plotly_white",
        legend_title=color_by,
        xaxis_title="Número de Alunos Concluintes Participantes",
        yaxis_title="Proficientes (%)",
        yaxis=dict(range=[0, 100]),  # Fixed Y-axis range
        hovermode="closest"
    )

    st.plotly_chart(fig_scatter, use_container_width=True)
else:
    st.warning("Nenhum curso encontrado com os filtros selecionados.")

st.divider()

# =========================================
# SECTION 2: Interactive Map of Brazil
# =========================================
st.header("2. Mapa das Instituições")
st.markdown("Visualize a localização geográfica das instituições de Medicina no Brasil.")

# Add coordinates to dataframe
df_geo = add_coordinates(df, coords)

# Map filters
col_map_filter1, col_map_filter2 = st.columns(2)

with col_map_filter1:
    # UF filter for map
    map_uf_options = sorted(df_geo['uf'].dropna().unique().tolist())
    map_selected_ufs = st.multiselect(
        "Filtrar por UF",
        options=map_uf_options,
        default=[],
        placeholder="Todas as UFs",
        key="map_uf"
    )

with col_map_filter2:
    # Administrative category filter for map
    map_cat_options = sorted(df_geo['categoria'].dropna().unique().tolist())
    map_selected_cats = st.multiselect(
        "Filtrar por Categoria Administrativa",
        options=map_cat_options,
        default=[],
        placeholder="Todas as categorias",
        key="map_cat"
    )

# Apply map filters
df_map_filtered = df_geo.copy()

if map_selected_ufs:
    df_map_filtered = df_map_filtered[df_map_filtered['uf'].isin(map_selected_ufs)]

if map_selected_cats:
    df_map_filtered = df_map_filtered[df_map_filtered['categoria'].isin(map_selected_cats)]

# Filter out rows without coordinates
df_map = df_map_filtered.dropna(subset=['lat', 'lon'])

if len(df_map) > 0:
    # Calculate weighted statistics for filtered data
    total_participantes = df_map['n_participantes'].sum()
    # Weighted mean: sum(proficiency * participants) / sum(participants)
    weighted_mean_proficiency = (
        (df_map['pct_proficiencia_display'] * df_map['n_participantes']).sum() / total_participantes
    )

    # Display statistics
    col_stats1, col_stats2, col_stats3 = st.columns(3)
    with col_stats1:
        st.metric("Instituições", f"{len(df_map)}")
    with col_stats2:
        st.metric("Total de Participantes", f"{int(total_participantes):,}".replace(",", "."))
    with col_stats3:
        st.metric("Média Ponderada de Proficiência", f"{weighted_mean_proficiency:.1f}%")

    # Map controls
    col_map1, col_map2 = st.columns([1, 2])

    with col_map1:
        # Color scale for proficiency
        color_scale_options = {
            "Viridis": "Viridis",
            "Plasma": "Plasma",
            "Inferno": "Inferno",
            "Blues": "Blues",
            "Greens": "Greens",
            "Reds": "Reds",
            "RdYlGn": "RdYlGn"
        }
        selected_colorscale = st.selectbox(
            "Escala de cores",
            options=list(color_scale_options.keys()),
            index=0
        )

        # Proficiency range for color mapping
        min_pct = float(df_map['pct_proficiencia_display'].min())
        max_pct = float(df_map['pct_proficiencia_display'].max())

        color_range = st.slider(
            "Faixa de proficiência para cores (%)",
            min_value=0.0,
            max_value=100.0,
            value=(min_pct, max_pct),
            step=1.0
        )

    with col_map2:
        st.caption(f"Mostrando {len(df_map)} instituições no mapa")

    # Create map
    fig_map = px.scatter_mapbox(
        df_map,
        lat="lat",
        lon="lon",
        color="pct_proficiencia_display",
        size_max=15,
        hover_name="nome_ies",
        hover_data={
            "lat": False,
            "lon": False,
            "pct_proficiencia_display": ":.1f",
            "n_participantes": True,
            "n_inscritos": True,
            "abstencao": True,
            "municipio": True,
            "uf": True,
            "categoria": True,
            "conceito_enade": True
        },
        labels={
            "pct_proficiencia_display": "Proficientes (%)",
            "n_participantes": "Nº Participantes",
            "n_inscritos": "Nº Inscritos",
            "abstencao": "Abstenção (%)",
            "municipio": "Município",
            "uf": "UF",
            "categoria": "Categoria",
            "conceito_enade": "Conceito ENADE"
        },
        color_continuous_scale=color_scale_options[selected_colorscale],
        range_color=color_range,
        zoom=3,
        center={"lat": -14.235, "lon": -51.925},  # Center of Brazil
        mapbox_style="carto-positron",
        height=700
    )

    fig_map.update_traces(
        marker=dict(size=10, opacity=0.8)
    )

    fig_map.update_layout(
        title="Localização das Instituições de Medicina",
        title_x=0.5,
        coloraxis_colorbar=dict(
            title="Proficientes (%)",
            ticksuffix="%"
        ),
        margin=dict(l=0, r=0, t=50, b=0)
    )

    st.plotly_chart(fig_map, use_container_width=True)

    st.info("💡 Use o scroll do mouse para zoom. Clique e arraste para mover o mapa.")
else:
    st.warning("Nenhuma instituição encontrada com os filtros selecionados.")

# -------------------------
# Footer
# -------------------------
st.divider()
st.caption(
    "Fonte: INEP / ENADE 2025 – Cursos de Medicina. "
    "Aplicação desenvolvida em Python (Streamlit + Plotly)."
)

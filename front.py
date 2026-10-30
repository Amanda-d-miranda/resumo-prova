"""
Painel do Clima - Streamlit + Open-Meteo
Executar:  streamlit run app_clima.py
Requisitos: pip install streamlit requests pandas plotly
"""

from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

# ----------------------------------------------------------------------------
# Configuração da página
# ----------------------------------------------------------------------------
st.set_page_config(page_title="Painel do Clima", page_icon="🌦️", layout="wide")

# Paleta: fundo azul-noite, cada métrica com sua própria cor
COR = {
    "fundo": "#0E1630",
    "painel": "#17234A",
    "texto": "#F2F5FF",
    "suave": "#9AA7D1",
    "temperatura": "#FF6B57",  # coral
    "sensacao": "#FFB938",  # âmbar
    "umidade": "#22D3C5",  # turquesa
    "vento": "#A78BFA",  # violeta
    "chuva": "#4DA3FF",  # azul céu
    "elevacao": "#7BD88F",  # verde
    "data": "#FF7EB6",  # rosa
}

CIDADES = {
    "São Paulo, SP": (-23.5505, -46.6333),
    "Rio de Janeiro, RJ": (-22.9068, -43.1729),
    "Brasília, DF": (-15.7939, -47.8828),
    "Salvador, BA": (-12.9777, -38.5016),
    "Fortaleza, CE": (-3.7319, -38.5267),
    "Manaus, AM": (-3.1190, -60.0217),
    "Curitiba, PR": (-25.4284, -49.2733),
    "Porto Alegre, RS": (-30.0346, -51.2177),
    "Florianópolis, SC": (-27.5954, -48.5480),
    "Joinville, SC": (-26.3045, -48.8487),
    "Belo Horizonte, MG": (-19.9167, -43.9345),
    "Recife, PE": (-8.0476, -34.8770),
}

CODIGOS = {
    0: ("Céu limpo", "☀️", "🌙"),
    1: ("Predomínio de sol", "🌤️", "🌙"),
    2: ("Parcialmente nublado", "⛅", "☁️"),
    3: ("Nublado", "☁️", "☁️"),
    45: ("Neblina", "🌫️", "🌫️"),
    48: ("Neblina com geada", "🌫️", "🌫️"),
    51: ("Garoa fraca", "🌦️", "🌧️"),
    53: ("Garoa moderada", "🌦️", "🌧️"),
    55: ("Garoa intensa", "🌧️", "🌧️"),
    61: ("Chuva fraca", "🌦️", "🌧️"),
    63: ("Chuva moderada", "🌧️", "🌧️"),
    65: ("Chuva forte", "🌧️", "🌧️"),
    66: ("Chuva congelante", "🌧️", "🌧️"),
    67: ("Chuva congelante forte", "🌧️", "🌧️"),
    71: ("Neve fraca", "🌨️", "🌨️"),
    73: ("Neve moderada", "🌨️", "🌨️"),
    75: ("Neve forte", "❄️", "❄️"),
    80: ("Pancadas de chuva", "🌦️", "🌧️"),
    81: ("Pancadas moderadas", "🌧️", "🌧️"),
    82: ("Pancadas fortes", "⛈️", "⛈️"),
    95: ("Trovoadas", "⛈️", "⛈️"),
    96: ("Trovoadas com granizo", "⛈️", "⛈️"),
    99: ("Trovoadas com granizo forte", "⛈️", "⛈️"),
}

DIAS = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]

# ----------------------------------------------------------------------------
# Estilo
# ----------------------------------------------------------------------------
st.markdown(
    f"""
    <style>
    .stApp {{
        background: radial-gradient(circle at 15% 0%, #1E2D63 0%, {COR['fundo']} 55%);
        color: {COR['texto']};
    }}
    [data-testid="stSidebar"] {{ background: {COR['painel']}; }}
    [data-testid="stHeader"] {{ background: transparent; }}
    h1, h2, h3, h4, p, label, span {{ color: {COR['texto']}; }}

    .hero {{
        background: linear-gradient(120deg, {COR['temperatura']}33, {COR['vento']}33 60%, {COR['chuva']}33);
        border: 1px solid #ffffff22;
        border-radius: 22px;
        padding: 26px 32px;
        display: flex; justify-content: space-between; align-items: center;
        flex-wrap: wrap; gap: 16px; margin-bottom: 22px;
    }}
    .hero .cidade {{ font-size: 1.1rem; color: {COR['suave']}; margin: 0; }}
    .hero .temp {{ font-size: 4.2rem; font-weight: 800; line-height: 1; margin: 4px 0; }}
    .hero .desc {{ font-size: 1.3rem; margin: 0; }}
    .hero .emoji {{ font-size: 5.5rem; line-height: 1; }}
    .hero .quando {{ color: {COR['data']}; font-weight: 600; margin-top: 6px; }}

    .card {{
        background: {COR['painel']};
        border-radius: 18px;
        padding: 18px 20px;
        border: 1px solid #ffffff14;
        border-left: 6px solid var(--cor);
        height: 100%;
    }}
    .card .rotulo {{ color: {COR['suave']}; font-size: .9rem; margin: 0 0 6px 0; }}
    .card .valor {{ font-size: 2rem; font-weight: 700; margin: 0; color: var(--cor); }}
    .card .valor small {{ font-size: 1rem; color: {COR['suave']}; font-weight: 500; }}
    .card .detalhe {{ color: {COR['suave']}; font-size: .8rem; margin: 6px 0 0 0; }}

    .dia {{
        background: {COR['painel']}; border-radius: 16px; padding: 14px 10px;
        text-align: center; border-top: 5px solid var(--cor); border: 1px solid #ffffff14;
        border-top: 5px solid var(--cor);
    }}
    .dia .nome {{ font-weight: 700; margin: 0; }}
    .dia .data {{ color: {COR['suave']}; font-size: .78rem; margin: 0 0 6px 0; }}
    .dia .ico {{ font-size: 2rem; margin: 0; }}
    .dia .max {{ color: {COR['temperatura']}; font-weight: 700; margin: 4px 0 0 0; }}
    .dia .min {{ color: {COR['chuva']}; font-weight: 600; margin: 0; }}
    .dia .chuva {{ color: {COR['umidade']}; font-size: .8rem; margin: 6px 0 0 0; }}

    button[data-baseweb="tab"] {{ font-weight: 600; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# Dados
# ----------------------------------------------------------------------------
UNIDADES_TEMP = {"°C": "celsius", "°F": "fahrenheit"}
UNIDADES_VENTO = {"km/h": "kmh", "m/s": "ms", "mph": "mph", "nós": "kn"}


@st.cache_data(ttl=600, show_spinner=False)
def buscar_clima(lat, lon, unid_temp, unid_vento):
    """Consulta a API Open-Meteo e devolve o JSON (cache de 10 minutos)."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,"
        "wind_speed_10m,precipitation,weather_code,is_day",
        "hourly": "temperature_2m,apparent_temperature,relative_humidity_2m,"
        "precipitation_probability,wind_speed_10m",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,"
        "precipitation_sum,precipitation_probability_max,wind_speed_10m_max",
        "timezone": "auto",
        "forecast_days": 7,
        "temperature_unit": unid_temp,
        "wind_speed_unit": unid_vento,
    }
    resposta = requests.get("https://api.open-meteo.com/v1/forecast", params=params, timeout=15)
    resposta.raise_for_status()
    return resposta.json()


def descricao(codigo, dia=True):
    nome, emoji_dia, emoji_noite = CODIGOS.get(codigo, ("Condição desconhecida", "🌡️", "🌡️"))
    return nome, (emoji_dia if dia else emoji_noite)


def formatar_data(dt):
    return f"{DIAS[dt.weekday()]}, {dt.day} {MESES[dt.month - 1]} {dt.year}"


def card(rotulo, valor, unidade, cor, detalhe=""):
    return (
        f'<div class="card" style="--cor:{cor}">'
        f'<p class="rotulo">{rotulo}</p>'
        f'<p class="valor">{valor} <small>{unidade}</small></p>'
        f'<p class="detalhe">{detalhe}</p></div>'
    )


def estilo_grafico(fig, altura=320, titulo=""):
    fig.update_layout(
        title=dict(text=titulo, font=dict(size=16, color=COR["texto"])),
        height=altura,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=COR["suave"]),
        legend=dict(orientation="h", y=1.15, x=0),
        hovermode="x unified",
    )
    fig.update_xaxes(gridcolor="#ffffff12", showline=False)
    fig.update_yaxes(gridcolor="#ffffff12", zeroline=False)
    return fig


def medidor(valor, titulo, minimo, maximo, cor, sufixo):
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=valor,
            number=dict(suffix=f" {sufixo}", font=dict(color=COR["texto"], size=34)),
            title=dict(text=titulo, font=dict(color=COR["suave"], size=16)),
            gauge=dict(
                axis=dict(range=[minimo, maximo], tickcolor=COR["suave"]),
                bar=dict(color=cor, thickness=0.75),
                bgcolor="#ffffff0d",
                borderwidth=0,
            ),
        )
    )
    fig.update_layout(
        height=240,
        margin=dict(l=25, r=25, t=60, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=COR["texto"]),
    )
    return fig


# ----------------------------------------------------------------------------
# Barra lateral
# ----------------------------------------------------------------------------
with st.sidebar:
    st.title("🌦️ Painel do Clima")
    st.caption("Dados em tempo real da Open-Meteo")

    escolha = st.selectbox("Cidade", [*CIDADES.keys(), "Coordenadas personalizadas"])
    if escolha == "Coordenadas personalizadas":
        lat = st.number_input("Latitude", value=-23.5505, min_value=-90.0, max_value=90.0, format="%.4f")
        lon = st.number_input("Longitude", value=-46.6333, min_value=-180.0, max_value=180.0, format="%.4f")
        nome_local = f"{lat:.2f}, {lon:.2f}"
    else:
        lat, lon = CIDADES[escolha]
        nome_local = escolha

    st.divider()
    unid_temp_rotulo = st.radio("Temperatura", list(UNIDADES_TEMP), horizontal=True)
    unid_vento_rotulo = st.radio("Vento", list(UNIDADES_VENTO), horizontal=True)

    st.divider()
    if st.button("🔄 Atualizar agora", use_container_width=True):
        buscar_clima.clear()
        st.rerun()

# ----------------------------------------------------------------------------
# Busca com tratamento de erros
# ----------------------------------------------------------------------------
try:
    with st.spinner("Buscando dados do clima..."):
        dados = buscar_clima(lat, lon, UNIDADES_TEMP[unid_temp_rotulo], UNIDADES_VENTO[unid_vento_rotulo])
except requests.exceptions.RequestException as erro:
    st.error(f"Não foi possível consultar a API. Verifique sua conexão e tente de novo. Detalhe: {erro}")
    st.stop()

atual = dados["current"]
horario = pd.DataFrame(dados["hourly"])
horario["time"] = pd.to_datetime(horario["time"])
diario = pd.DataFrame(dados["daily"])
diario["time"] = pd.to_datetime(diario["time"])

agora = datetime.fromisoformat(atual["time"])
eh_dia = bool(atual["is_day"])
nome_clima, emoji = descricao(atual["weather_code"], eh_dia)
un_t = unid_temp_rotulo
un_v = unid_vento_rotulo

# Próximas 48 horas a partir da hora atual
proximas = horario[horario["time"] >= pd.Timestamp(agora).floor("h")].head(48)

# ----------------------------------------------------------------------------
# Cabeçalho
# ----------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="hero">
        <div>
            <p class="cidade">📍 {nome_local}</p>
            <p class="temp">{atual['temperature_2m']:.1f}{un_t}</p>
            <p class="desc">{nome_clima} · sensação de {atual['apparent_temperature']:.1f}{un_t}</p>
            <p class="quando">{formatar_data(agora)} · {agora.strftime('%H:%M')}</p>
        </div>
        <div class="emoji">{emoji}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

aba_agora, aba_horas, aba_dias, aba_dados = st.tabs(
    ["Agora", "Próximas 48 horas", "Próximos 7 dias", "Dados"]
)

# ----------------------------------------------------------------------------
# Aba: Agora
# ----------------------------------------------------------------------------
with aba_agora:
    c1, c2, c3 = st.columns(3)
    c1.markdown(card("Temperatura", f"{atual['temperature_2m']:.1f}", un_t, COR["temperatura"], "Medida a 2 m do solo"), unsafe_allow_html=True)
    c2.markdown(card("Sensação térmica", f"{atual['apparent_temperature']:.1f}", un_t, COR["sensacao"], "Considera vento e umidade"), unsafe_allow_html=True)
    c3.markdown(card("Umidade relativa", f"{atual['relative_humidity_2m']:.0f}", "%", COR["umidade"], "Quanto maior, mais abafado"), unsafe_allow_html=True)

    st.write("")
    c4, c5, c6 = st.columns(3)
    c4.markdown(card("Velocidade do vento", f"{atual['wind_speed_10m']:.1f}", un_v, COR["vento"], "Medida a 10 m do solo"), unsafe_allow_html=True)
    c5.markdown(card("Precipitação", f"{atual['precipitation']:.1f}", "mm", COR["chuva"], "Acumulado na última hora"), unsafe_allow_html=True)
    c6.markdown(card("Elevação", f"{dados['elevation']:.0f}", "m", COR["elevacao"], "Acima do nível do mar"), unsafe_allow_html=True)

    st.write("")
    g1, g2, g3 = st.columns(3)
    faixa_t = (-10, 45) if un_t == "°C" else (14, 113)
    faixa_v = {"km/h": 100, "m/s": 28, "mph": 62, "nós": 54}[un_v]
    g1.plotly_chart(medidor(atual["temperature_2m"], "Temperatura", *faixa_t, COR["temperatura"], un_t), use_container_width=True)
    g2.plotly_chart(medidor(atual["relative_humidity_2m"], "Umidade", 0, 100, COR["umidade"], "%"), use_container_width=True)
    g3.plotly_chart(medidor(atual["wind_speed_10m"], "Vento", 0, faixa_v, COR["vento"], un_v), use_container_width=True)

# ----------------------------------------------------------------------------
# Aba: Próximas 48 horas
# ----------------------------------------------------------------------------
with aba_horas:
    col_a, col_b = st.columns(2)

    fig_t = go.Figure()
    fig_t.add_trace(go.Scatter(x=proximas["time"], y=proximas["temperature_2m"], name="Temperatura",
                               line=dict(color=COR["temperatura"], width=3), fill="tozeroy",
                               fillcolor="rgba(255,107,87,0.12)"))
    fig_t.add_trace(go.Scatter(x=proximas["time"], y=proximas["apparent_temperature"], name="Sensação",
                               line=dict(color=COR["sensacao"], width=2, dash="dot")))
    col_a.plotly_chart(estilo_grafico(fig_t, titulo=f"Temperatura ({un_t})"), use_container_width=True)

    fig_u = go.Figure(go.Scatter(x=proximas["time"], y=proximas["relative_humidity_2m"], name="Umidade",
                                 line=dict(color=COR["umidade"], width=3), fill="tozeroy",
                                 fillcolor="rgba(34,211,197,0.14)"))
    fig_u.update_yaxes(range=[0, 100])
    col_b.plotly_chart(estilo_grafico(fig_u, titulo="Umidade relativa (%)"), use_container_width=True)

    col_c, col_d = st.columns(2)
    fig_c = go.Figure(go.Bar(x=proximas["time"], y=proximas["precipitation_probability"],
                             name="Chance de chuva", marker_color=COR["chuva"]))
    fig_c.update_yaxes(range=[0, 100])
    col_c.plotly_chart(estilo_grafico(fig_c, titulo="Chance de chuva (%)"), use_container_width=True)

    fig_v = go.Figure(go.Scatter(x=proximas["time"], y=proximas["wind_speed_10m"], name="Vento",
                                 line=dict(color=COR["vento"], width=3, shape="spline")))
    col_d.plotly_chart(estilo_grafico(fig_v, titulo=f"Velocidade do vento ({un_v})"), use_container_width=True)

# ----------------------------------------------------------------------------
# Aba: Próximos 7 dias
# ----------------------------------------------------------------------------
with aba_dias:
    cores_dias = [COR["temperatura"], COR["sensacao"], COR["elevacao"], COR["umidade"],
                  COR["chuva"], COR["vento"], COR["data"]]
    colunas = st.columns(len(diario))
    for i, (col, linha) in enumerate(zip(colunas, diario.itertuples())):
        _, ico = descricao(linha.weather_code)
        rotulo_dia = "Hoje" if i == 0 else DIAS[linha.time.weekday()]
        col.markdown(
            f"""
            <div class="dia" style="--cor:{cores_dias[i % len(cores_dias)]}">
                <p class="nome">{rotulo_dia}</p>
                <p class="data">{linha.time.day} {MESES[linha.time.month - 1]}</p>
                <p class="ico">{ico}</p>
                <p class="max">▲ {linha.temperature_2m_max:.0f}{un_t}</p>
                <p class="min">▼ {linha.temperature_2m_min:.0f}{un_t}</p>
                <p class="chuva">💧 {linha.precipitation_probability_max:.0f}% · {linha.precipitation_sum:.1f} mm</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    fig_d = go.Figure()
    fig_d.add_trace(go.Scatter(x=diario["time"], y=diario["temperature_2m_max"], name="Máxima",
                               mode="lines+markers", line=dict(color=COR["temperatura"], width=3)))
    fig_d.add_trace(go.Scatter(x=diario["time"], y=diario["temperature_2m_min"], name="Mínima",
                               mode="lines+markers", line=dict(color=COR["chuva"], width=3),
                               fill="tonexty", fillcolor="rgba(167,139,250,0.15)"))
    st.plotly_chart(estilo_grafico(fig_d, 340, f"Faixa de temperatura diária ({un_t})"), use_container_width=True)

    fig_p = go.Figure(go.Bar(x=diario["time"], y=diario["precipitation_sum"], name="Chuva acumulada",
                             marker_color=COR["umidade"]))
    st.plotly_chart(estilo_grafico(fig_p, 300, "Chuva acumulada por dia (mm)"), use_container_width=True)

# ----------------------------------------------------------------------------
# Aba: Dados
# ----------------------------------------------------------------------------
with aba_dados:
    st.subheader("Previsão horária")
    tabela = proximas.rename(columns={
        "time": "Horário",
        "temperature_2m": f"Temperatura ({un_t})",
        "apparent_temperature": f"Sensação ({un_t})",
        "relative_humidity_2m": "Umidade (%)",
        "precipitation_probability": "Chance de chuva (%)",
        "wind_speed_10m": f"Vento ({un_v})",
    })
    st.dataframe(tabela, use_container_width=True, hide_index=True)
    st.download_button(
        "⬇️ Baixar CSV",
        tabela.to_csv(index=False).encode("utf-8"),
        file_name="previsao_horaria.csv",
        mime="text/csv",
    )
    with st.expander("Ver resposta bruta da API"):
        st.json(dados)

st.caption(f"Atualizado em {agora.strftime('%d/%m/%Y %H:%M')} (fuso {dados['timezone']}) · Fonte: open-meteo.com")
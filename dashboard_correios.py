import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import io
 
# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="📦 Correios - Integração de pacotes",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)
 
# ============================================================
# CSS CUSTOMIZADO
# ============================================================
st.markdown("""
<style>
    .main-header {
        font-size: 1.0rem;
        font-weight: bold;
        text-align: center;
        padding: 0.4rem;
        background: linear-gradient(90deg, #1a1a2e, #16213e, #0f3460);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .status-card {
        padding: 1.1rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        font-weight: bold;
        font-size: 1.2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .verde { background-color: #28a745; }
    .amarelo { background-color: #ffc107; color: #333; }
    .laranja { background-color: #fd7e14; }
    .vermelho { background-color: #dc3545; }
    .roxo { background-color: #6f42c1; }
    .metric-big {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
    }
    .alert-ruptura {
        background-color: #6f42c1;
        color: white;
        padding: 0.8rem;
        border-radius: 8px;
        text-align: center;
        font-size: 0.9rem;
        animation: pulse 1s infinite;
        border: 3px solid #ff0000;
    }
    @keyframes pulse {
        0% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.7; transform: scale(1.02); }
        100% { opacity: 1; transform: scale(1); }
    }
    .sirene {
        font-size: 1.3rem;
        animation: rotate 0.5s infinite;
    }
    @keyframes rotate {
        0% { transform: rotate(0deg); }
        25% { transform: rotate(15deg); }
        50% { transform: rotate(0deg); }
        75% { transform: rotate(-15deg); }
        100% { transform: rotate(0deg); }
    }
</style>
""", unsafe_allow_html=True)
 
# ============================================================
# CARREGAR DADOS
# ============================================================
@st.cache_data
def load_data():
    df = pd.read_excel("Base_Correios.xlsx")
    df['data'] = pd.to_datetime(df['data'])
    df['mes'] = df['data'].dt.to_period('M').astype(str)
    df['dia'] = df['data'].dt.strftime('%Y-%m-%d')
    return df
 
df = load_data()
 
# ============================================================
# FUNÇÕES DE CLASSIFICAÇÃO DE STATUS
# ============================================================
def classificar_status(qtd_nao_integrados):
    """Classifica o status baseado na quantidade de pacotes não integrados"""
    if qtd_nao_integrados == 0:
        return "🟢 NORMAL", "verde", "#28a745"
    elif 1 <= qtd_nao_integrados <= 4:
        return "🟡 ATENÇÃO", "amarelo", "#ffc107"
    elif 5 <= qtd_nao_integrados <= 10:
        return "🟠 ALTO RISCO", "laranja", "#fd7e14"
    elif 11 <= qtd_nao_integrados <= 49:
        return "🔴 CRÍTICO", "vermelho", "#dc3545"
    else:  # 50+
        return "🟣 RUPTURA", "roxo", "#6f42c1"
 
# ============================================================
# SIDEBAR - FILTROS
# ============================================================
st.sidebar.markdown("## 📮 Correios Brasil")
st.sidebar.markdown("---")
st.sidebar.header("⚙️ Filtros")
 
# Toggle para mostrar integrados ou não integrados
mostrar_integrados = st.sidebar.toggle("📦 Mostrar Pacotes Integrados", value=False)
 
# Filtro de data
data_min = df['data'].min().date()
data_max = df['data'].max().date()
date_range = st.sidebar.date_input(
    "📅 Período",
    value=(data_min, data_max),
    min_value=data_min,
    max_value=data_max
)
 
# ============================================================
# FILTRAR DADOS
# ============================================================
if len(date_range) == 2:
    mask = (df['data'].dt.date >= date_range[0]) & (df['data'].dt.date <= date_range[1])
    df_filtered = df[mask].copy()
else:
    df_filtered = df.copy()
 
# Separar integrados e não integrados
df_integrados = df_filtered[df_filtered['Status'] == 'integrado']
df_nao_integrados = df_filtered[df_filtered['Status'] != 'integrado']
 
# ============================================================
# HEADER PRINCIPAL
# ============================================================
st.markdown('<div class="main-header">📦 Correios - integração de pacotes</div>', unsafe_allow_html=True)
 
# ============================================================
# STATUS GERAL - SEMÁFORO
# ============================================================
st.markdown("##### 🚦 Status Geral")
 
qtd_nao_integrados = len(df_nao_integrados)
qtd_integrados = len(df_integrados)
total = len(df_filtered)
 
status_texto, status_classe, status_cor = classificar_status(qtd_nao_integrados)
 
# Mostrar alerta de RUPTURA com sirene
if qtd_nao_integrados >= 50:
    st.markdown(f"""
    <div class="alert-ruptura">
        <span class="sirene">🚨</span>
        <strong style="font-size: 0.9rem;"> ALERTA DE RUPTURA! </strong>
        <span class="sirene">🚨</span>
        <br><br>
        <span style="font-size: 1.2rem;">{qtd_nao_integrados}</span> pacotes não integrados!
        <br>
        <small>⏰ Delay de integração acima de 2 horas detectado - Ação imediata necessária!</small>
    </div>
    """, unsafe_allow_html=True)
    st.snow()
    time.sleep(0.5)
 
# Cards de métricas
col1, col2, col3, col4 = st.columns(4)
 
with col1:
    st.metric("📦 Total de Pacotes", total)
with col2:
    st.metric("✅ Integrados", qtd_integrados)
with col3:
    st.metric("❌ Não Integrados", qtd_nao_integrados)
with col4:
    st.metric("📊 Taxa de Integração", f"{(qtd_integrados/total*100):.1f}%" if total > 0 else "0%")
 
# Status visual - Cards de severidade
st.markdown("### 📊 Classificação de Severidade Atual")
 
col_status = st.columns(5)
categorias = [
    ("🟢 NORMAL", "0 pacotes", "verde", qtd_nao_integrados == 0),
    ("🟡 ATENÇÃO", "1 a 4 pacotes", "amarelo", 1 <= qtd_nao_integrados <= 4),
    ("🟠 ALTO RISCO", "5 a 10 pacotes", "laranja", 5 <= qtd_nao_integrados <= 10),
    ("🔴 CRÍTICO", "11 a 49 pacotes", "vermelho", 11 <= qtd_nao_integrados <= 49),
    ("🟣 RUPTURA", "50+ pacotes", "roxo", qtd_nao_integrados >= 50),
]
 
for i, (nome, desc, classe, ativo) in enumerate(categorias):
    with col_status[i]:
        opacity = "1" if ativo else "0.3"
        border = "3px solid white" if ativo else "none"
        st.markdown(f"""
        <div class="status-card {classe}" style="opacity: {opacity}; border: {border};">
            <div style="font-size: 1.5rem;">{nome}</div>
            <div style="font-size: 0.9rem; margin-top: 0.5rem;">{desc}</div>
            {"<div style='font-size: 2rem; margin-top: 0.5rem;'>⬆️ ATIVO</div>" if ativo else ""}
        </div>
        """, unsafe_allow_html=True)
 
st.markdown("---")
 
# ============================================================
# DELAY DE 2 HORAS (para status RUPTURA)
# ============================================================
if qtd_nao_integrados >= 50:
    st.markdown("### ⏰ Monitoramento de Delay - integração acima de 2 Horas")
    col_delay1, col_delay2 = st.columns(2)
    with col_delay1:
        st.error("🚨 **DELAY DETECTADO:** Mais de 50 pacotes com integração acima de 2 horas!")
        st.warning("⚠️ **Ação necessária:** Verificar sistema de integração dos Correios imediatamente.")
    with col_delay2:
        st.info("🕐 **Tempo desde último alerta:** 2h 00min")
        st.progress(100)
    st.markdown("---")
 
# ============================================================
# HISTÓRICO DE NÃO INTEGRAÇÃO
# ============================================================
st.markdown("## 📈 Histórico de Não Integração")
 
# Contagem por dia
historico_nao_int = df[df['Status'] != 'integrado'].groupby('dia').size().reset_index(name='nao_integrados')
historico_int = df[df['Status'] == 'integrado'].groupby('dia').size().reset_index(name='integrados')
 
# Merge para ter visão completa
historico_completo = df.groupby('dia').size().reset_index(name='total')
historico_completo = historico_completo.merge(historico_int, on='dia', how='left')
historico_completo = historico_completo.merge(historico_nao_int, on='dia', how='left')
historico_completo = historico_completo.fillna(0)
 
# Gráfico de histórico
fig_hist = go.Figure()
 
fig_hist.add_trace(go.Bar(
    x=historico_completo['dia'],
    y=historico_completo['integrados'],
    name='Integrados',
    marker_color='#28a745'
))
 
fig_hist.add_trace(go.Bar(
    x=historico_completo['dia'],
    y=historico_completo['nao_integrados'],
    name='Não Integrados',
    marker_color='#dc3545'
))
 
fig_hist.update_layout(
    title="Histórico Diário - Integrados vs Não Integrados",
    xaxis_title="Data",
    yaxis_title="Quantidade de Pacotes",
    barmode='stack',
    template='plotly_dark',
    height=400
)
 
st.plotly_chart(fig_hist, use_container_width=True)
 
st.markdown("---")
 
# ============================================================
# GRÁFICOS DE TENDÊNCIA
# ============================================================
st.markdown("## 📊 Gráficos de Tendência")
 
# --- Preparar dados de tendência ---
tendencia_diaria = df.groupby('dia').agg(
    total=('Tracking', 'count'),
    integrados=('Status', lambda x: (x == 'integrado').sum()),
    nao_integrados=('Status', lambda x: (x != 'integrado').sum())
).reset_index()
tendencia_diaria['dia'] = pd.to_datetime(tendencia_diaria['dia'])
tendencia_diaria = tendencia_diaria.sort_values('dia')
 
# Acumulado
tendencia_diaria['acumulado_total'] = tendencia_diaria['total'].cumsum()
tendencia_diaria['acumulado_nao_int'] = tendencia_diaria['nao_integrados'].cumsum()
 
# Média móvel (3 dias)
tendencia_diaria['media_movel_3d'] = tendencia_diaria['total'].rolling(window=3, min_periods=1).mean()
 
# Prefixo do tracking
df['prefixo'] = df['Tracking'].str[:5]
 
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Tendência Diária",
    "📊 Volume Acumulado",
    "🔄 Média Móvel",
    "📦 Por Tipo de Pacote"
])
 
# ============================================================
# TAB 1: TENDÊNCIA DIÁRIA
# ============================================================
with tab1:
    st.markdown("### 📈 Tendência Diária de Pacotes")
    fig_tend = go.Figure()
    fig_tend.add_trace(go.Scatter(
        x=tendencia_diaria['dia'],
        y=tendencia_diaria['total'],
        mode='lines+markers+text',
        name='Total Pacotes',
        line=dict(color='#0f3460', width=3),
        marker=dict(size=10),
        text=tendencia_diaria['total'],
        textposition='top center',
        textfont=dict(size=12, color='white')
    ))
    fig_tend.add_trace(go.Scatter(
        x=tendencia_diaria['dia'],
        y=tendencia_diaria['nao_integrados'],
        mode='lines+markers+text',
        name='Não Integrados',
        line=dict(color='#dc3545', width=3, dash='dash'),
        marker=dict(size=10, symbol='x'),
        text=tendencia_diaria['nao_integrados'],
        textposition='top center',
        textfont=dict(size=12, color='#dc3545')
    ))
    fig_tend.add_trace(go.Scatter(
        x=tendencia_diaria['dia'],
        y=tendencia_diaria['integrados'],
        mode='lines+markers+text',
        name='Integrados',
        line=dict(color='#28a745', width=3),
        marker=dict(size=10, symbol='diamond'),
        text=tendencia_diaria['integrados'],
        textposition='bottom center',
        textfont=dict(size=12, color='#28a745')
    ))
    fig_tend.add_hline(y=50, line_dash="dot", line_color="#6f42c1",
                       annotation_text="🟣 RUPTURA (50+)", annotation_position="top right")
    fig_tend.add_hline(y=11, line_dash="dot", line_color="#dc3545",
                       annotation_text="🔴 CRÍTICO (11-49)", annotation_position="top right")
    fig_tend.add_hline(y=5, line_dash="dot", line_color="#fd7e14",
                       annotation_text="🟠 ALTO RISCO (5-10)", annotation_position="top right")
    fig_tend.update_layout(
        title="Tendência Diária de Pacotes - Integrados vs Não Integrados",
        xaxis_title="Data",
        yaxis_title="Quantidade de Pacotes",
        template='plotly_dark',
        height=500,
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_tend, use_container_width=True)
    col_t1, col_t2, col_t3, col_t4 = st.columns(4)
    with col_t1:
        if len(tendencia_diaria) >= 2:
            variacao = tendencia_diaria['total'].iloc[-1] - tendencia_diaria['total'].iloc[-2]
            st.metric("📦 Hoje vs Ontem", tendencia_diaria['total'].iloc[-1], delta=int(variacao))
        else:
            st.metric("📦 Hoje", tendencia_diaria['total'].iloc[-1])
    with col_t2:
        st.metric("📊 Média Diária", f"{tendencia_diaria['total'].mean():.0f}")
    with col_t3:
        st.metric("📈 Máximo", f"{tendencia_diaria['total'].max():.0f}")
    with col_t4:
        st.metric("📉 Mínimo", f"{tendencia_diaria['total'].min():.0f}")
 
# ============================================================
# TAB 2: VOLUME ACUMULADO
# ============================================================
with tab2:
    st.markdown("### 📊 Volume Acumulado de Pacotes")
    fig_acum = go.Figure()
    fig_acum.add_trace(go.Scatter(
        x=tendencia_diaria['dia'],
        y=tendencia_diaria['acumulado_total'],
        mode='lines+markers',
        name='Acumulado Total',
        fill='tozeroy',
        line=dict(color='#0f3460', width=3),
        marker=dict(size=8),
        fillcolor='rgba(15, 52, 96, 0.3)'
    ))
    fig_acum.add_trace(go.Scatter(
        x=tendencia_diaria['dia'],
        y=tendencia_diaria['acumulado_nao_int'],
        mode='lines+markers',
        name='Acumulado Não Integrados',
        fill='tozeroy',
        line=dict(color='#dc3545', width=3, dash='dash'),
        marker=dict(size=8, symbol='x'),
        fillcolor='rgba(220, 53, 69, 0.3)'
    ))
    fig_acum.update_layout(
        title="Volume Acumulado ao Longo do Tempo",
        xaxis_title="Data",
        yaxis_title="Quantidade Acumulada",
        template='plotly_dark',
        height=450,
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_acum, use_container_width=True)
    st.markdown("#### 🔮 Projeção")
    if len(tendencia_diaria) >= 2:
        taxa_crescimento = tendencia_diaria['total'].pct_change().mean()
        projecao_7d = tendencia_diaria['acumulado_total'].iloc[-1] * (1 + taxa_crescimento) ** 7
        st.info(f"📈 **Taxa média de crescimento diário:** {taxa_crescimento*100:.1f}%")
        st.info(f"🔮 **Projeção acumulada em 7 dias:** ~{projecao_7d:.0f} pacotes")
 
# ============================================================
# TAB 3: MÉDIA MÓVEL
# ============================================================
with tab3:
    st.markdown("### 🔄 Média Móvel (3 dias)")
    fig_mm = go.Figure()
    fig_mm.add_trace(go.Bar(
        x=tendencia_diaria['dia'],
        y=tendencia_diaria['total'],
        name='Volume Diário',
        marker_color='rgba(15, 52, 96, 0.5)',
        text=tendencia_diaria['total'],
        textposition='auto'
    ))
    fig_mm.add_trace(go.Scatter(
        x=tendencia_diaria['dia'],
        y=tendencia_diaria['media_movel_3d'],
        mode='lines+markers',
        name='Média Móvel 3 dias',
        line=dict(color='#e74c3b', width=4),
        marker=dict(size=10)
    ))
    media_geral = tendencia_diaria['total'].mean()
    fig_mm.add_hline(y=media_geral, line_dash="dot", line_color="#ffc107",
                     annotation_text=f"Média Geral: {media_geral:.0f}",
                     annotation_position="top right")
    fig_mm.update_layout(
        title="Volume Diário com Média Móvel de 3 Dias",
        xaxis_title="Data",
        yaxis_title="Quantidade de Pacotes",
        template='plotly_dark',
        height=450,
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_mm, use_container_width=True)
    st.markdown("#### 📊 Análise de Tendência")
    if len(tendencia_diaria) >= 3:
        ultimo_valor = tendencia_diaria['media_movel_3d'].iloc[-1]
        penultimo_valor = tendencia_diaria['media_movel_3d'].iloc[-2]
        if ultimo_valor > penultimo_valor:
            st.warning(f"⬆️ **Tendência de ALTA** - Média móvel subindo de {penultimo_valor:.0f} para {ultimo_valor:.0f}")
        elif ultimo_valor < penultimo_valor:
            st.success(f"⬇️ **Tendência de QUEDA** - Média móvel caindo de {penultimo_valor:.0f} para {ultimo_valor:.0f}")
        else:
            st.info(f"➡️ **Tendência ESTÁVEL** - Média móvel em {ultimo_valor:.0f}")
 
# ============================================================
# TAB 4: POR TIPO DE PACOTE (PREFIXO)
# ============================================================
with tab4:
    st.markdown("### 📦 Tendência por Tipo de Pacote (Prefixo)")
    tend_prefixo = df.groupby([df['data'].dt.strftime('%Y-%m-%d'), 'prefixo']).size().reset_index(name='quantidade')
    tend_prefixo.columns = ['dia', 'prefixo', 'quantidade']
    tend_prefixo['dia'] = pd.to_datetime(tend_prefixo['dia'])
    tend_prefixo = tend_prefixo.sort_values('dia')
    fig_prefixo = go.Figure()
    cores = {'TJ225': '#0f3460', 'QS637': '#e74c3b', 'QS636': '#f39c1d', 'QS635': '#6c5ce7'}
    for prefixo in tend_prefixo['prefixo'].unique():
        df_pref = tend_prefixo[tend_prefixo['prefixo'] == prefixo]
        fig_prefixo.add_trace(go.Scatter(
            x=df_pref['dia'],
            y=df_pref['quantidade'],
            mode='lines+markers+text',
            name=f'Série {prefixo}',
            line=dict(width=3, color=cores.get(prefixo, '#ffffff')),
            marker=dict(size=10),
            text=df_pref['quantidade'],
            textposition='top center'
        ))
    fig_prefixo.update_layout(
        title="Volume por Série de Tracking ao Longo do Tempo",
        xaxis_title="Data",
        yaxis_title="Quantidade de Pacotes",
        template='plotly_dark',
        height=450,
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_prefixo, use_container_width=True)
    col_pizza1, col_pizza2 = st.columns(2)
    with col_pizza1:
        dist_prefixo = df.groupby('prefixo').size().reset_index(name='quantidade')
        fig_pizza = go.Figure(data=[go.Pie(
            labels=dist_prefixo['prefixo'],
            values=dist_prefixo['quantidade'],
            hole=0.4,
            marker_colors=['#0f3460', '#e74c3b', '#f39c1d', '#6c5ce7'],
            textinfo='label+percent+value'
        )])
        fig_pizza.update_layout(
            title="Distribuição por Série de Tracking",
            template='plotly_dark',
            height=350
        )
        st.plotly_chart(fig_pizza, use_container_width=True)
    with col_pizza2:
        resumo_prefixo = df.groupby('prefixo').agg(
            total=('Tracking', 'count'),
            primeiro_dia=('data', 'min'),
            ultimo_dia=('data', 'max')
        ).reset_index()
        resumo_prefixo['primeiro_dia'] = resumo_prefixo['primeiro_dia'].dt.strftime('%d/%m/%Y')
        resumo_prefixo['ultimo_dia'] = resumo_prefixo['ultimo_dia'].dt.strftime('%d/%m/%Y')
        resumo_prefixo.columns = ['Série', 'Total Pacotes', 'Primeiro Registro', 'Último Registro']
        st.markdown("#### 📋 Resumo por Série")
        st.dataframe(resumo_prefixo, use_container_width=True, hide_index=True)
 
# ============================================================
# VARIAÇÃO PERCENTUAL DIA A DIA
# ============================================================
st.markdown("---")
st.markdown("### 📉 Variação Percentual Dia a Dia")
 
tendencia_diaria['variacao_pct'] = tendencia_diaria['total'].pct_change() * 100
 
fig_var = go.Figure()
 
cores_var = ['#28a745' if v <= 0 else '#dc3545' for v in tendencia_diaria['variacao_pct'].fillna(0)]
 
fig_var.add_trace(go.Bar(
    x=tendencia_diaria['dia'],
    y=tendencia_diaria['variacao_pct'],
    marker_color=cores_var,
    text=[f"{v:.1f}%" if pd.notna(v) else "—" for v in tendencia_diaria['variacao_pct']],
    textposition='auto',
    name='Variação %'
))
 
fig_var.add_hline(y=0, line_color="white", line_width=2)
 
fig_var.update_layout(
    title="Variação Percentual Diária (Verde = Redução | Vermelho = Aumento)",
    xaxis_title="Data",
    yaxis_title="Variação (%)",
    template='plotly_dark',
    height=350
)
 
st.plotly_chart(fig_var, use_container_width=True)
 
st.markdown("---")
 
# ============================================================
# TOGGLE - PACOTES INTEGRADOS vs NÃO INTEGRADOS
# ============================================================
st.markdown("## 🔄 Visualização de Pacotes")
 
if mostrar_integrados:
    st.success("✅ Exibindo **Pacotes Integrados**")
    df_display = df_integrados
else:
    st.error("❌ Exibindo **Pacotes Não Integrados**")
    df_display = df_nao_integrados
 
st.info(f"📊 Total de registros: **{len(df_display)}**")
 
if len(df_display) > 0:
    st.dataframe(
        df_display[['data', 'Tracking', 'Status']].sort_values('data', ascending=False),
        use_container_width=True,
        height=300
    )
else:
    st.warning(f"Nenhum pacote {'integrado' if mostrar_integrados else 'não integrado'} encontrado no período selecionado.")
 
st.markdown("---")
 
# ============================================================
# VISÃO MENSAL - DRILL DOWN (Mês → Dia → Tracking ID)
# ============================================================
st.markdown("## 📅 Visão Mensal - Pacotes Não Integrados")
st.caption("Selecione o mês para ver os dias, e o dia para ver os Tracking IDs")
 
df_drill = df_filtered.copy()
 
meses_disponiveis = sorted(df_drill['mes'].unique())
mes_selecionado = st.selectbox("📆 Selecione o Mês:", meses_disponiveis, index=len(meses_disponiveis)-1)
 
if mes_selecionado:
    df_mes = df_drill[df_drill['mes'] == mes_selecionado]
    contagem_dia = df_mes.groupby('dia').agg(
        total=('Tracking', 'count'),
        integrados=('Status', lambda x: (x == 'integrado').sum()),
        nao_integrados=('Status', lambda x: (x != 'integrado').sum())
    ).reset_index()
    fig_dia = go.Figure()
    fig_dia.add_trace(go.Bar(
        x=contagem_dia['dia'],
        y=contagem_dia['total'],
        name='Total Pacotes',
        marker_color='#0f3460',
        text=contagem_dia['total'],
        textposition='auto'
    ))
    if contagem_dia['nao_integrados'].sum() > 0:
        fig_dia.add_trace(go.Bar(
            x=contagem_dia['dia'],
            y=contagem_dia['nao_integrados'],
            name='Não Integrados',
            marker_color='#dc3545',
            text=contagem_dia['nao_integrados'],
            textposition='auto'
        ))
    fig_dia.update_layout(
        title=f"📊 Pacotes por Dia - {mes_selecionado}",
        xaxis_title="Dia",
        yaxis_title="Quantidade",
        template='plotly_dark',
        height=350,
        barmode='group'
    )
    st.plotly_chart(fig_dia, use_container_width=True)
    dias_disponiveis = sorted(df_mes['dia'].unique())
    dia_selecionado = st.selectbox("📅 Selecione o Dia para ver Tracking IDs:", dias_disponiveis)
    if dia_selecionado:
        df_dia = df_mes[df_mes['dia'] == dia_selecionado]
        col_info1, col_info2, col_info3 = st.columns(3)
        with col_info1:
            st.metric("Total no dia", len(df_dia))
        with col_info2:
            st.metric("Integrados", len(df_dia[df_dia['Status'] == 'integrado']))
        with col_info3:
            nao_int_dia = len(df_dia[df_dia['Status'] != 'integrado'])
            st.metric("Não Integrados", nao_int_dia)
        st.markdown(f"#### 🔍 Tracking IDs - {dia_selecionado}")
        st.dataframe(
            df_dia[['Tracking', 'Status']].reset_index(drop=True),
            use_container_width=True,
            height=300
        )
 
st.markdown("---")
 
# ============================================================
# DOWNLOAD DA BASE
# ============================================================
st.markdown("## 📥 Download da Base de Dados")
 
col_dl1, col_dl2 = st.columns(2)
 
with col_dl1:
    st.markdown("### 📄 Base Completa")
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Pacotes')
    st.download_button(
        label="⬇️ Baixar Base Completa (Excel)",
        data=buffer.getvalue(),
        file_name=f"base_correios_completa_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
 
with col_dl2:
    st.markdown("### 📄 Apenas Não Integrados")
    buffer2 = io.BytesIO()
    df_nao_int_download = df[df['Status'] != 'integrado']
    if len(df_nao_int_download) > 0:
        with pd.ExcelWriter(buffer2, engine='openpyxl') as writer:
            df_nao_int_download.to_excel(writer, index=False, sheet_name='Não Integrados')
        st.download_button(
            label="⬇️ Baixar Não Integrados (Excel)",
            data=buffer2.getvalue(),
            file_name=f"base_nao_integrados_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("✅ Não há pacotes não integrados para download!")
 
st.markdown("### 📄 Download em CSV")
csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="⬇️ Baixar Base Completa (CSV)",
    data=csv,
    file_name=f"base_correios_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
    mime="text/csv"
)
 
st.markdown("---")
 
# ============================================================
# FOOTER
# ============================================================
st.markdown(f"""
<div style="text-align: center; padding: 2rem; color: #666;">
    <p>📦 Correios - integração de pacotes | Atualizado em tempo real</p>
    <p>🔄 Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
</div>
""", unsafe_allow_html=True)

import streamlit as st
import requests
import json
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from j1939_decoder import J1939Decoder

# Configuração da página
st.set_page_config(
    page_title="Monitor CAN Bus - John Deere",
    page_icon="🚜",
    layout="wide"
)

# Estilo personalizado
st.markdown("""
    <style>
        .main {
            background-color: #367C2B;
        }
        .stApp {
            background: linear-gradient(180deg, #367C2B 0%, #2B5E22 100%);
        }
        .css-1d391kg {
            background-color: rgba(255,255,255,0.1);
        }
        h1, h2 {
            color: #FFDE00 !important;
        }
    </style>
""", unsafe_allow_html=True)

def init_session_state():
    if 'can_data' not in st.session_state:
        st.session_state.can_data = []
    if 'connected' not in st.session_state:
        st.session_state.connected = False
    if 'esp32_ip' not in st.session_state:
        st.session_state.esp32_ip = ""
    if 'auto_update' not in st.session_state:
        st.session_state.auto_update = False
    if 'running' not in st.session_state:
        st.session_state.running = True

def connect_to_esp32(ip):
    try:
        if not ip:
            st.error("Digite o IP do ESP32")
            return False
            
        # Salva o IP na session_state
        st.session_state.esp32_ip = ip
        
        # Tenta conectar
        url = f"http://{ip}/status"
        st.info(f"Tentando conectar em: {url}")
        
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            st.success(f"Conectado ao ESP32 no IP: {ip}")
            st.session_state.connected = True
            st.session_state.auto_update = True
            return True
    except requests.exceptions.ConnectionError:
        st.error(f"Não foi possível conectar ao ESP32 no IP: {ip}")
        st.session_state.connected = False
    except Exception as e:
        st.error(f"Erro ao conectar: {str(e)}")
        st.session_state.connected = False
    return False

def fetch_can_data():
    if not st.session_state.connected or not st.session_state.esp32_ip:
        return None
        
    try:
        url = f"http://{st.session_state.esp32_ip}/data"
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            data = response.json()
            if data.get("current"):
                st.session_state.can_data.append(data["current"])
                if len(st.session_state.can_data) > 100:
                    st.session_state.can_data.pop(0)
            return data
    except requests.exceptions.ConnectionError:
        st.warning("Conexão perdida com ESP32")
        st.session_state.connected = False
    except Exception as e:
        st.warning(f"Erro ao obter dados: {str(e)}")
    return None

def create_gauge(value, title, unit, min_val, max_val):
    """Cria gauge com estilo John Deere"""
    return go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = value,
        title = {'text': f"{title}<br><span style='font-size:0.8em'>{unit}</span>",
                'font': {'color': '#FFDE00'}},
        number = {'suffix': f" {unit}"},
        gauge = {
            'axis': {'range': [min_val, max_val], 
                    'tickcolor': "#FFDE00",
                    'tickwidth': 2},
            'bar': {'color': "#367C2B"},
            'bgcolor': "rgba(255,255,255,0.1)",
            'borderwidth': 2,
            'bordercolor': "#FFDE00",
            'steps': [
                {'range': [0, max_val*0.6], 'color': 'rgba(0,255,0,0.1)'},
                {'range': [max_val*0.6, max_val*0.8], 'color': 'rgba(255,255,0,0.1)'},
                {'range': [max_val*0.8, max_val], 'color': 'rgba(255,0,0,0.1)'}
            ]
        }
    ))

def create_time_series(data_history, param_name, unit):
    """Cria gráfico de série temporal"""
    times = [d['timestamp'] for d in data_history]
    values = [d['decoded']['values'][param_name]['value'] 
             for d in data_history if param_name in d.get('decoded', {}).get('values', {})]
    
    return go.Figure(data=go.Scatter(
        x=times,
        y=values,
        mode='lines+markers',
        name=param_name,
        line={'color': '#FFDE00'}
    )).update_layout(
        title=f"{param_name.replace('_', ' ').title()} vs Tempo",
        xaxis_title="Tempo",
        yaxis_title=unit,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#FFDE00'}
    )

def main():
    init_session_state()
    
    # Header
    st.title("Monitor CAN Bus John Deere")
    st.markdown("### Sistema de Monitoramento de Implementos Agrícolas")
    
    # Sidebar para configuração
    with st.sidebar:
        st.header("Configurações")
        
        # Controle de execução
        if st.button("🛑 Parar" if st.session_state.running else "▶️ Iniciar"):
            st.session_state.running = not st.session_state.running
            if not st.session_state.running:
                st.warning("Monitoramento pausado")
            else:
                st.success("Monitoramento iniciado")
        
        # Mostra IP atual se conectado
        if st.session_state.connected:
            st.success(f"Conectado ao IP: {st.session_state.esp32_ip}")
        
        # Input do IP
        ip_input = st.text_input(
            "IP do ESP32",
            value=st.session_state.esp32_ip,
            key="esp32_ip_input"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Conectar"):
                connect_to_esp32(ip_input)
        with col2:
            st.session_state.auto_update = st.checkbox(
                "Auto Atualizar", 
                value=st.session_state.auto_update
            )
    
    # Layout principal
    if st.session_state.running:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Dados em Tempo Real")
            if st.session_state.connected:
                data = fetch_can_data() if st.session_state.auto_update else None
                
                if data and data.get("current"):
                    current = data["current"]
                    
                    # Decodifica mensagem
                    decoded = J1939Decoder.decode_message(current["pgn"], current["data"])
                    if decoded:
                        current['decoded'] = decoded
                        
                        st.subheader(f"📊 {decoded['name']}")
                        
                        # Cria gauges para cada parâmetro
                        cols = st.columns(len(decoded['values']))
                        for i, (param_name, param_info) in enumerate(decoded['values'].items()):
                            with cols[i]:
                                fig = create_gauge(
                                    param_info['value'],
                                    param_name.replace('_', ' ').title(),
                                    param_info['unit'],
                                    param_info['range'][0],
                                    param_info['range'][1]
                                )
                                st.plotly_chart(fig, use_container_width=True)
                        
                        # Gráficos de histórico
                        st.subheader("📈 Histórico")
                        for param_name, param_info in decoded['values'].items():
                            fig = create_time_series(
                                st.session_state.can_data,
                                param_name,
                                param_info['unit']
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    
                    # Dados brutos
                    with st.expander("🔍 Dados Brutos"):
                        st.metric("PGN", current["pgn"])
                        st.metric("Origem", f"0x{current['source']:02X}")
                        st.metric("Prioridade", current["priority"])
                        st.text("Dados Hexadecimais:")
                        hex_data = " ".join([f"{x:02X}" for x in current["data"]])
                        st.code(hex_data)
            else:
                st.info("Aguardando conexão com ESP32...")
            
        with col2:
            st.subheader("Histórico")
            if st.session_state.can_data:
                df = pd.DataFrame(st.session_state.can_data)
                st.dataframe(df)
        
        # Atualização automática
        if st.session_state.auto_update and st.session_state.running:
            st.rerun()
    else:
        st.warning("Monitoramento está pausado. Clique em Iniciar para continuar.")

if __name__ == "__main__":
    main() 
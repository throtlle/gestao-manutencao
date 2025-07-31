
import streamlit as st
import pandas as pd
import datetime

# ================== CONFIG ==================
st.set_page_config(page_title="Gestão de Confiabilidade", layout="wide")
st.markdown(
    """
    <style>
    .main {background-color: #f9f9f9;}
    .stButton>button {background-color: #4CAF50; color:white; border-radius:8px; height:3em; width:100%;}
    .stSidebar {background-color: #f1f3f6;}
    </style>
    """, unsafe_allow_html=True)

# ================== LOGIN ==================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    user = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if user == "admin" and password == "123":
            st.session_state.logged_in = True
        else:
            st.error("Usuário ou senha incorretos!")

if not st.session_state.logged_in:
    st.title("🔐 Login do Sistema")
    login()
    st.stop()

# ================== BANCO EM MEMÓRIA ==================
if "equipamentos" not in st.session_state:
    st.session_state.equipamentos = pd.DataFrame(columns=["ID","Nome","Localização"])
if "falhas" not in st.session_state:
    st.session_state.falhas = pd.DataFrame(columns=["Equipamento","Data Falha","Data Reparo"])

# ================== FUNÇÕES ==================
def calcular_indicadores():
    if len(st.session_state.falhas) == 0:
        return pd.DataFrame(columns=["Equipamento","MTTR","MTBF","Disponibilidade"])
    indicadores = []
    for equip in st.session_state.equipamentos["Nome"].unique():
        df_eq = st.session_state.falhas[st.session_state.falhas["Equipamento"]==equip]
        if len(df_eq) < 1: 
            continue
        df_eq = df_eq.sort_values("Data Falha")
        tempos_reparo = (df_eq["Data Reparo"] - df_eq["Data Falha"]).dt.total_seconds()/3600
        mttr = tempos_reparo.mean()
        tempos_entre_falhas = df_eq["Data Falha"].sort_values().diff().dt.total_seconds()/3600
        mtbf = tempos_entre_falhas[1:].mean() if len(tempos_entre_falhas)>1 else 0
        disponibilidade = (mtbf/(mtbf+mttr)*100) if (mtbf and mttr) else 0
        indicadores.append({"Equipamento":equip,"MTTR":mttr,"MTBF":mtbf,"Disponibilidade":disponibilidade})
    return pd.DataFrame(indicadores)

def gerar_relatorio_html(linha):
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial; margin: 40px; }}
            h1 {{ text-align: center; color: #4CAF50; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h1>Relatório Individual - {linha['Equipamento']}</h1>
        <p><b>Data de emissão:</b> {datetime.date.today()}</p>
        <table>
            <tr><th>MTTR (h)</th><td>{linha['MTTR']:.2f}</td></tr>
            <tr><th>MTBF (h)</th><td>{linha['MTBF']:.2f}</td></tr>
            <tr><th>Disponibilidade (%)</th><td>{linha['Disponibilidade']:.2f}</td></tr>
        </table>
    </body>
    </html>
    """
    return html

# ================== SIDEBAR ==================
menu = st.sidebar.radio("Menu", ["Cadastro Equipamento","Registro Falha","Dashboard","Relatório Individual","Sair"])

# ================== CADASTRO EQUIPAMENTO ==================
if menu == "Cadastro Equipamento":
    st.title("Cadastro de Equipamentos")
    nome = st.text_input("Nome do equipamento")
    local = st.text_input("Localização")
    if st.button("Salvar equipamento"):
        if nome:
            novo_id = len(st.session_state.equipamentos)+1
            st.session_state.equipamentos.loc[len(st.session_state.equipamentos)] = [novo_id, nome, local]
            st.success("Equipamento cadastrado!")
    st.dataframe(st.session_state.equipamentos, use_container_width=True)

# ================== REGISTRO FALHA ==================
elif menu == "Registro Falha":
    st.title("Registro de Falhas e Reparos")
    if len(st.session_state.equipamentos)==0:
        st.warning("Cadastre um equipamento primeiro!")
    else:
        equip = st.selectbox("Equipamento", st.session_state.equipamentos["Nome"])
        data_falha = st.date_input("Data da Falha", datetime.date.today())
        data_reparo = st.date_input("Data do Reparo", datetime.date.today())
        if st.button("Salvar falha"):
            st.session_state.falhas.loc[len(st.session_state.falhas)] = [equip, pd.to_datetime(data_falha), pd.to_datetime(data_reparo)]
            st.success("Falha registrada!")
    st.dataframe(st.session_state.falhas, use_container_width=True)

# ================== DASHBOARD ==================
elif menu == "Dashboard":
    st.title("📊 Dashboard de Confiabilidade")
    indicadores = calcular_indicadores()
    if len(indicadores)==0:
        st.warning("Nenhum dado de falhas disponível.")
    else:
        col1,col2,col3 = st.columns(3)
        col1.metric("MTTR Médio", f"{indicadores['MTTR'].mean():.2f} h")
        col2.metric("MTBF Médio", f"{indicadores['MTBF'].mean():.2f} h")
        col3.metric("Disponibilidade Média", f"{indicadores['Disponibilidade'].mean():.2f}%")
        st.subheader("Indicadores por Equipamento")
        st.dataframe(indicadores, use_container_width=True)
        st.subheader("Disponibilidade por Equipamento")
        st.bar_chart(indicadores.set_index("Equipamento")["Disponibilidade"])

# ================== RELATÓRIO INDIVIDUAL ==================
elif menu == "Relatório Individual":
    st.title("Relatório Individual")
    indicadores = calcular_indicadores()
    if len(indicadores)==0:
        st.warning("Nenhum dado disponível.")
    else:
        equip = st.selectbox("Equipamento", indicadores["Equipamento"])
        linha = indicadores[indicadores["Equipamento"]==equip].iloc[0]
        html = gerar_relatorio_html(linha)
        st.download_button("Baixar Relatório HTML", data=html, file_name=f"relatorio_{equip}.html", mime="text/html")
        st.info("Abra o arquivo HTML baixado, pressione CTRL+P e escolha 'Salvar como PDF'.")

# ================== SAIR ==================
elif menu == "Sair":
    st.session_state.logged_in = False
    st.experimental_rerun()

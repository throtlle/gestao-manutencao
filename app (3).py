
import streamlit as st
import pandas as pd
from io import BytesIO

# ================== CONFIG ==================
st.set_page_config(page_title="Gestão de Manutenção", layout="wide")

# Estilo básico
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
    st.session_state.equipamentos = pd.DataFrame(columns=["ID", "Nome", "Localização"])
if "ordens" not in st.session_state:
    st.session_state.ordens = pd.DataFrame(columns=["ID", "Equipamento", "Descrição", "Status"])

# ================== SIDEBAR ==================
menu = st.sidebar.radio("Menu", ["Dashboard", "Equipamentos", "Ordens de Manutenção", "Importar Planilha", "Exportar Dados", "Sair"])

# ================== DASHBOARD ==================
if menu == "Dashboard":
    st.title("📊 Painel de Controle")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Equipamentos", len(st.session_state.equipamentos))
    col2.metric("Total de Ordens", len(st.session_state.ordens))
    pendentes = len(st.session_state.ordens[st.session_state.ordens["Status"] == "Pendente"])
    col3.metric("Ordens Pendentes", pendentes)
    
    if len(st.session_state.ordens) > 0:
        st.subheader("Distribuição de Ordens por Status")
        st.bar_chart(st.session_state.ordens["Status"].value_counts())

# ================== EQUIPAMENTOS ==================
elif menu == "Equipamentos":
    st.title("Cadastro de Equipamentos")
    nome = st.text_input("Nome do equipamento")
    local = st.text_input("Localização")
    if st.button("Adicionar equipamento"):
        novo_id = len(st.session_state.equipamentos) + 1
        st.session_state.equipamentos.loc[len(st.session_state.equipamentos)] = [novo_id, nome, local]
        st.success("Equipamento adicionado!")
    st.dataframe(st.session_state.equipamentos, use_container_width=True)

# ================== ORDENS ==================
elif menu == "Ordens de Manutenção":
    st.title("Registro de Ordens de Manutenção")
    if len(st.session_state.equipamentos) == 0:
        st.warning("Cadastre primeiro um equipamento!")
    else:
        equipamento = st.selectbox("Equipamento", st.session_state.equipamentos["Nome"])
        descricao = st.text_area("Descrição da manutenção")
        if st.button("Criar ordem"):
            novo_id = len(st.session_state.ordens) + 1
            st.session_state.ordens.loc[len(st.session_state.ordens)] = [novo_id, equipamento, descricao, "Pendente"]
            st.success("Ordem criada!")
    st.subheader("Ordens existentes")
    st.dataframe(st.session_state.ordens, use_container_width=True)

# ================== IMPORTAÇÃO ==================
elif menu == "Importar Planilha":
    st.title("Importar Dados de Planilha")
    arquivo = st.file_uploader("Selecione um arquivo Excel", type=["xls", "xlsx", "xlsm"])
    if arquivo is not None:
        df_importado = pd.read_excel(arquivo)
        st.write("Pré-visualização dos dados importados:")
        st.dataframe(df_importado.head(), use_container_width=True)
        if st.button("Usar como base de equipamentos"):
            st.session_state.equipamentos = df_importado.copy()
            st.success("Dados de equipamentos carregados com sucesso!")

# ================== EXPORTAÇÃO CSV ==================
elif menu == "Exportar Dados":
    st.title("Exportar Dados")
    csv_equip = st.session_state.equipamentos.to_csv(index=False).encode('utf-8')
    csv_ordens = st.session_state.ordens.to_csv(index=False).encode('utf-8')

    st.download_button("Baixar Equipamentos (CSV)", csv_equip, "equipamentos.csv", "text/csv")
    st.download_button("Baixar Ordens (CSV)", csv_ordens, "ordens.csv", "text/csv")

# ================== SAIR ==================
elif menu == "Sair":
    st.session_state.logged_in = False
    st.experimental_rerun()

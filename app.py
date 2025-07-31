
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
    st.session_state.equipamentos = pd.DataFrame(columns=["Nome", "Localização", "MTTR", "MTBF", "Disponibilidade"])

# ================== FUNÇÃO RELATÓRIO HTML ==================
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
        <h1>Relatório Individual - {linha['Nome']}</h1>
        <p><b>Data de emissão:</b> {datetime.date.today()}</p>
        <table>
            <tr><th>Localização</th><td>{linha['Localização']}</td></tr>
            <tr><th>MTTR</th><td>{linha['MTTR']}</td></tr>
            <tr><th>MTBF</th><td>{linha['MTBF']}</td></tr>
            <tr><th>Disponibilidade</th><td>{linha['Disponibilidade']}%</td></tr>
        </table>
    </body>
    </html>
    """
    return html

# ================== SIDEBAR ==================
menu = st.sidebar.radio("Menu", ["Importar Dados", "Dashboard Confiabilidade", "Relatório Individual", "Sair"])

# ================== IMPORTAÇÃO ==================
if menu == "Importar Dados":
    st.title("Importar Dados de Confiabilidade")
    arquivo = st.file_uploader("Selecione um arquivo Excel", type=["xls", "xlsx", "xlsm"])
    if arquivo is not None:
        df_importado = pd.read_excel(arquivo)
        st.write("Pré-visualização dos dados importados:")
        st.dataframe(df_importado.head(), use_container_width=True)
        if st.button("Usar como base de equipamentos"):
            st.session_state.equipamentos = df_importado.copy()
            st.success("Dados carregados com sucesso!")

# ================== DASHBOARD ==================
elif menu == "Dashboard Confiabilidade":
    st.title("📊 Dashboard de Confiabilidade")
    if len(st.session_state.equipamentos) == 0:
        st.warning("Nenhum dado carregado.")
    else:
        mttr_medio = st.session_state.equipamentos["MTTR"].mean()
        mtbf_medio = st.session_state.equipamentos["MTBF"].mean()
        disp_medio = st.session_state.equipamentos["Disponibilidade"].mean()

        col1, col2, col3 = st.columns(3)
        col1.metric("MTTR Médio", f"{mttr_medio:.2f}")
        col2.metric("MTBF Médio", f"{mtbf_medio:.2f}")
        col3.metric("Disponibilidade Média", f"{disp_medio:.2f}%")

        st.subheader("Disponibilidade por Equipamento")
        st.bar_chart(st.session_state.equipamentos.set_index("Nome")["Disponibilidade"])

        st.subheader("Tabela Completa")
        st.dataframe(st.session_state.equipamentos, use_container_width=True)

# ================== RELATÓRIO INDIVIDUAL ==================
elif menu == "Relatório Individual":
    st.title("Gerar Relatório Individual (HTML → PDF)")
    if len(st.session_state.equipamentos) == 0:
        st.warning("Nenhum dado carregado.")
    else:
        equipamento = st.selectbox("Selecione o equipamento", st.session_state.equipamentos["Nome"])
        linha = st.session_state.equipamentos[st.session_state.equipamentos["Nome"] == equipamento].iloc[0]
        html = gerar_relatorio_html(linha)
        st.download_button("Baixar Relatório HTML", data=html, file_name=f"relatorio_{equipamento}.html", mime="text/html")
        st.info("Abra o arquivo HTML baixado, pressione CTRL+P e escolha 'Salvar como PDF'.")

# ================== SAIR ==================
elif menu == "Sair":
    st.session_state.logged_in = False
    st.experimental_rerun()

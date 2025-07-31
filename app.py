
import streamlit as st
import pandas as pd
from io import BytesIO

# Configuração da página
st.set_page_config(page_title="Gestão de Manutenção", layout="wide")

# Inicializa bancos de dados em memória
if "equipamentos" not in st.session_state:
    st.session_state.equipamentos = pd.DataFrame(columns=["ID", "Nome", "Localização"])
if "ordens" not in st.session_state:
    st.session_state.ordens = pd.DataFrame(columns=["ID", "Equipamento", "Descrição", "Status"])

# Menu lateral
menu = st.sidebar.radio("Menu", ["Equipamentos", "Ordens de Manutenção", "Relatórios", "Exportar Dados"])

# Cadastro de equipamentos
if menu == "Equipamentos":
    st.header("Cadastro de Equipamentos")
    nome = st.text_input("Nome do equipamento")
    local = st.text_input("Localização")
    if st.button("Adicionar equipamento"):
        novo_id = len(st.session_state.equipamentos) + 1
        st.session_state.equipamentos.loc[len(st.session_state.equipamentos)] = [novo_id, nome, local]
        st.success("Equipamento adicionado!")
    st.dataframe(st.session_state.equipamentos)

# Ordens de manutenção
elif menu == "Ordens de Manutenção":
    st.header("Registro de Ordens de Manutenção")
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
    st.dataframe(st.session_state.ordens)

# Relatórios
elif menu == "Relatórios":
    st.header("Relatórios de Manutenção")
    st.write(f"Total de equipamentos: {len(st.session_state.equipamentos)}")
    st.write(f"Total de ordens: {len(st.session_state.ordens)}")
    if len(st.session_state.ordens) > 0:
        st.bar_chart(st.session_state.ordens["Status"].value_counts())

# Exportação de dados
else:
    st.header("Exportar Dados")
    with BytesIO() as buffer:
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            st.session_state.equipamentos.to_excel(writer, sheet_name="Equipamentos", index=False)
            st.session_state.ordens.to_excel(writer, sheet_name="Ordens", index=False)
        st.download_button("Baixar Excel", buffer.getvalue(), "dados_manutencao.xlsx")

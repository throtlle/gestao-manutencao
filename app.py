
import streamlit as st
import pandas as pd
import requests
import urllib.parse

# ================== CONFIG ==================
st.set_page_config(page_title="Gestão + Salesforce OAuth", layout="wide")

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

# ================== SIDEBAR ==================
menu = st.sidebar.radio("Menu", ["Salesforce OAuth","Sair"])

# ================== SALESFORCE OAUTH ==================
if menu == "Salesforce OAuth":
    st.title("Conexão OAuth 2.0 com Salesforce")

    consumer_key = st.text_input("Consumer Key (Client ID)")
    consumer_secret = st.text_input("Consumer Secret", type="password")
    callback_url = st.text_input("Callback URL", value="https://throtlle-gestao-manutencao-app-w7byxp.streamlit.app")
    instance_url = "https://login.salesforce.com"

    if st.button("Conectar ao Salesforce"):
        if not consumer_key or not consumer_secret:
            st.warning("Preencha o Consumer Key e Secret.")
        else:
            # Monta URL de autorização
            auth_url = (
                f"{instance_url}/services/oauth2/authorize?response_type=code"
                f"&client_id={urllib.parse.quote(consumer_key)}"
                f"&redirect_uri={urllib.parse.quote(callback_url)}"
            )
            st.markdown(f"[Clique aqui para autenticar no Salesforce]({auth_url})")

    # Campo para colar o "code" retornado
    auth_code = st.text_input("Cole aqui o 'code' retornado pelo Salesforce")
    if auth_code and st.button("Obter Token de Acesso"):
        token_url = f"{instance_url}/services/oauth2/token"
        data = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "client_id": consumer_key,
            "client_secret": consumer_secret,
            "redirect_uri": callback_url
        }
        response = requests.post(token_url, data=data)
        if response.status_code == 200:
            tokens = response.json()
            st.success("Token de acesso obtido com sucesso!")
            st.json(tokens)
            st.session_state.salesforce_token = tokens["access_token"]
            st.session_state.salesforce_instance = tokens["instance_url"]
        else:
            st.error(f"Erro ao obter token: {response.text}")

    # Exemplo de consulta
    if "salesforce_token" in st.session_state:
        if st.button("Buscar dados de exemplo (Ativos)"):
            query = "SELECT Id, Name FROM Asset LIMIT 10"
            url = f"{st.session_state.salesforce_instance}/services/data/v57.0/query?q={urllib.parse.quote(query)}"
            headers = {"Authorization": f"Bearer {st.session_state.salesforce_token}"}
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                df = pd.DataFrame(r.json()["records"]).drop(columns="attributes")
                st.dataframe(df)
            else:
                st.error(f"Erro na consulta: {r.text}")

# ================== SAIR ==================
elif menu == "Sair":
    st.session_state.logged_in = False
    st.experimental_rerun()

import os
import subprocess
import time
import requests
import streamlit as st # type: ignore

def load_uploaded_files(uploaded_files):
    file_contents = []
    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name
        try:
            file_contents.append(f"FILE: {file_name}\n")
            file_contents.append("---------------------------------------------------\n")
            content = uploaded_file.getvalue().decode("utf-8")
            file_contents.append(content)
            file_contents.append("---------------------------------------------------\n")
        except (UnicodeDecodeError, Exception) as e:
            file_contents.append(f"Errore nella lettura del file {file_name}: {e}\n")
            file_contents.append("---------------------------------------------------\n")
    return "".join(file_contents)

def query_ollama(prompt):
    try:
        url = "http://localhost:11434/api/generate"
        response = requests.post(
            url,
            json={
                "model": "codellama",
                "prompt": prompt,
                "stream": False
                }
            )
        response.raise_for_status()
        return response.json()["response"]
    except requests.RequestException as e:
        return f"Errore durante la connessione a Ollama: {e}"

@st.cache_resource
def start_ollama_server():
    try:
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.PIPE, stderr=subprocess.PIPE) # Avvia il server Ollama in background
        time.sleep(5) # Aspetta qualche secondo per dare il tempo al server di avviarsi
        print("Server Ollama avviato.")
    except Exception as e:
        print(f"Errore durante l'avvio del server Ollama: {e}")

# Avvia il server Ollama automaticamente
start_ollama_server()

st.title("Codellama")
st.write(
    """
    Benvenuto! Questo strumento ti permette di interagire con un Codellama in esecuzione locale.
    Puoi caricare file di testo per fornire contesto aggiuntivo al modello.
    """
)

default_prompt = "Basandoti sul codice della seguente infrastruttura Terraform riportami, senza riprendere la domanda, dei componenti di deception coerenti."
prompt = st.text_area("Inserisci il tuo prompt:", placeholder="Prompt...", value=default_prompt)

uploaded_files = st.file_uploader("Carica files:", accept_multiple_files=True)

if st.button("Invia al Chatbot"):
    with st.spinner("Elaborazione in corso..."):
        full_prompt = prompt
        if uploaded_files:
            files_contents = load_uploaded_files(uploaded_files)
            full_prompt += f"\n\nContenuto dei file caricati:\n{files_contents} \n\n"

        chatbot_response = query_ollama(full_prompt)

    st.subheader("Risposta del Chatbot:")
    st.write(chatbot_response)

st.markdown(
    """
    **Note:**
    - Assicurati che il server di Ollama sia attivo e accessibile su `http://localhost:11434`.
    """
)

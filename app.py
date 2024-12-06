import os
import subprocess
import time
import requests
import streamlit as st # type: ignore
from openai import OpenAI # type: ignore

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
        except (Exception) as e:
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
        return response.json()["response"]
    except requests.RequestException as e:
        return f"Errore durante la connessione a Ollama: {e}"

@st.cache_resource
def start_ollama_server():
    try:
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.PIPE, stderr=subprocess.PIPE) # Avvia il server Ollama in background
        print("Server Ollama avviato.")
    except Exception as e:
        print(f"Errore durante l'avvio del server Ollama: {e}")
start_ollama_server()

def query_chatgpt(api_key, prompt, system_prompt, max_tokens=512):
    client = OpenAI(
        api_key = api_key
        )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        max_tokens=max_tokens
    )
    return response['choices'][0]['message']['content'].strip()

st.title("Codellama")
st.write(
    """
    Benvenuto! Questo strumento ti permette di interagire con Codellama in esecuzione locale o mediante query con ChatGPT.
    Puoi caricare file di testo per fornire contesto aggiuntivo al modello.
    """
)

use_chatgpt = st.checkbox("Use ChatGPT instead of local model. **SECURITY AND DATA PRIVACY WARNING**", value=False)
if(use_chatgpt):
    api_key = st.text_input("OpenAI API Key", type="password", 
    value="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")

system_prompt = "Sei un assistente virtuale, specializzata in Terraform. Puoi aiutare a scrivere codice Terraform per implementare componenti di deception."
default_prompt = """
Aggiungi alla configurazione di Terraform già esistente componenti di deception.
Non includere per intero il codice dei file, ma solo le nuove risorse da aggiungere per implementare questi componenti.
Assicurati che il codice segua la struttura di Terraform e che i nuovi componenti siano configurati correttamente con la rete personalizzata esistente.
Il codice deve essere scritto in modo completo, chiaro e ben strutturato.
"""
prompt = st.text_area("Inserisci il tuo prompt:", placeholder="Prompt...", value=default_prompt, height=200)

uploaded_files = st.file_uploader("Carica files:", accept_multiple_files=True)

if st.button("Genera risposta!"):
    with st.spinner("Elaborazione in corso..."):
        full_prompt = prompt
        if uploaded_files:
            files_contents = load_uploaded_files(uploaded_files)
            full_prompt += f"\n\nContenuto dei file caricati:\n{files_contents}\n\n"
        if use_chatgpt and api_key:
            response = query_chatgpt(api_key, full_prompt, system_prompt)
        else:
            response = query_ollama(full_prompt)

    st.subheader("Risposta:")
    st.write(response)

st.markdown(
    """
    **Note:**
    - Assicurati che il server di Ollama sia attivo e accessibile su `http://localhost:11434`.
    """
)

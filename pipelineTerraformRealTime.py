import os
import subprocess
import time
import requests
import streamlit as st  # type: ignore
from openai import OpenAI  # type: ignore
import random
import asyncio

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Funzione per leggere i file caricati dall'utente
def read_files_from_directory(directory_path):
    file_contents = []
    try:
        for file_name in os.listdir(directory_path):
            file_path = os.path.join(directory_path, file_name)
            if os.path.isfile(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        file_contents.append(f"FILE: {file_name}\n")
                        file_contents.append("---------------------------------------------------\n")
                        file_contents.append(file.read())
                        file_contents.append("\n---------------------------------------------------\n")
                except Exception as e:
                    file_contents.append(f"Errore nella lettura del file {file_name}: {e}\n")
                    file_contents.append("---------------------------------------------------\n")
    except Exception as e:
        return f"Errore durante l'accesso alla directory: {e}"
    return "".join(file_contents)

# Funzione per inviare un prompt al modello Codellama
def query_ollama(prompt):
    try:
        url = "http://localhost:11434/api/generate"
        response = requests.post(
            url,
            json={
                "model": "codellama",
                "prompt": prompt,
                "stream": False,
            },
        )
        return response.json()["response"]
    except requests.RequestException as e:
        return f"Errore durante la connessione a Ollama: {e}"

# Funzione per avviare il server Ollama
@st.cache_resource
def start_ollama_server():
    try:
        subprocess.Popen(
            ["ollama", "serve"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )  # Avvia il server Ollama in background
        print("Server Ollama avviato.")
    except Exception as e:
        print(f"Errore durante l'avvio del server Ollama: {e}")

start_ollama_server()

# Funzione per salvare i nuovi componenti in un file
def save_to_file(content, file_path):
    with open(file_path, "w") as f:
        f.write(content)

# Funzione per aggiornare il file configurazione Terraform
def update_terraform_file(source_file, destination_file):
    if not os.path.exists(source_file):
        print(f"Errore: il file sorgente {source_file} non esiste.")
        return
    if not os.path.exists(destination_file):
        print(f"Errore: il file destinazione {destination_file} non esiste.")
        return
    try:
        os.replace(source_file, destination_file)
        print(f"File Terraform aggiornato: {destination_file}")
    except Exception as e:
        print(f"Errore durante l'aggiornamento del file Terraform: {e}")

# Funzione per eseguire la pipeline Terraform
def execute_terraform_deploy(terraform_dir):
    if not os.path.exists(terraform_dir):
        print(f"Errore: la directory Terraform {terraform_dir} non esiste.")
        return
    try:
        print("Inizializzazione di Terraform...")
        subprocess.run(["terraform", "init"], cwd=terraform_dir, check=True)

        print("Validazione della configurazione...")
        subprocess.run(["terraform", "validate"], cwd=terraform_dir, check=True)

        print("Pianificazione delle modifiche...")
        subprocess.run(["terraform", "plan"], cwd=terraform_dir, check=True)

        print("Approvazione delle modifiche...")
        subprocess.run(["terraform", "apply", "-auto-approve"], cwd=terraform_dir, check=True)

        print("Deploy completato con successo!")
    except Exception as e:
        print(f"Errore: {e}")


# Interfaccia utente Streamlit
st.title("Codellama")
st.write(
    """Benvenuto! Questo strumento ti permette di interagire con Codellama in esecuzione locale."""
)

default_prompt = """Aggiungi alla configurazione di Terraform già esistente componenti di deception.
Includi per intero il codice del file main.tf con le nuove aggiunte.
Assicurati che il codice segua la struttura di Terraform e che i nuovi componenti siano configurati correttamente con la rete personalizzata esistente.
Il codice deve essere scritto in modo completo, chiaro e ben strutturato."""
user_prompt = st.text_area(
    "Inserisci il tuo prompt:", placeholder="Prompt...", value=default_prompt, height=200
)

if st.button("Update prompt"):
    prompt = user_prompt
    st.success("Prompt aggiornato con successo!")

async def periodic_deploy(prompt=default_prompt):
    while True:
        with st.spinner("Generazione del codice Terraform in corso..."):
            terraform_directory = os.path.join(BASE_DIR, "terraform_architecture")  # Directory contenente i file Terraform
            
            files_contents = read_files_from_directory(terraform_directory)
            prompt += f"\n\nContenuto dei file caricati:\n{files_contents}\n\n"
            print("Prompt: ", prompt)

            # Invia il prompt al modello Codellama
            response = query_ollama(prompt)
            print("Response: ", response)

        # Salva nuovo file Terraform generato
        new_main_file = os.path.join(BASE_DIR, "new_main.tf")  # File terraform generato
        save_to_file(response, new_main_file)

        # Update file Terraform
        original_file = os.path.join(BASE_DIR, "terraform_architecture/main.tf")  # File Terraform originale
        update_terraform_file(new_main_file, original_file)

        with st.spinner("Deploy in corso..."):
            # Esegue deploy Terraform
            execute_terraform_deploy(terraform_directory)

        interval = random.randint(300, 900)  # Range casuale tra 5 e 15 minuti
        print(f"Deploy completato. Attendo {interval} secondi prima del prossimo aggiornamento.")
        await asyncio.sleep(interval)  # Pausa asincrona

# Esegui la funzione asincrona
if __name__ == "__main__":
    asyncio.run(periodic_deploy())

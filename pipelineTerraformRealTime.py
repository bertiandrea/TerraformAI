import os
import subprocess
import time
import requests
import streamlit as st  # type: ignore
import random
import asyncio
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Funzione per leggere i file caricati dall'utente
def read_files_from_directory(directory_path):
    file_contents = []
    try:
        for file_name in os.listdir(directory_path):
            file_path = os.path.join(directory_path, file_name)
            if os.path.isfile(file_path):
                if not use_only_tf_file or file_path.endswith(".tf"):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as file:
                            file_contents.append(f"FILE: {file_name}\n")
                            file_contents.append("---------------------------------------------------\n")
                            file_contents.append(file.read())
                            file_contents.append("\n---------------------------------------------------\n")
                    except Exception as e:
                        file_contents.append(f"Errore nella lettura del file {file_name}: {e}\n")
                        file_contents.append("---------------------------------------------------\n")
        return "".join(file_contents)
    except Exception as e:
        print(f"Errore durante l'accesso alla directory: {e}")
        raise e

def read_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Errore nella lettura del file {file_path}: {e}")
        raise e

# Funzione per inviare un prompt al modello Codellama
def query_ollama(model, prompt):
    try:
        url = "http://localhost:11434/api/generate"
        response = requests.post(
            url,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
            },
        )
        return response.json()["response"]
    except requests.RequestException as e:
        print(f"Errore durante la connessione a Ollama: {e}")
        raise e

    
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
        raise e

# Funzione per eseguire la pipeline Terraform
def execute_terraform_deploy(terraform_dir):
    if not os.path.exists(terraform_dir):
        print(f"Errore: la directory Terraform {terraform_dir} non esiste.")
        return
    try:
        print("Inizializzazione di Terraform...")
        subprocess.run([os.path.join(terraform_dir, "terraform"), "init"], cwd=terraform_dir, check=True)

        print("Validazione della configurazione...")
        subprocess.run([os.path.join(terraform_dir, "terraform"), "validate"], cwd=terraform_dir, check=True)

        print("Pianificazione delle modifiche...")
        subprocess.run([os.path.join(terraform_dir, "terraform"), "plan"], cwd=terraform_dir, check=True)

        print("Approvazione delle modifiche...")
        subprocess.run([os.path.join(terraform_dir, "terraform"), "apply", "-auto-approve"], cwd=terraform_dir, check=True)
        
        print("Deploy completato con successo!")
    except Exception as e:
        print(f"Errore: {e}")
        raise e

def parse_string(string):
    string = re.search('```(.*?)```', string, re.DOTALL).group(1).strip()
    return string

# Interfaccia utente Streamlit
st.title("TerraformLLaMa - Pipeline Terraform")
st.write(
    """Benvenuto! Questo strumento ti permette di interagire con llama in esecuzione locale."""
)

default_prompt = """Modifica il file 'main.tf' aggiungendo nuovi honeypot o modificando quelli esistenti. La risposta deve contenere esclusivamente il nuovo codice modificato del file 'main.tf'."""
user_prompt = st.text_area(
    "Inserisci il tuo prompt:", placeholder="Prompt...", value=default_prompt, height=200
)

use_only_tf_file = st.checkbox("Analyze only .tf file (Speeds up computation).", value=True)
model_choice = st.selectbox("Modello LLaMa:", ["llama3.2", "codellama"])

if st.button("Update prompt"):
    prompt = user_prompt
    st.success("Prompt aggiornato con successo!")

async def periodic_deploy(prompt=default_prompt):
    while True:
        try:
            with st.spinner("Generazione del codice Terraform in corso..."):
                terraform_directory = os.path.join(BASE_DIR, "terraform_architecture")  # Directory contenente i file Terraform
                
                # Costruisci prompt completo
                files_contents = read_files_from_directory(terraform_directory)
                full_prompt = f"{files_contents}\n\n"
                full_prompt += prompt
                print("\nPROMPT:\n", full_prompt)

                # Invia il prompt al modello Codellama
                response = query_ollama(model_choice, full_prompt)
                print("\nRESPONSE:\n", response)

                # Parsing della risposta
                response_parsed = parse_string(response)
                print("\nRESPONSE PARSED:\n", response_parsed)

            # Salva nuovo file Terraform generato
            new_main_file = os.path.join(BASE_DIR, "new_main.tf")  # File terraform generato
            save_to_file(response_parsed, new_main_file)

            # Update file Terraform
            original_file = os.path.join(BASE_DIR, "terraform_architecture/main.tf")  # File Terraform originale
            update_terraform_file(new_main_file, original_file)

            with st.spinner("Deploy in corso..."):
                # Esegue deploy Terraform
                execute_terraform_deploy(terraform_directory)

            st.success("Deploy completato con successo! Timestamp: " + str(time.time()))
        except Exception as e:
            st.error(f"Errore durante l'esecuzione della pipeline: {e}")
                   
        interval = random.randint(300, 900)  # Range casuale tra 5 e 15 minuti
        print(f"Deploy completato. Attendo {interval} secondi prima del prossimo aggiornamento.")
        await asyncio.sleep(interval)  # Pausa asincrona

# Esegui la funzione asincrona
if __name__ == "__main__":
    asyncio.run(periodic_deploy())

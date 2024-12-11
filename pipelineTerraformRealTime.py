import os
import subprocess
import time
import requests
import streamlit as st  # type: ignore
import random
import asyncio
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Funzione per leggere i file caricati dall'utente
def read_files_from_directory(directory_path):
    if not os.path.exists(directory_path):
        print(f"Errore: la directory {directory_path} non esiste.")
        return
    file_contents = ""
    try:
        for file_name in os.listdir(directory_path):
            file_path = os.path.join(directory_path, file_name)
            if os.path.isfile(file_path):
                if not use_only_tf_file or file_path.endswith(".tf"):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as file:
                            file_contents += str("FILE: " + file_name + " = {\n")
                            for line in file.read().splitlines():
                                file_contents += str("  " + line + "\n")
                            file_contents += str("\n}\n")
                    except Exception as e:
                        file_contents += str(f"Errore nella lettura del file {file_name}: {e}\n")
                        file_contents += str("\n}\n")
        return file_contents
    except Exception as e:
        print(f"Errore durante l'accesso alla directory: {e}")
        raise e

def read_file(file_path):
    if not os.path.exists(file_path):
        print(f"Errore: il file {file_path} non esiste.")
        return
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
    try:
        with open(file_path, "w") as f:
            f.write(content)
    except Exception as e:
        print(f"Errore durante il salvataggio del file: {e}")
        raise e

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

def backup_terraform_file(source_file, destination_file):
    if not os.path.exists(source_file):
        print(f"Errore: il file sorgente {source_file} non esiste.")
        return
    try:
        shutil.copy(source_file, destination_file)
        print(f"File Terraform di backup creato: {destination_file}")
    except Exception as e:
        print(f"Errore durante la creazione del file di backup Terraform: {e}")
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
        print(f"Errore durante il deploy della configurazione Terraform: {e}")
        raise e

def parse_string(string):
    try:
        string = re.search('```(.*?)```', string, re.DOTALL).group(1).strip()
        return string
    except Exception as e:
        print(f"Errore durante il parsing della stringa: {e}")
        raise e

# Interfaccia utente Streamlit
st.title("TerraformLLaMa - Pipeline Terraform")
st.write("""Benvenuto! Questo strumento ti permette di interagire con llama in esecuzione locale.""")

default_prompt = """Il codice del file 'main.tf' deve essere riportato in modo completo e preciso, aggiungendo nuovi honeypot o modificando quelli esistenti in modo coerente con l'infrastruttura Terraform. La risposta deve contenere solo il nuovo codice modificato del file 'main.tf'."""
user_prompt = st.text_area(
    "Inserisci il tuo prompt:", placeholder="Prompt...", value=default_prompt, height=200
)

use_only_tf_file = st.checkbox("Analyze only .tf file (Speeds up computation).", value=True)
model_choice = st.selectbox("Modello LLaMa:", ["codellama", "llama3.2"])

if st.button("Update prompt"):
    prompt = user_prompt
    st.success("Prompt aggiornato con successo!")

async def periodic_deploy(prompt=default_prompt):
    while True:
        try:
            init = time.time()
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
            new_main_file = os.path.join(BASE_DIR, "new_main.tf")
            save_to_file(response_parsed, new_main_file)

            # Salva vecchia configurazione Terraform in caso deploy fallisca
            old_main_file = os.path.join(BASE_DIR, "old_main.tf")
            backup_terraform_file(os.path.join(terraform_directory, "main.tf"), old_main_file)
            
            # Update file Terraform
            update_terraform_file(new_main_file, os.path.join(terraform_directory, "main.tf"))
        except Exception as e:
            st.error(f"Errore durante la generazione del codice terraform: {e}")
            return

        try:
            with st.spinner("Deploy in corso..."):
                execute_terraform_deploy(terraform_directory)
            st.success("Deploy completato con successo! Tempo impiegato: {:.2f} secondi.".format(time.time() - init))
        except Exception as e:
            update_terraform_file(old_main_file, os.path.join(terraform_directory, "main.tf"))
            st.error("Errore durante il deploy. Ripristino della configurazione originale.")
            
        interval = random.randint(300, 900)  # Range casuale tra 5 e 15 minuti
        print(f"Attendo {interval} secondi prima del prossimo aggiornamento.")
        await asyncio.sleep(interval)  # Pausa asincrona

# Esegui la funzione asincrona
if __name__ == "__main__":
    asyncio.run(periodic_deploy())

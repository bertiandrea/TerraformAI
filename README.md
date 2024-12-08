
# Terraform deception elements with LLM

## Descrizione Generale
Questo progetto ha come obiettivo l'implementazione di una pipeline automatizzata per la gestione e il deployment di configurazioni Terraform, integrando la generazione di elementi di deception tramite il modello Codellama.

## Struttura Principale
### Funzionalità
1. **Lettura dei File**
   - `read_files_from_directory(directory_path)`: Legge e restituisce il contenuto dei file in una directory specificata.
   - `read_file(file_path)`: Legge il contenuto di un singolo file.

2. **Interazione con Codellama**
   - `query_ollama(prompt)`: Invia un prompt al modello Codellama e restituisce la risposta.

3. **Avvio del Server Codellama**
   - `start_ollama_server()`: Avvia il server Codellama in background.

4. **Gestione dei File Terraform**
   - `save_to_file(content, file_path)`: Salva il contenuto in un file specificato.
   - `update_terraform_file(source_file, destination_file)`: Aggiorna un file Terraform sostituendo il contenuto esistente.

5. **Pipeline Terraform**
   - `execute_terraform_deploy(terraform_dir)`: Esegue una serie di comandi Terraform (`init`, `validate`, `plan`, `apply`) per implementare le configurazioni.

6. **Periodicità Asincrona**
   - `periodic_deploy(prompt)`: Esegue ciclicamente la pipeline Terraform con un intervallo casuale tra 5 e 15 minuti.

### Interfaccia Utente
L'interfaccia utente sviluppata con Streamlit permette di:
- Inserire e aggiornare un prompt da inviare a Codellama.
- Visualizzare lo stato delle operazioni di deploy.

### Flusso di Esecuzione
1. Lettura dei file Terraform nella directory specificata.
2. Generazione del nuovo file Terraform con gli elementi di deception usando il modello Codellama.
3. Aggiornamento del file principale di configurazione Terraform.
4. Esecuzione del processo di deployment.
5. Ripetizione periodica del processo con un intervallo casuale.

### Utilizzo
Esegui lo script con Python:
```bash
streamlit run pipelineTerraformRealTime.py
```
Assicurati di avere:
- Il server Codellama configurato correttamente.
- La directory contenente i file Terraform esistente.

## Conclusione
Questa soluzione proposta offre una modalità di gestione automatizzata delle infrastrutture Terraform, combinando generazione automatica di configurazioni e un'interfaccia utente intuitiva.


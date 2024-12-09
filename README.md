# Terraform Deception Elements with LLM

## Descrizione Generale

Questo progetto ha l'obiettivo di creare una pipeline automatizzata per la gestione e il deployment di configurazioni Terraform, integrando elementi di deception generati tramite **Codellama**. La soluzione include funzionalità avanzate per la lettura dei file, interazione con il modello Codellama e gestione automatizzata del ciclo di vita Terraform, con un'interfaccia utente semplice e intuitiva sviluppata in **Streamlit**.

---

## Struttura Principale

### Funzionalità

#### Gestione dei File
- **`read_files_from_directory(directory_path)`**: Legge e restituisce il contenuto dei file in una directory specificata. Supporta un'opzione per analizzare solo file con estensione `.tf`.
- **`read_file(file_path)`**: Legge il contenuto di un singolo file.

#### Interazione con Codellama
- **`query_ollama(prompt)`**: Invia un prompt al modello Codellama e restituisce la risposta.
- **`start_ollama_server()`**: Avvia il server Codellama in background.

#### Gestione dei File Terraform
- **`save_to_file(content, file_path)`**: Salva il contenuto generato in un file specificato.
- **`update_terraform_file(source_file, destination_file)`**: Sostituisce il contenuto di un file Terraform con uno aggiornato.

#### Pipeline Terraform
- **`execute_terraform_deploy(terraform_dir)`**: Esegue una sequenza di comandi Terraform (`init`, `validate`, `plan`, `apply`) per implementare le configurazioni.

#### Esecuzione Periodica
- **`periodic_deploy(prompt)`**: Implementa una pipeline Terraform asincrona, con esecuzioni periodiche ogni 5-15 minuti.

---

## Interfaccia Utente

L'interfaccia utente basata su **Streamlit** include:
- Campo di testo per inserire o aggiornare un prompt da inviare a Codellama.
- Checkbox per analizzare solo file `.tf`, migliorando l'efficienza.
- Dropdown per scegliere il modello Codellama da utilizzare.
- Stato in tempo reale delle operazioni di generazione e deployment.

---

## Flusso di Esecuzione

1. **Lettura dei File Terraform**: Recupera i contenuti dei file dalla directory configurata.
2. **Generazione degli Elementi di Deception**: Invia il contenuto dei file e un prompt specifico al modello Codellama per generare nuove configurazioni Terraform.
3. **Aggiornamento del File**: Salva il file generato e aggiorna il file principale `main.tf`.
4. **Esecuzione del Deployment**: Applica le modifiche usando Terraform.
5. **Periodicità**: Ripete il processo con un intervallo casuale tra 5 e 15 minuti.

---

## Istruzioni per l'Esecuzione

Esegui il progetto con il comando:

```bash
streamlit run pipelineTerraformRealTime.py
```

### Requisiti
- Server Codellama configurato e in esecuzione.
- Una directory contenente i file Terraform (`terraform_architecture`).
- Installazione di Terraform.

---

## Conclusione

Questa soluzione offre una gestione automatizzata delle infrastrutture Terraform, combinando tecnologie avanzate di machine learning e un'interfaccia utente user-friendly. Il sistema può essere facilmente integrato in flussi di lavoro DevOps esistenti per migliorare l'efficienza e la sicurezza.
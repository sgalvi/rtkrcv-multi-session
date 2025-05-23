# 🛰️ RTKRCV Pool Manager

Un'applicazione web per gestire più sessioni RTKRCV per un pool di dispositivi GNSS, con interfaccia semplice per configurare Master e Rover e monitorare le sessioni di correzione differenziale RTK.

## 📋 Caratteristiche

- **Gestione Dispositivi**: Aggiunta, modifica ed eliminazione di dispositivi GNSS
- **Configurazione Master/Rover**: Supporto per ruoli Master e Rover
- **Gestione Sessioni**: Avvio e stop delle sessioni RTKRCV per ogni Rover
- **Monitoraggio Real-time**: Visualizzazione dell'output NMEA in tempo reale
- **Interfaccia Web**: UI responsive e intuitiva
- **Auto-refresh**: Aggiornamento automatico dello stato delle sessioni

## 🏗️ Architettura

### Backend (Python + Flask)
- **app.py**: Server principale Flask con API REST
- **sessions.py**: Gestione delle sessioni RTKRCV con subprocess
- **pool_list.json**: File di configurazione dei dispositivi

### Frontend (HTML + JavaScript)
- **templates/index.html**: Interfaccia web responsive
- **static/script.js**: Logica frontend per interazione con API

### Struttura Directory
```
rtkrcv-manager/
├── app.py              # Server Flask principale
├── sessions.py         # Gestione sessioni RTKRCV
├── pool_list.json      # Configurazione dispositivi (generato automaticamente)
├── requirements.txt    # Dipendenze Python
├── templates/
│   └── index.html      # Interfaccia web
├── static/
│   └── script.js       # Logica frontend
├── config/             # File configurazione RTKRCV (generati automaticamente)
├── output/             # File output NMEA (generati automaticamente)
└── README.md          # Questo file
```

## 🚀 Installazione e Avvio

### 1. Prerequisiti
- Python 3.7 o superiore
- pip (gestore pacchetti Python)
- Rtkrcv

### 2. Installazione Dipendenze

#### 2.1 RTKRCV
Clona i repository di rtkrcv
Puoi trovare l'ultima versione di rtkrcv a questo indirizzo:
https://github.com/rtklibexplorer/RTKLIB.git
Una volta clonato sulla propria macchina, spostarsi nella directory /app/consapp/rtkrcv/gcc/ e compiliamo il nostro programma
```bash
git clone https://github.com/rtklibexplorer/RTKLIB.git
cd /app/consapp/rtkrcv/gcc
make
```
a questo punto ci troveremo il binario compilato di rtkrcv. consiglio di spostarlo nella root del progetto oppure in /usr/local/bin/ assicurandoci di renderlo eseguibile
```bash 
chmod +x rtkrcv
```
#### 2.2 Dipendenze python 
Crea un virtual enviroment:
> ```bash
>python3 -m venv venv
>```
>Attiva virtual enviroment:
>```bash
>source venv/bin/activate
>```

Installa le dipendenze:
```bash
pip install -r requirements.txt
```

### 3. Avvio dell'Applicazione

```bash
python app.py
```

Il server si avvierà su `http://localhost:5000`

### 4. Accesso all'Interfaccia Web

Apri il browser e vai su:
```
http://localhost:5000
```

## 📖 Come Usare l'Applicazione

### 1. Aggiungere Dispositivi

1. Nella sezione "Aggiungi/Modifica Dispositivo":
   - **Nome**: Nome descrittivo del dispositivo
   - **Seriale**: Numero seriale univoco del dispositivo
   - **IP**: Indirizzo IP del dispositivo GNSS
   - **Porta**: Porta di comunicazione (es. 2222)
   - **Ruolo**: Seleziona "Master" o "Rover"

2. Clicca "Aggiungi Dispositivo"

### 2. Gestire le Sessioni

- **Per avviare una sessione RTK**:
  1. Assicurati di avere almeno un Master configurato
  2. Clicca il pulsante "▶️ Start" accanto al Rover desiderato
  3. La sessione RTKRCV si avvierà automaticamente

- **Per fermare una sessione**:
  1. Clicca il pulsante "⏹️ Stop" accanto al Rover attivo

### 3. Monitorare l'Output

1. Nella sezione "Output Sessioni NMEA":
   - Seleziona un rover dal menu a tendina
   - L'output NMEA verrà mostrato in tempo reale
   - L'aggiornamento è automatico ogni 2 secondi per sessioni attive

### 4. Modificare/Eliminare Dispositivi

- **Modifica**: Clicca "✏️ Modifica" per caricare i dati nel form
- **Elimina**: Clicca "🗑️ Elimina" (conferma richiesta)

## ⚙️ Componenti Tecnici

### API Endpoints

- `GET /` - Interfaccia web principale
- `GET /api/devices` - Lista dispositivi con stato sessioni
- `POST /api/devices` - Aggiunge nuovo dispositivo
- `PUT /api/devices/<serial>` - Aggiorna dispositivo esistente
- `DELETE /api/devices/<serial>` - Elimina dispositivo
- `POST /api/sessions/<serial>/start` - Avvia sessione RTKRCV
- `POST /api/sessions/<serial>/stop` - Ferma sessione RTKRCV
- `GET /api/sessions/<serial>/status` - Stato della sessione
- `GET /api/sessions/<serial>/output` - Output NMEA della sessione

### Gestione Processi

- Ogni sessione RTKRCV viene eseguita come processo separato usando `subprocess`
- I processi vengono tracciati e possono essere fermati correttamente
- La configurazione RTKRCV viene generata automaticamente per ogni rover
- L'output NMEA viene salvato in file separati per ogni sessione

### File Generati

- **config/<seriale>.conf**: File di configurazione RTKRCV per ogni rover
- **output/<seriale>.nmea**: File di output NMEA per ogni sessione
- **pool_list.json**: Configurazione persistente dei dispositivi

## 🔧 Personalizzazione

### Simulazione vs RTKRCV Reale

Attualmente l'applicazione simula l'esecuzione di RTKRCV per test. Per usare RTKRCV reale:

1. Modifica il file `sessions.py`
2. Nella funzione `start_session`, sostituisci la variabile `cmd` con:
```python
cmd = ['rtkrcv', '-c', config_path]
```

### Configurazione RTKRCV

I parametri di configurazione RTKRCV possono essere personalizzati modificando la funzione `create_rtkrcv_config` in `sessions.py`.

### Coordinate Master

La funzione `extract_master_coordinates` attualmente usa coordinate simulate. Per implementazioni reali, connettiti al dispositivo Master e estrai le coordinate dai messaggi NMEA.

## 🐛 Troubleshooting

### Problemi Comuni

1. **Server non si avvia**:
   - Verifica che Flask sia installato: `pip install Flask`
   - Controlla che la porta 5000 sia libera

2. **Sessioni non si avviano**:
   - Verifica la configurazione IP/porta dei dispositivi
   - Controlla i log del server per errori

3. **Output NMEA non visibile**:
   - Assicurati che la sessione sia attiva (stato "running")
   - Verifica che il file output nella cartella `output/` sia presente

### Debug

Per abilitare maggiori informazioni di debug, modifica `app.py`:
```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

## 📄 Licenza

Questo progetto è rilasciato come esempio educativo. Personalizza secondo le tue esigenze.

## 🤝 Contributi

Per miglioramenti o segnalazioni di bug, considera di:
1. Documentare il problema o la feature richiesta
2. Testare le modifiche prima dell'implementazione
3. Mantenere la semplicità dell'interfaccia

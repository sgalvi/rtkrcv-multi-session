from flask import Flask, render_template, request, jsonify
import json
import os
from sessions import SessionManager

app = Flask(__name__)
session_manager = SessionManager()

# File di configurazione del pool dispositivi
POOL_CONFIG_FILE = 'pool_list.json'

def load_pool_config():
    """Carica la configurazione del pool dai file JSON"""
    if os.path.exists(POOL_CONFIG_FILE):
        try:
            with open(POOL_CONFIG_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"devices": []}
    return {"devices": []}

def save_pool_config(config):
    """Salva la configurazione del pool nel file JSON"""
    with open(POOL_CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

@app.route('/')
def index():
    """Pagina principale dell'applicazione"""
    return render_template('index.html')

@app.route('/api/devices', methods=['GET'])
def get_devices():
    """Restituisce l'elenco dei dispositivi configurati"""
    config = load_pool_config()
    # Aggiungi lo stato delle sessioni a ogni dispositivo
    for device in config['devices']:
        if device['role'] == 'Rover':
            device['session_status'] = session_manager.get_session_status(device['serial'])
    return jsonify(config)

@app.route('/api/devices', methods=['POST'])
def add_device():
    """Aggiunge un nuovo dispositivo alla configurazione"""
    data = request.json
    
    # Validazione base dei dati
    required_fields = ['name', 'serial', 'ip', 'port', 'role']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Campi obbligatori mancanti"}), 400
    
    if data['role'] not in ['Master', 'Rover']:
        return jsonify({"error": "Ruolo deve essere Master o Rover"}), 400
    
    config = load_pool_config()
    
    # Controlla se il seriale esiste già
    for device in config['devices']:
        if device['serial'] == data['serial']:
            return jsonify({"error": "Dispositivo con questo seriale già esistente"}), 400
    
    # Aggiungi il nuovo dispositivo
    new_device = {
        "name": data['name'],
        "serial": data['serial'],
        "ip": data['ip'],
        "port": int(data['port']),
        "role": data['role']
    }
    
    config['devices'].append(new_device)
    save_pool_config(config)
    
    return jsonify({"message": "Dispositivo aggiunto con successo"})

@app.route('/api/devices/<serial>', methods=['DELETE'])
def delete_device(serial):
    """Rimuove un dispositivo dalla configurazione"""
    config = load_pool_config()
    
    # Ferma la sessione se è attiva
    if session_manager.is_session_running(serial):
        session_manager.stop_session(serial)
    
    # Rimuovi il dispositivo
    config['devices'] = [d for d in config['devices'] if d['serial'] != serial]
    save_pool_config(config)
    
    return jsonify({"message": "Dispositivo rimosso con successo"})

@app.route('/api/devices/<serial>', methods=['PUT'])
def update_device(serial):
    """Aggiorna un dispositivo esistente"""
    data = request.json
    config = load_pool_config()
    
    # Trova il dispositivo
    device = None
    for d in config['devices']:
        if d['serial'] == serial:
            device = d
            break
    
    if not device:
        return jsonify({"error": "Dispositivo non trovato"}), 404
    
    # Ferma la sessione se è attiva e il dispositivo sta cambiando
    if session_manager.is_session_running(serial):
        session_manager.stop_session(serial)
    
    # Aggiorna i campi
    device.update({
        "name": data.get('name', device['name']),
        "ip": data.get('ip', device['ip']),
        "port": int(data.get('port', device['port'])),
        "role": data.get('role', device['role'])
    })
    
    save_pool_config(config)
    return jsonify({"message": "Dispositivo aggiornato con successo"})

@app.route('/api/sessions/<serial>/start', methods=['POST'])
def start_session(serial):
    """Avvia una sessione RTKRCV per un rover"""
    config = load_pool_config()
    
    # Trova il rover
    rover = None
    master = None
    
    for device in config['devices']:
        if device['serial'] == serial and device['role'] == 'Rover':
            rover = device
        elif device['role'] == 'Master':
            master = device
    
    if not rover:
        return jsonify({"error": "Rover non trovato"}), 404
    
    if not master:
        return jsonify({"error": "Master non configurato"}), 400
    
    # Avvia la sessione
    success, message = session_manager.start_session(rover, master)
    
    if success:
        return jsonify({"message": message})
    else:
        return jsonify({"error": message}), 500

@app.route('/api/sessions/<serial>/stop', methods=['POST'])
def stop_session(serial):
    """Ferma una sessione RTKRCV per un rover"""
    success, message = session_manager.stop_session(serial)
    
    if success:
        return jsonify({"message": message})
    else:
        return jsonify({"error": message}), 500

@app.route('/api/sessions/<serial>/status', methods=['GET'])
def get_session_status(serial):
    """Ottieni lo stato di una sessione"""
    status = session_manager.get_session_status(serial)
    return jsonify({"status": status})

@app.route('/api/sessions/<serial>/output', methods=['GET'])
def get_session_output(serial):
    """Ottieni l'output NMEA di una sessione"""
    output = session_manager.get_session_output(serial)
    return jsonify({"output": output})

if __name__ == '__main__':
    # Crea la cartella per i file di output se non esiste
    os.makedirs('output', exist_ok=True)
    os.makedirs('config', exist_ok=True)
    
    app.run(host='0.0.0.0', port=5000, debug=True)

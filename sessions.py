import subprocess
import threading
import time
import os
import re
from datetime import datetime
import pwd
import os.path

class SessionManager:
    def __init__(self, rtkrcv_path='rtkrcv'):
        self.active_sessions = {}  # serial -> session_info
        self.lock = threading.Lock()
        # Converti in percorso assoluto
        self.rtkrcv_path = os.path.abspath(os.path.expanduser(rtkrcv_path))
        
        # Aggiungi debug info
        print(f"Current working directory: {os.getcwd()}")
        print(f"Absolute rtkrcv path: {self.rtkrcv_path}")
        print(f"Path exists: {os.path.exists(self.rtkrcv_path)}")
        print(f"Is file: {os.path.isfile(self.rtkrcv_path)}")
        print(f"Has execute permission: {os.access(self.rtkrcv_path, os.X_OK)}")
        print(f"Effective user: {pwd.getpwuid(os.geteuid()).pw_name}")
    
    def create_rtkrcv_config(self, rover, master):
        """Crea il file di configurazione per RTKRCV"""
        config_content = f"""# RTKRCV Configuration for {rover['name']}
# Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

console-passwd = admin
console-timetype = gpst

# Input streams
inpstr1-type = tcpcli
inpstr1-path = {rover['ip']}:{rover['port']}
inpstr1-format = rtcm3

inpstr2-type = tcpcli  
inpstr2-path = {master['ip']}:{master['port']}
inpstr2-format = rtcm3

# Output stream
outstr1-type = file
outstr1-path = output/{rover['serial']}.nmea
outstr1-format = nmea

# Processing options
pos1-posmode = kinematic
pos1-frequency = l1+l2
pos1-soltype = forward
pos1-elmask = 15
pos1-snrmask_r = off
pos1-snrmask_b = off
pos1-snrmask_L1 = 0,0,0,0,0,0,0,0,0
pos1-snrmask_L2 = 0,0,0,0,0,0,0,0,0
pos1-snrmask_L5 = 0,0,0,0,0,0,0,0,0
pos1-dynamics = on
pos1-tidecorr = off
pos1-ionoopt = brdc
pos1-tropopt = saas
pos1-sateph = brdc
pos1-posopt1 = off
pos1-posopt2 = off
pos1-posopt3 = off
pos1-posopt4 = off
pos1-posopt5 = off
pos1-exclsats = 
pos1-navsys = 1

pos2-armode = continuous
pos2-gloarmode = on
pos2-arthres = 3
pos2-arlockcnt = 0
pos2-arelmask = 0
pos2-arminfix = 10
pos2-armaxiter = 1
pos2-elmaskhold = 0
pos2-aroutcnt = 5
pos2-slipthres = 0.05
pos2-maxage = 30
pos2-rejionno = 0.0
pos2-niter = 1
pos2-baselen = 0
pos2-basesig = 0

out-solformat = nmea
out-outhead = on
out-outopt = on
out-timesys = gpst
out-timeform = tow
out-timendec = 3
out-degform = deg
out-fieldsep = 
out-height = ellipsoidal
out-geoid = internal
out-solstatic = all
out-nmeaintv1 = 0
out-nmeaintv2 = 0
out-outstat = off

stats-eratio1 = 100
stats-eratio2 = 100
stats-errphase = 0.003
stats-errphaseel = 0.003
stats-errphasebl = 0
stats-errdoppler = 1
stats-stdbias = 30
stats-stdiono = 0.03
stats-stdtrop = 0.3
stats-prnaccelh = 1
stats-prnaccelv = 1
stats-prnbias = 0.0001
stats-prniono = 0.001
stats-prntrop = 0.0001
stats-prnpos = 0
stats-clkstab = 5e-12

ant1-postype = llh
ant1-pos1 = 0
ant1-pos2 = 0  
ant1-pos3 = 0
ant1-anttype = 
ant1-antdele = 0
ant1-antdeln = 0
ant1-antdelu = 0

ant2-postype = llh
ant2-pos1 = 0
ant2-pos2 = 0
ant2-pos3 = 0
ant2-anttype =
ant2-antdele = 0
ant2-antdeln = 0
ant2-antdelu = 0

misc-timeinterp = off
misc-sbasatsel = 0
misc-rnxopt1 = 
misc-rnxopt2 = 
file-cmdfile1 = 
file-cmdfile2 = 
file-cmdfile3 = 
"""
        
        config_path = f"config/{rover['serial']}.conf"
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        return config_path
    
    def extract_master_coordinates(self, master):
        """Estrae le coordinate del master da NMEA (simulato)"""
        # In un'implementazione reale, qui si connetterebbe al master
        # e si estrarrebebbero le coordinate reali da NMEA
        # Per ora simuliamo delle coordinate fisse
        return {
            'lat': 45.0641,  # Esempio: Torino
            'lon': 7.6697,
            'alt': 239.0
        }
    
    def start_session(self, rover, master):
        """Avvia una sessione RTKRCV per un rover"""
        with self.lock:
            serial = rover['serial']

            # Controlla se la sessione è già attiva
            if serial in self.active_sessions:
                if self.active_sessions[serial]['process'].poll() is None:
                    return False, "Sessione già attiva per questo rover"

            try:
                # Crea le directory se non esistono
                os.makedirs("config", exist_ok=True)
                os.makedirs("output", exist_ok=True)
                
                # Assicurati che il working directory sia quello corretto
                script_dir = os.path.dirname(os.path.abspath(__file__))
                os.chdir(script_dir)

                # Crea il file di configurazione
                config_path = self.create_rtkrcv_config(rover, master)

                # Estrai coordinate del master (simulato)
                master_coords = self.extract_master_coordinates(master)

                # Debugging: Print the value of self.rtkrcv_path
                print(f"Debug: self.rtkrcv_path = {self.rtkrcv_path}")

                # Debugging: Check if the file exists and is executable using os.path
                try:
                    if not os.path.isfile(self.rtkrcv_path):
                        raise FileNotFoundError(f"File not found: {self.rtkrcv_path}")
                    if not os.access(self.rtkrcv_path, os.X_OK):
                        raise PermissionError(f"File not executable: {self.rtkrcv_path}")
                except Exception as e:
                    print(f"Error accessing rtkrcv: {str(e)}")
                    print(f"Current working directory: {os.getcwd()}")
                    return False, f"Error accessing rtkrcv: {str(e)}"

                cmd = [self.rtkrcv_path, '-c', config_path]

                # Avvia il processo
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                # Salva le informazioni della sessione
                self.active_sessions[serial] = {
                    'process': process,
                    'rover': rover,
                    'master': master,
                    'config_path': config_path,
                    'start_time': datetime.now(),
                    'output_file': f"output/{serial}.nmea"
                }

                return True, f"Sessione RTKRCV avviata per {rover['name']}"

            except Exception as e:
                return False, f"Errore nell'avvio della sessione: {str(e)}"
    
    def stop_session(self, serial):
        """Ferma una sessione RTKRCV"""
        with self.lock:
            if serial not in self.active_sessions:
                return False, "Nessuna sessione attiva per questo rover"
            
            try:
                session = self.active_sessions[serial]
                process = session['process']
                
                # Termina il processo
                if process.poll() is None:
                    process.terminate()
                    
                    # Aspetta che il processo termini
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
                
                # Aggiungi una nota di fine nel file di output
                try:
                    with open(session['output_file'], 'a') as f:
                        f.write(f"# Session ended at {datetime.now()}\n")
                except:
                    pass
                
                # Rimuovi la sessione dalla lista
                del self.active_sessions[serial]
                
                return True, f"Sessione fermata per rover {serial}"
                
            except Exception as e:
                return False, f"Errore nel fermare la sessione: {str(e)}"
    
    def is_session_running(self, serial):
        """Controlla se una sessione è in esecuzione"""
        with self.lock:
            if serial not in self.active_sessions:
                return False
            
            process = self.active_sessions[serial]['process']
            return process.poll() is None
    
    def get_session_status(self, serial):
        """Ottieni lo stato di una sessione"""
        with self.lock:
            if serial not in self.active_sessions:
                return "stopped"
            
            process = self.active_sessions[serial]['process']
            if process.poll() is None:
                return "running"
            else:
                # Processo terminato, rimuovi dalla lista
                del self.active_sessions[serial]
                return "stopped"
    
    def get_session_output(self, serial, lines=20):
        """Ottieni le ultime righe dell'output NMEA"""
        output_file = f"output/{serial}.nmea"
        
        if not os.path.exists(output_file):
            return []
        
        try:
            with open(output_file, 'r') as f:
                all_lines = f.readlines()
                return [line.strip() for line in all_lines[-lines:]]
        except Exception as e:
            return [f"Errore nella lettura del file: {str(e)}"]
    
    def get_all_sessions_status(self):
        """Ottieni lo stato di tutte le sessioni attive"""
        with self.lock:
            status = {}
            for serial, session in self.active_sessions.items():
                status[serial] = {
                    'rover_name': session['rover']['name'],
                    'status': 'running' if session['process'].poll() is None else 'stopped',
                    'start_time': session['start_time'].isoformat(),
                    'output_file': session['output_file']
                }
            return status
    
    def cleanup_stopped_sessions(self):
        """Pulisce le sessioni terminate dalla lista"""
        with self.lock:
            stopped_sessions = []
            for serial, session in self.active_sessions.items():
                if session['process'].poll() is not None:
                    stopped_sessions.append(serial)
            
            for serial in stopped_sessions:
                del self.active_sessions[serial]

manager = SessionManager(rtkrcv_path='./rtkrcv')


# Ottieni il percorso assoluto dello script corrente
script_dir = os.path.dirname(os.path.abspath(__file__))
rtkrcv_path = os.path.join(script_dir, 'rtklib', 'rtkrcv')

# Inizializza il manager con il percorso assoluto
manager = SessionManager(rtkrcv_path=rtkrcv_path)

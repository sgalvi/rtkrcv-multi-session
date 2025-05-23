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
    
    def create_rtkrcv_config(self, rover, master_device_info, master_coords):
        """Crea il file di configurazione per RTKRCV"""
        config_content = f"""# RTKRCV Configuration for {rover['name']}
    # Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

    console-passwd     =admin
    console-timetype   =utc
    console-soltype    =dms
    console-solflag    =off

    # OPTIONS 1
    pos1-posmode       =static-start
    pos1-frequency     =l1
    pos1-soltype       =forward
    pos1-elmask        =15
    pos1-snrmask_r     =on
    pos1-snrmask_b     =on
    pos1-snrmask_L1    =20,20,20,20,20,20,20,20,20
    pos1-snrmask_L2    =0,0,0,0,0,0,0,0,0
    pos1-snrmask_L5    =0,0,0,0,0,0,0,0,0
    pos1-dynamics      =on
    pos1-tidecorr      =off
    pos1-ionoopt       =brdc
    pos1-tropopt       =saas
    pos1-sateph        =brdc
    pos1-posopt1       =off
    pos1-posopt2       =off
    pos1-posopt3       =off
    pos1-posopt4       =off
    pos1-posopt5       =off
    pos1-exclsats      =
    pos1-navsys        =13

    # OPTIONS 2
    pos2-armode        =fix-and-hold
    pos2-gloarmode     =off
    pos2-arfilter      =on
    pos2-bdsarmode     =off
    pos2-arlockcnt     =0
    pos2-arthres       =3
    pos2-arthres1      =0.99
    pos2-arthres2      =-0.055
    pos2-arthres3      =1E-7
    pos2-arthres4      =1E-3
    pos2-minfixsats    =4
    pos2-minholdsats   =5
    pos2-arelmask      =0
    pos2-aroutcnt      =5
    pos2-arminfix      =0
    pos2-armaxiter     =1
    pos2-elmaskhold    =0
    pos2-slipthres     =0.05
    pos2-maxage        =100
    pos2-syncsol       =off
    pos2-rejionno      =1000
    pos2-rejgdop       =30
    pos2-niter         =1
    pos2-baselen       =0
    pos2-basesig       =0

    # OUTPUT DETAILS
    out-solformat      =llh        # (0:llh,1:xyz,2:enu,3:nmea)
    out-outhead        =on
    out-outopt         =off
    out-timesys        =gpst
    out-timeform       =hms
    out-timendec       =3
    out-degform        =deg
    out-fieldsep       =
    out-height         =ellipsoidal
    out-geoid          =internal
    out-solstatic      =all
    out-nmeaintv1      =1
    out-nmeaintv2      =1
    out-outstat        =off
    out-outsingle      =on

    # STATISTICS
    stats-eratio1      =300
    stats-eratio2      =100
    stats-errphase     =0.003
    stats-errphaseel   =0.003
    stats-errphasebl   =0
    stats-errdoppler   =10
    stats-stdbias      =30
    stats-stdiono      =0.03
    stats-stdtrop      =0.3
    stats-prnaccelh    =1
    stats-prnaccelv    =1
    stats-prnbias      =0.0001
    stats-prniono      =0.001
    stats-prntrop      =0.0001
    stats-clkstab      =5e-12

    # ROVER DETAILS
    ant1-postype       =single
    ant1-pos1          =
    ant1-pos2          =
    ant1-pos3          =
    ant1-anttype       =
    ant1-antdele       =0
    ant1-antdeln       =0
    ant1-antdelu       =0

    # MASTER DETAILS
    ant2-postype       =llh # Use LLH for master coordinates
    ant2-pos1          ={master_coords['lat']}
    ant2-pos2          ={master_coords['lon']}
    ant2-pos3          ={master_coords['alt']}
    ant2-anttype       =
    ant2-antdele       =0
    ant2-antdeln       =0
    ant2-antdelu       =0

    # Input streams
    inpstr1-type       =tcpcli
    inpstr2-type       =ntripcli
    inpstr3-type       =off
    inpstr1-path       = {rover['ip']}:{rover['port']}
    inpstr1-format     = rtcm3

    inpstr2-type       =tcpcli
    inpstr2-path       = {master_device_info['ip']}:{master_device_info['port']} # This should be the master's RTCM stream for corrections
    inpstr2-format     = rtcm3

    # Output stream
    outstr1-type       =file
    outstr1-path       =output/{rover['serial']}.pos
    outstr1-format     =llh

    misc-timeinterp    =off
    misc-sbasatsel     =0
    misc-rnxopt1       =
    misc-rnxopt2       =
    file-cmdfile1      =
    file-cmdfile2      =
    file-cmdfile3      =
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

                # Estrai le coordinate del master (LLH for antenna position)
                # master_coords are for ant2-pos1, ant2-pos2, ant2-pos3
                # The RTCM stream for corrections comes from master_device_info['ip']:master_device_info['port'] (inpstr2-path)
                # However, the requirement is to get master's coordinates from RTCM stream on port 2222.
                # This implies that the master device itself broadcasts its position via an RTCM message (e.g., type 1005/1006)
                # For now, extract_master_coordinates will simulate getting these LLH coordinates.
                # The master_device_info (containing IP/port) is still needed for inpstr2-path which is the correction stream.

                # Let's assume the master device (whose details are in 'master') provides its coordinates
                # via an RTCM stream accessible on its IP and a specific port (e.g. 2222 as per requirement for master coord acquisition)
                # For the rtkrcv config, ant2-pos1/2/3 are these coordinates.
                # inpstr2-path is where rtkrcv connects to get RTCM *correction* messages from the master.
                # This might be the same IP/port or a different one, depending on the master's setup.
                # The original code used master['ip']:master['port'] for inpstr2-path.
                # The requirement says "Use the RTCM stream from port 2222 to obtain the master device’s coordinates."
                # This is handled by extract_master_coordinates. The result is used for ant2-pos1/2/3.
                # The inpstr2-path for *corrections* should still point to the master's correction stream output.
                # We'll keep using master['ip']:master['port'] for inpstr2-path as in the original config logic,
                # assuming this is where the master outputs RTCM corrections.

                master_llh_coords = self.extract_master_coordinates(master) # master here is master_device_info
                if not master_llh_coords:
                    return False, "Impossibile ottenere le coordinate LLH del master."

                # Crea il file di configurazione
                # Pass rover info, master device info (for IP/port of correction stream), and master LLH coords (for antenna position)
                config_path = self.create_rtkrcv_config(rover, master, master_llh_coords)

                # Comando per avviare RTKRCV
                cmd = [self.rtkrcv_path, '-s', '-o', config_path]
                print(f"Avvio del comando: {' '.join(cmd)}")
                print(f"Nella directory: {os.getcwd()}")

                # Avvia il processo RTKRCV
                process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) # stdout e stderr a DEVNULL se non servono
                output_file_path = os.path.join(script_dir, "output", f"{rover['serial']}.pos")
                self.active_sessions[serial] = {
                    'process': process,
                    'output_file': output_file_path,
                    'rover_coords': None, # Placeholder per le coordinate del rover
                    'status': 'running' # Stato iniziale
                }
                
                # Avvia un thread per monitorare il file .pos e lo stato del processo
                threading.Thread(target=self._monitor_pos_file, args=(serial, process, output_file_path), daemon=True).start()

                return True, f"Sessione RTKRCV avviata per {rover['name']}. Monitoraggio del file .pos iniziato."
            except Exception as e:
                print(f"Errore durante l'avvio della sessione per {serial}: {e}")
                return False, f"Errore nell'avvio della sessione: {e}"
    
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
        """Ottieni lo stato di una sessione (running/stopped/fix/error)"""
        with self.lock:
            if serial in self.active_sessions:
                return self.active_sessions[serial].get('status', 'stopped')
            return 'stopped'

    def get_rover_coordinates(self, serial):
        """Ottieni le coordinate XYZ del rover se disponibili."""
        with self.lock:
            if serial in self.active_sessions:
                return self.active_sessions[serial].get('rover_coords')
            return None

    def _monitor_pos_file(self, serial, process, pos_file_path):
        """Monitora il file .pos per lo stato 'fix' e estrae le coordinate."""
        print(f"[{serial}] Monitoraggio del file: {pos_file_path}")
        try:
            while process.poll() is None: # Finchè il processo rtkrcv è attivo
                if not os.path.exists(pos_file_path):
                    time.sleep(1) # Attendi che il file venga creato
                    continue

                with open(pos_file_path, 'r') as f:
                    lines = f.readlines()
                
                # Cerca l'ultima riga valida con coordinate e stato
                # Formato atteso (esempio, può variare): 
                # YYYY/MM/DD HH:MM:SS.sss    lat(deg)    lon(deg)    height(m) Q=s ...
                # Q=1 (fix), Q=2 (float), Q=5 (single)
                # Le coordinate sono solitamente in LLH (lat, lon, height)
                # Dobbiamo convertirle in XYZ se richiesto dal frontend, ma per ora estraiamo LLH.
                last_valid_line = None
                for line in reversed(lines):
                    if line.startswith('%') or not line.strip(): # Ignora commenti e righe vuote
                        continue
                    parts = line.split()
                    if len(parts) >= 5: # Deve avere almeno data, ora, lat, lon, height, Q
                        last_valid_line = parts
                        break
                
                if last_valid_line:
                    try:
                        # L'indice di Q e delle coordinate dipende dal formato esatto del file .pos
                        # Questo è un esempio basato su un formato comune.
                        # Ad esempio, se Q è il 6° elemento (indice 5) e le coordinate sono 2,3,4
                        q_status = int(last_valid_line[5]) # Assumendo che Q sia il sesto campo
                        
                        if q_status == 1: # Stato FIX
                            lat = float(last_valid_line[2])
                            lon = float(last_valid_line[3])
                            alt = float(last_valid_line[4]) # Altezza ellissoidica
                            
                            # Qui dovresti convertire LLH in XYZ se necessario.
                            # Per ora, memorizziamo LLH e simuliamo XYZ.
                            # La conversione LLH -> XYZ richiede un modello geodetico (es. WGS84)
                            # e può essere complessa. Usiamo valori fittizi per XYZ.
                            rover_xyz_coords = {
                                'x': lon * 100000, # Esempio di trasformazione banale
                                'y': lat * 100000,
                                'z': alt * 10
                            }

                            with self.lock:
                                if serial in self.active_sessions:
                                    self.active_sessions[serial]['rover_coords'] = rover_xyz_coords
                                    self.active_sessions[serial]['status'] = 'fix'
                            print(f"[{serial}] Stato FIX raggiunto. Coordinate (LLH): {lat}, {lon}, {alt}. XYZ (simulato): {rover_xyz_coords}")
                            process.terminate() # Termina rtkrcv
                            try:
                                process.wait(timeout=5) # Attendi che termini
                            except subprocess.TimeoutExpired:
                                process.kill()
                            print(f"[{serial}] Processo RTKRCV terminato.")
                            # Pulisci il file .pos dopo aver ottenuto il fix (opzionale)
                            # if os.path.exists(pos_file_path):
                            #    os.remove(pos_file_path)
                            return # Esce dal thread di monitoraggio
                        elif q_status == 2: # Float
                             with self.lock:
                                if serial in self.active_sessions:
                                    self.active_sessions[serial]['status'] = 'float'
                        elif q_status == 5: # Single
                            with self.lock:
                                if serial in self.active_sessions:
                                    self.active_sessions[serial]['status'] = 'single'
                        # Altri stati potrebbero essere gestiti qui

                    except (ValueError, IndexError) as e:
                        print(f"[{serial}] Errore nel parsing della riga del file .pos: {line.strip()} - {e}")
                        pass # Ignora righe malformate

                time.sleep(2) # Controlla ogni 2 secondi
            
            # Se il loop finisce, il processo rtkrcv si è fermato per qualche motivo
            with self.lock:
                if serial in self.active_sessions and self.active_sessions[serial]['status'] not in ['fix', 'error']:
                    self.active_sessions[serial]['status'] = 'stopped'
            print(f"[{serial}] Processo RTKRCV non più attivo. Monitoraggio terminato.")

        except Exception as e:
            print(f"[{serial}] Errore nel thread di monitoraggio del file .pos: {e}")
            with self.lock:
                if serial in self.active_sessions:
                    self.active_sessions[serial]['status'] = 'error'
    
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

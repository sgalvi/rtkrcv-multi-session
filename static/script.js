// Variabili globali
let devices = [];
let isEditing = false;
let outputUpdateInterval = null;

// Inizializzazione dell'applicazione
document.addEventListener('DOMContentLoaded', function() {
    loadDevices();
    
    // Setup form submit
    document.getElementById('deviceForm').addEventListener('submit', handleFormSubmit);
    
    // Auto-refresh ogni 5 secondi per gli stati delle sessioni
    setInterval(loadDevices, 5000);
});

// Gestione del submit del form
function handleFormSubmit(e) {
    e.preventDefault();
    
    const formData = {
        name: document.getElementById('deviceName').value,
        serial: document.getElementById('deviceSerial').value,
        ip: document.getElementById('deviceIp').value,
        port: document.getElementById('devicePort').value,
        role: document.getElementById('deviceRole').value
    };
    
    if (isEditing) {
        updateDevice(document.getElementById('editSerial').value, formData);
    } else {
        addDevice(formData);
    }
}

// Mostra alert
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alertContainer');
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    alertContainer.appendChild(alertDiv);
    
    // Rimuovi l'alert dopo 5 secondi
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}

// Carica l'elenco dei dispositivi
async function loadDevices() {
    try {
        const response = await fetch('/api/devices');
        const data = await response.json();
        
        if (response.ok) {
            devices = data.devices || [];
            updateDevicesTable();
            updateOutputDeviceSelect();
        } else {
            showAlert('Errore nel caricamento dei dispositivi: ' + (data.error || 'Errore sconosciuto'), 'error');
        }
    } catch (error) {
        showAlert('Errore di connessione: ' + error.message, 'error');
    }
}

// Aggiorna la tabella dei dispositivi
function updateDevicesTable() {
    const tbody = document.getElementById('devicesTableBody');
    
    if (devices.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" style="text-align: center; padding: 40px; color: #7f8c8d;">
                    Nessun dispositivo configurato
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = devices.map(device => {
        const roleClass = device.role === 'Master' ? 'role-master' : 'role-rover';
        let statusBadge = '';
        let sessionActions = '';
        
        if (device.role === 'Rover') {
            const status = device.session_status || 'stopped';
            const statusClass = status === 'running' ? 'status-running' : 'status-stopped';
            statusBadge = `<span class="status-badge ${statusClass}">${status}</span>`;
            
            if (status === 'running') {
                sessionActions = `
                    <button class="btn-danger btn-small" onclick="stopSession('${device.serial}')" title="Ferma sessione">
                        ⏹️ Stop
                    </button>
                `;
            } else {
                sessionActions = `
                    <button class="btn-success btn-small" onclick="startSession('${device.serial}')" title="Avvia sessione">
                        ▶️ Start
                    </button>
                `;
            }
        } else {
            statusBadge = '<span style="color: #7f8c8d;">N/A</span>';
        }
        
        return `
            <tr>
                <td>${escapeHtml(device.name)}</td>
                <td><code>${escapeHtml(device.serial)}</code></td>
                <td>${escapeHtml(device.ip)}:${device.port}</td>
                <td><span class="${roleClass}">${device.role}</span></td>
                <td>${statusBadge}</td>
                <td>${escapeHtml(device.coordinates?.x ?? 'N/A')}</td>
                <td>${escapeHtml(device.coordinates?.y ?? 'N/A')}</td>
                <td>${escapeHtml(device.coordinates?.z ?? 'N/A')}</td>
                <td>
                    ${sessionActions}
                    <button class="btn-warning btn-small" onclick="editDevice('${device.serial}')" title="Modifica dispositivo">
                        ✏️ Modifica
                    </button>
                    <button class="btn-danger btn-small" onclick="deleteDevice('${device.serial}')" title="Elimina dispositivo">
                        🗑️ Elimina
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

// Aggiorna la select per l'output delle sessioni
function updateOutputDeviceSelect() {
    const select = document.getElementById('outputDeviceSelect');
    const currentValue = select.value;
    
    const rovers = devices.filter(d => d.role === 'Rover');
    
    select.innerHTML = '<option value="">Seleziona un rover per vedere l\'output</option>';
    
    rovers.forEach(rover => {
        const option = document.createElement('option');
        option.value = rover.serial;
        option.textContent = `${rover.name} (${rover.serial})`;
        
        if (rover.session_status === 'running') {
            option.textContent += ' - 🟢 Attivo';
        } else {
            option.textContent += ' - 🔴 Fermo';
        }
        
        select.appendChild(option);
    });
    
    // Ripristina la selezione precedente se possibile
    if (currentValue && rovers.find(r => r.serial === currentValue)) {
        select.value = currentValue;
    }
}

// Aggiungi un nuovo dispositivo
async function addDevice(deviceData) {
    try {
        const response = await fetch('/api/devices', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(deviceData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert(data.message, 'success');
            resetForm();
            loadDevices();
        } else {
            showAlert(data.error || 'Errore nell\'aggiunta del dispositivo', 'error');
        }
    } catch (error) {
        showAlert('Errore di connessione: ' + error.message, 'error');
    }
}

// Modifica un dispositivo esistente
async function updateDevice(serial, deviceData) {
    try {
        const response = await fetch(`/api/devices/${serial}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(deviceData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert(data.message, 'success');
            resetForm();
            loadDevices();
        } else {
            showAlert(data.error || 'Errore nell\'aggiornamento del dispositivo', 'error');
        }
    } catch (error) {
        showAlert('Errore di connessione: ' + error.message, 'error');
    }
}

// Elimina un dispositivo
async function deleteDevice(serial) {
    if (!confirm('Sei sicuro di voler eliminare questo dispositivo?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/devices/${serial}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert(data.message, 'success');
            loadDevices();
        } else {
            showAlert(data.error || 'Errore nell\'eliminazione del dispositivo', 'error');
        }
    } catch (error) {
        showAlert('Errore di connessione: ' + error.message, 'error');
    }
}

// Modifica un dispositivo (carica i dati nel form)
function editDevice(serial) {
    const device = devices.find(d => d.serial === serial);
    if (!device) return;
    
    document.getElementById('deviceName').value = device.name;
    document.getElementById('deviceSerial').value = device.serial;
    document.getElementById('deviceSerial').disabled = true; // Non permettere la modifica del seriale
    document.getElementById('deviceIp').value = device.ip;
    document.getElementById('devicePort').value = device.port;
    document.getElementById('deviceRole').value = device.role;
    document.getElementById('editSerial').value = serial;
    
    document.getElementById('submitBtn').textContent = 'Aggiorna Dispositivo';
    document.getElementById('cancelBtn').classList.remove('hidden');
    
    isEditing = true;
    
    // Scroll al form
    document.getElementById('deviceForm').scrollIntoView({ behavior: 'smooth' });
}

// Annulla la modifica
function cancelEdit() {
    resetForm();
}

// Reset del form
function resetForm() {
    document.getElementById('deviceForm').reset();
    document.getElementById('deviceSerial').disabled = false;
    document.getElementById('editSerial').value = '';
    document.getElementById('submitBtn').textContent = 'Aggiungi Dispositivo';
    document.getElementById('cancelBtn').classList.add('hidden');
    isEditing = false;
}

// Avvia una sessione RTKRCV
async function startSession(serial) {
    const button = event.target;
    const originalText = button.innerHTML;
    button.innerHTML = '<div class="loading"></div>';
    button.disabled = true;
    
    try {
        const response = await fetch(`/api/sessions/${serial}/start`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert(data.message, 'success');
            loadDevices();
        } else {
            showAlert(data.error || 'Errore nell\'avvio della sessione', 'error');
        }
    } catch (error) {
        showAlert('Errore di connessione: ' + error.message, 'error');
    } finally {
        button.innerHTML = originalText;
        button.disabled = false;
    }
}

// Ferma una sessione RTKRCV
async function stopSession(serial) {
    if (!confirm('Sei sicuro di voler fermare questa sessione?')) {
        return;
    }
    
    const button = event.target;
    const originalText = button.innerHTML;
    button.innerHTML = '<div class="loading"></div>';
    button.disabled = true;
    
    try {
        const response = await fetch(`/api/sessions/${serial}/stop`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert(data.message, 'success');
            loadDevices();
        } else {
            showAlert(data.error || 'Errore nel fermare la sessione', 'error');
        }
    } catch (error) {
        showAlert('Errore di connessione: ' + error.message, 'error');
    } finally {
        button.innerHTML = originalText;
        button.disabled = false;
    }
}

// Carica l'output di una sessione
async function loadSessionOutput() {
    const select = document.getElementById('outputDeviceSelect');
    const serial = select.value;
    const console = document.getElementById('outputConsole');
    
    if (!serial) {
        console.innerHTML = `
            <div style="text-align: center; color: #7f8c8d;">
                Seleziona un rover per visualizzare l'output NMEA
            </div>
        `;
        
        // Ferma l'auto-refresh se attivo
        if (outputUpdateInterval) {
            clearInterval(outputUpdateInterval);
            outputUpdateInterval = null;
        }
        return;
    }
    
    try {
        const response = await fetch(`/api/sessions/${serial}/output`);
        const data = await response.json();
        
        if (response.ok) {
            const output = data.output || [];
            
            if (output.length === 0) {
                console.innerHTML = `
                    <div style="text-align: center; color: #7f8c8d;">
                        Nessun output disponibile per questo rover
                    </div>
                `;
            } else {
                console.innerHTML = output.map(line => 
                    `<div class="output-line">${escapeHtml(line)}</div>`
                ).join('');
                
                // Scroll automaticamente in basso
                console.scrollTop = console.scrollHeight;
            }
            
            // Avvia l'auto-refresh se la sessione è attiva
            const device = devices.find(d => d.serial === serial);
            if (device && device.session_status === 'running') {
                if (!outputUpdateInterval) {
                    outputUpdateInterval = setInterval(loadSessionOutput, 2000);
                }
            } else {
                if (outputUpdateInterval) {
                    clearInterval(outputUpdateInterval);
                    outputUpdateInterval = null;
                }
            }
            
        } else {
            console.innerHTML = `
                <div style="color: #e74c3c;">
                    Errore nel caricamento dell'output: ${data.error || 'Errore sconosciuto'}
                </div>
            `;
        }
    } catch (error) {
        console.innerHTML = `
            <div style="color: #e74c3c;">
                Errore di connessione: ${error.message}
            </div>
        `;
    }
}

// Utility function per escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Cleanup quando la pagina viene chiusa
window.addEventListener('beforeunload', function() {
    if (outputUpdateInterval) {
        clearInterval(outputUpdateInterval);
    }
});

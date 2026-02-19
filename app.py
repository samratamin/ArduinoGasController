import os
import time
import json
import serial
import serial.tools.list_ports
import pandas as pd
import logging
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
GAS_MAPPING_FILE = 'GasMapping.csv'
SETTINGS_FILE = 'AppSettings.json'
BAUD_RATE = 115200 # Matches GasController_Serial_v1.ino
SERIAL_TIMEOUT = 0.5 

# Default Settings (Overridden by AppSettings.json)
app_settings = {
    "max_purge_time": 60,
    "show_pin_number": False,
    "check_interval": 30
}

# Global state
ser = None
gas_mappings = []
connected_port = None
last_mapping_mtime = 0
last_check_time = 0
mapping_was_reloaded = False
mapping_error = None

def load_settings():
    """Load application settings from JSON file"""
    global app_settings
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                new_settings = json.load(f)
                app_settings.update(new_settings)
                logging.info(f"Loaded settings from {SETTINGS_FILE}: {app_settings}")
        except Exception as e:
            logging.error(f"Error loading {SETTINGS_FILE}: {e}")

def create_template_mapping():
    """Create a template GasMapping.csv file"""
    template_data = [
        {"Gas": "Air", "Pin": 4},
        {"Gas": "Nitrogen", "Pin": 5},
        {"Gas": "Carbon Dioxide", "Pin": 6},
        {"Gas": "Helium", "Pin": 7},
        {"Gas": "R-134A", "Pin": 8},
        {"Gas": "Vacuum", "Pin": 9}
    ]
    try:
        df = pd.DataFrame(template_data)
        df.to_csv(GAS_MAPPING_FILE, index=False)
        logging.info(f"Created template mapping file: {GAS_MAPPING_FILE}")
        return template_data
    except Exception as e:
        logging.error(f"Failed to create template mapping: {e}")
        return template_data

def load_gas_mappings():
    """Load gas mapping from CSV file, creating template if missing"""
    global gas_mappings, last_mapping_mtime, mapping_was_reloaded, mapping_error
    
    if not os.path.exists(GAS_MAPPING_FILE):
        logging.warning(f"{GAS_MAPPING_FILE} not found. Creating template...")
        gas_mappings = create_template_mapping()
        last_mapping_mtime = os.path.getmtime(GAS_MAPPING_FILE)
        mapping_was_reloaded = True
        mapping_error = None
        return

    try:
        new_mtime = os.path.getmtime(GAS_MAPPING_FILE)
        df = pd.read_csv(GAS_MAPPING_FILE)
        
        # Check basic column existence
        if df.empty:
             raise ValueError("CSV is empty")
        if 'Gas' not in df.columns or 'Pin' not in df.columns:
            raise ValueError("Missing columns ('Gas', 'Pin'). Ensure the first line is exactly 'Gas,Pin'")
            
        # Row-by-row validation
        validated_mappings = []
        seen_pins = {}
        for index, row in df.iterrows():
            gas = str(row['Gas']).strip()
            pin = row['Pin']
            
            # Check for empty gas name
            if pd.isna(row['Gas']) or gas == "" or gas.lower() == "nan":
                 raise ValueError(f"Line {index+2}: Gas name cannot be empty")
            
            # Check for valid Pin (ensure it's not NaN or non-numeric)
            if pd.isna(pin):
                 raise ValueError(f"Line {index+2}: Missing Pin for gas '{gas}'. Did you forget a comma?")
            
            try:
                pin_int = int(pin)
            except (ValueError, TypeError):
                raise ValueError(f"Line {index+2}: Pin for '{gas}' must be a whole number (found '{pin}')")
                
            # Check for duplicate pins
            if pin_int in seen_pins:
                raise ValueError(f"Line {index+2}: Duplicate Pin detected! Pin {pin_int} is already assigned to '{seen_pins[pin_int]}'")
                
            seen_pins[pin_int] = gas
            validated_mappings.append({"Gas": gas, "Pin": pin_int})
            
        gas_mappings = validated_mappings
        last_mapping_mtime = new_mtime
        mapping_was_reloaded = True
        mapping_error = None # Clear previous error if successful
        logging.info(f"Loaded {len(gas_mappings)} gas mappings from {GAS_MAPPING_FILE}")
    except Exception as e:
        mapping_error = str(e)
        logging.error(f"Error loading gas mappings: {mapping_error}")
        # Mark as reloaded so the error is reported to the UI
        mapping_was_reloaded = True

def check_for_changes(force=False):
    """Periodic check for File changes"""
    global last_check_time, last_mapping_mtime
    
    now = time.time()
    if force or (now - last_check_time > app_settings.get('check_interval', 30)):
        last_check_time = now
        if os.path.exists(GAS_MAPPING_FILE):
            current_mtime = os.path.getmtime(GAS_MAPPING_FILE)
            if current_mtime > last_mapping_mtime:
                logging.info(f"Change detected in {GAS_MAPPING_FILE}. Reloading...")
                load_gas_mappings()
        else:
             logging.warning(f"{GAS_MAPPING_FILE} missing during periodic check. Regenerating...")
             load_gas_mappings()

def get_serial_ports():
    """List available serial ports"""
    return [port.device for port in serial.tools.list_ports.comports()]

def auto_connect_serial():
    """Scan and connect to the correct Arduino serial port"""
    global ser, connected_port
    
    ports = get_serial_ports()
    logging.info(f"Scanning {len(ports)} ports for Gas Controller...")
    
    for port in ports:
        try:
            # Try to connect with a short timeout
            test_ser = serial.Serial(port, BAUD_RATE, timeout=0.2)
            time.sleep(1.0) # Wait for Arduino reset
            
            # Send 'conn' padded to 24 bytes as expected by ListenToSerial()
            msg = "conn".ljust(24)
            test_ser.write(msg.encode())
            
            # Read response
            response = test_ser.readline().decode().strip()
            test_ser.close()
            
            if "true" in response:
                logging.info(f"Found Gas Controller on {port}")
                ser = serial.Serial(port, BAUD_RATE, timeout=SERIAL_TIMEOUT)
                connected_port = port
                return True
        except Exception as e:
            logging.debug(f"Failed to test port {port}: {e}")
            continue
            
    connected_port = None
    return False

@app.route('/')
def index():
    """Render main page"""
    check_for_changes(force=True)
    return render_template('index.html', 
                           gases=gas_mappings, 
                           mapping_error=mapping_error,
                           settings=app_settings)

@app.route('/regenerate_mapping', methods=['POST'])
def handle_regenerate():
    """Trigger template regeneration"""
    global gas_mappings, last_mapping_mtime, mapping_was_reloaded, mapping_error
    try:
        gas_mappings = create_template_mapping()
        last_mapping_mtime = os.path.getmtime(GAS_MAPPING_FILE)
        mapping_was_reloaded = True
        mapping_error = None
        return jsonify({"status": "success", "message": "Template mapping recreated!"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to recreate: {e}"}), 500

@app.route('/status', methods=['GET'])
def handle_status():
    """Get connection status"""
    global ser, mapping_was_reloaded
    check_for_changes()

    res = {
        "status": "success",
        "connected": bool(ser and ser.is_open),
        "port": connected_port,
        "mapping_reloaded": mapping_was_reloaded,
        "mapping_error": mapping_error,
        "show_pin_number": app_settings.get('show_pin_number')
    }
    
    if mapping_was_reloaded:
        res["gases"] = gas_mappings
        mapping_was_reloaded = False # Reset flag after sending
        
    if not res["connected"]:
        # Try to auto-connect if not connected
        if auto_connect_serial():
            res["connected"] = True
            res["port"] = connected_port
            
    return jsonify(res)

@app.route('/purge', methods=['POST'])
def handle_purge():
    """Send purge command to Arduino"""
    global ser
    check_for_changes()
    if not ser or not ser.is_open:
        # Try one last auto-connect
        if not auto_connect_serial():
            return jsonify({"status": "error", "message": "Gas controller not connected"}), 400
    
    data = request.get_json()
    gas_name = data.get('gas')
    purge_time = int(data.get('time', 10))
    
    # Enforce max purge time from settings
    max_time = app_settings.get('max_purge_time', 60)
    if purge_time > max_time:
        return jsonify({"status": "error", "message": f"Purge time exceeds maximum of {max_time}s"}), 400
    
    # Find pin for gas
    pin = None
    for item in gas_mappings:
        if item['Gas'] == gas_name:
            pin = item['Pin']
            break
    
    if pin is None:
        return jsonify({"status": "error", "message": f"Gas {gas_name} not found"}), 400
    
    # Format according to .ino: GPIO08:005 (for Pin 8 for 5 seconds)
    # Padded to 24 bytes as expected by char message[25] loop
    message = f"GPIO{int(pin):02d}:{int(purge_time):03d}"
    padded_message = message.ljust(24)
    
    try:
        ser.write(padded_message.encode())
        logging.info(f"Sent command: {padded_message}")
        return jsonify({"status": "success", "message": f"Purging {gas_name} for {purge_time}s"})
    except Exception as e:
        logging.error(f"Error sending command: {e}")
        ser = None # Reset serial on error
        return jsonify({"status": "error", "message": "Serial communication failed"}), 500

if __name__ == '__main__':
    load_settings()
    load_gas_mappings()
    mapping_was_reloaded = False # Reset flag so first load doesn't show reload notification
    
    # Get configuration from environment variables if available
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logging.info(f"Starting Gas Controller on {host}:{port} (Debug: {debug})")
    app.run(host=host, port=port, debug=debug)

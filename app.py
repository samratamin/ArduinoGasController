import os
import time
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
BAUD_RATE = 115200 # Matches GasController_Serial_v1.ino
SERIAL_TIMEOUT = 0.5 

# Global state
ser = None
gas_mappings = []
connected_port = None

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
    """Load gas mapping from CSV file, creating template if missing or corrupted"""
    global gas_mappings
    
    if not os.path.exists(GAS_MAPPING_FILE):
        logging.warning(f"{GAS_MAPPING_FILE} not found. Creating template...")
        gas_mappings = create_template_mapping()
        return

    try:
        df = pd.read_csv(GAS_MAPPING_FILE)
        if df.empty or 'Gas' not in df.columns or 'Pin' not in df.columns:
            raise ValueError("CSV is empty or missing required columns")
            
        gas_mappings = df.to_dict('records')
        logging.info(f"Loaded {len(gas_mappings)} gas mappings from {GAS_MAPPING_FILE}")
    except Exception as e:
        logging.error(f"Error loading gas mappings (file may be corrupted): {e}")
        logging.info("Regenerating template mapping...")
        gas_mappings = create_template_mapping()

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
    return render_template('index.html', gases=gas_mappings)

@app.route('/status', methods=['GET'])
def handle_status():
    """Get connection status"""
    global ser
    if ser and ser.is_open:
        return jsonify({"status": "success", "connected": True, "port": connected_port})
    
    # Try to auto-connect if not connected
    if auto_connect_serial():
         return jsonify({"status": "success", "connected": True, "port": connected_port})
         
    return jsonify({"status": "success", "connected": False})

@app.route('/purge', methods=['POST'])
def handle_purge():
    """Send purge command to Arduino"""
    global ser
    if not ser or not ser.is_open:
        # Try one last auto-connect
        if not auto_connect_serial():
            return jsonify({"status": "error", "message": "Gas controller not connected"}), 400
    
    data = request.get_json()
    gas_name = data.get('gas')
    purge_time = data.get('time', 10)
    
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
    load_gas_mappings()
    app.run(host='0.0.0.0', port=5001, debug=True)

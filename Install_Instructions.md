# Getting Started: Arduino Gas Controller

This application is designed to run locally on your machine and communicate with an Arduino over USB (Serial).

### Prerequisites
1. Python 3.x installed (Check with 'python --version' or 'python3 --version').
2. Arduino connected to your computer via USB.
3. Arduino Sketch uploaded: Make sure the sketch in Arduino_GasController_Serial_v1/GasController_Serial_v1/GasController_Serial_v1.ino is uploaded to your Arduino.
4. Gas Configuration: Ensure the gas names and pins in GasMapping.csv match your physical Arduino wiring.

---

## Easy One-Click Setup (Recommended)

### Windows
1. Open the folder containing the project in File Explorer.
2. Double-click run.bat.
3. The script will automatically create a virtual environment, install requirements, and launch the app in your browser at http://localhost:5001.

### macOS / Linux
1. Open your Terminal and navigate to the project folder.
2. Make the script executable:
   chmod +x run.sh
3. Run the script:
   ./run.sh
4. Open your browser to http://localhost:5001.

---

## Manual Installation

If you prefer to set up your environment manually:

1. Create a Virtual Environment:
   python -m venv venv
2. Activate it:
   - Windows: venv\Scriptsctivate
   - macOS/Linux: source venv/bin/activate
3. Install Dependencies:
   pip install -r requirements.txt
4. Launch the App:
   python app.py

---

## Troubleshooting

### Serial Port Access (Linux Only)
If the app cannot connect to your Arduino, you may need to add your user to the dialout group:
sudo usermod -a -G dialout $USER
Note: You must log out and back in for this change to take effect.

---

## Gas Configuration (GasMapping.csv)

The application uses GasMapping.csv to map gas names to their corresponding Arduino digital pins.

* Customize Your Setup: Open GasMapping.csv in any text editor or Excel and update the Gas and Pin columns. Use commas to separate the gas name and the pin number (e.g., Argon,2).
* Immediate Update: To see changes immediately after saving the file, simply refresh the web page in your browser.
* Dynamic Updates: The app checks for changes in the background every 30 seconds. The web interface will notify you with a 'CSV Mapping Reloaded!' status and update the dropdown automatically.
* Strict Validation: The app ensures gas names are not empty, pins are valid numbers, and no two gases share the same GPIO pin. If a rule is violated, an error will appear in the web interface and prevent purge actions until fixed.
* Handling Errors: If the CSV file is corrupted (e.g., missing columns or duplicate pins), an error will appear in the web interface. Use the 'Regenerate Default Template' button in the error box to reset the configuration.
* Resetting to Defaults: To return to factory settings manually, delete GasMapping.csv. The app will regenerate a template on next startup or check.

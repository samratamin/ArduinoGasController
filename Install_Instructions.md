# Getting Started: Arduino Gas Controller

This application is designed to run locally on your machine and communicate with an Arduino over USB (Serial). 

### Prerequisites
1.  **Python 3.x** installed (Check with `python --version` or `python3 --version`).
2.  **Arduino** connected to your computer via USB.
3.  **Arduino Sketch** uploaded: Make sure the sketch in [Arduino_GasController_Serial_v1/GasController_Serial_v1/GasController_Serial_v1.ino](Arduino_GasController_Serial_v1/GasController_Serial_v1/GasController_Serial_v1.ino) is uploaded to your Arduino.
4.  **Gas Configuration**: Ensure the gas names and pins in [GasMapping.csv](GasMapping.csv) match your physical Arduino wiring.

---

## Easy One-Click Setup (Recommended)

### **Windows**
1.  Open the folder containing the project.
2.  Double-click **`run.bat`**.
3.  It will automatically create a virtual environment (`venv`), install all requirements, and launch the app in your browser at `http://localhost:5001`.

### **macOS / Linux**
1.  Open your Terminal and navigate to the project folder.
2.  Ensure the file is executable (only needs to be done once):
    ```bash
    chmod +x run.sh
    ```
3.  Run the script:
    ```bash
    ./run.sh
    ```
4.  Open your browser to `http://localhost:5001`.

---

## 🐋 Docker Setup (Advanced / Linux)

Docker is the best way to run this on Linux consistently. Note: Serial port passthrough via Docker can be unstable on Windows/macOS.

1.  Open your terminal in the project folder.
2.  Run:
    ```bash
    docker-compose up --build -d
    ```
3.  The app will be available at `http://localhost:5001`.

*Note: You may need to edit `docker-compose.yml` to match your Arduino's serial port (e.g., `/dev/ttyUSB0` vs `/dev/ttyACM0`).*

---

## 🛠 Manual Installation (If things go wrong)

If you prefer to set up your environment manually:

1.  **Create a Virtual Environment**:
    ```bash
    python -m venv venv
    ```
2.  **Activate it**:
    -   Windows: `venv\Scripts\activate`
    -   macOS/Linux: `source venv/bin/activate`
3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Launch the App**:
    ```bash
    python app.py
    ```

---

## 🔌 Troubleshooting

### **Serial Port Access (Linux Only)**
If the app can't connect to your Arduino, you might need to add your user to the `dialout` group:
```bash
sudo usermod -a -G dialout $USER
```
*Note: You must log out and back in for this change to take effect.*

---

## � Gas Configuration (`GasMapping.csv`)

The application uses [GasMapping.csv](GasMapping.csv) to map gas names to their corresponding Arduino digital pins.

- **Customize Your Setup**: Open [GasMapping.csv](GasMapping.csv) in any text editor or Excel and update the `Gas` and `Pin` columns to match your physical wiring. Use **commas** to separate the gas name and the pin number (e.g., `Argon,2`).
- **Immediate Update**: If you want to see changes immediately after saving the file, simply **refresh the web page** in your browser.
- **Dynamic Updates**: The application also automatically checks for changes in the background every 30 seconds. The web interface will notify you with a "CSV Mapping Reloaded!" status and update the gas selection dropdown automatically.
- **Strict Validation**: The app performs row-by-row validation. It ensures gas names are not empty, pins are valid numbers, and importantly, **that no two gases share the same GPIO pin**. If any rule is violated, an error will appear in the web interface and prevent any purge actions until fixed.
- **Handling Errors**: If the CSV file is corrupted (e.g., missing columns, empty, or duplicate pins), an error will appear in the web interface. You can use the **"Regenerate Default Template"** button in the error box to reset the configuration.
- **Resetting to Defaults**: If you want to return to factory settings manually, simply **delete `GasMapping.csv`**.
- **Regeneration**: On the next startup or periodic check, the app will detect the missing file and automatically generate a new one with standard template values.

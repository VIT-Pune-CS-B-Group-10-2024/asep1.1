from flask import Flask, render_template, request, jsonify
import numpy as np
import pandas as pd
import os

app = Flask(__name__)

# Path to the directory containing your data files
DATA_DIR = "data"  # Update this path to the folder containing your .txt files

# Material densities (g/cm³)
material_densities = {
    'aluminium': 2.7,
    'titanium': 4.5,
    'steel': 7.8,
    'iron': 7.87  # Example density for iron
}

def load_material_data(metal):
    """Load the data file for the selected metal."""
    file_path = os.path.join(DATA_DIR, f"{metal}.txt")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Data file for {metal} not found: {file_path}")
    
    # Load the data, skipping the header rows
    data = pd.read_csv(file_path, delim_whitespace=True, skiprows=4, header=None)
    data.columns = [
        'Kinetic Energy', 'Total Stp. Pow.', 'CSDA Range', 
        'Radiation Yield', 'Damage Effect Parameter'
    ]
    return data

def simulate_radiation(metal, radiation, temperature, intensity):
    try:
        # Load the data for the selected metal
        material_data = load_material_data(metal)
        
        # Example: Use the first row of data for simulation
        row = material_data.iloc[0]
        stopping_power = row['Total Stp. Pow.']  # MeV cm²/g
        csda_range = row['CSDA Range']  # g/cm²
        damage_effect = row['Damage Effect Parameter']

        # Material density
        density = material_densities[metal]  # g/cm³

        # Thickness of material (example: 1 cm)
        thickness = 1.0  # cm

        # Energy loss calculation
        energy_loss = stopping_power * density * thickness  # MeV

        # Damage factor calculation
        damage_factor = damage_effect * intensity / temperature

        # Radiation absorption calculation
        absorption = 1 - np.exp(-thickness / csda_range)

        # Result text
        result = (
            f"{metal.capitalize()} exposed to {radiation} radiation at {temperature}K and {intensity} W/m²:\n"
            f"Energy Loss: {energy_loss:.2f} MeV\n"
            f"Damage Factor: {damage_factor:.2f}\n"
            f"Radiation Absorption: {absorption:.2f}"
        )

        # Plot data: Energy Loss vs Thickness
        thickness_range = np.linspace(0, 10, 100)  # Thickness range (cm)
        energy_loss_range = stopping_power * density * thickness_range
        plot_data = [{
            'x': thickness_range,
            'y': energy_loss_range,
            'type': 'scatter',
            'name': 'Energy Loss vs Thickness'
        }]

        return result, plot_data

    except Exception as e:
        return f"Error: {str(e)}", []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/simulate', methods=['POST'])
def simulate():
    data = request.json
    result, plot_data = simulate_radiation(data['metal'], data['radiation'], data['temperature'], data['intensity'])
    return jsonify({'result': result, 'plot_data': plot_data})

if __name__ == '__main__':
    app.run(debug=True)
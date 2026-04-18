# QC-SDC-TP-Demo
**Quantum Communication: Superdense Coding & Teleportation**

This repository contains a Qiskit-based implementation and analysis of two fundamental quantum communication protocols: **Superdense Coding (SDC)** and **Quantum Teleportation (TP)**. 

The project demonstrates how to build these circuits and evaluates their performance across three different execution environments:
1. **Ideal Statevector Simulation:** Perfect mathematical execution.
2. **Noisy Hardware Model:** Local simulation with injected depolarizing errors to model NISQ device decoherence.
3. **Real IBM Quantum Hardware:** Physical execution on real superconducting qubits via Qiskit Runtime.

---

## Features

* **Protocol Implementations:** Modular functions to construct circuits for SDC (transmitting 2 classical bits via 1 qubit) and TP (transmitting 1 quantum state via 2 classical bits).
* **Multi-Environment Execution:** Run the same logical circuits locally or on real IBM QPUs.
* **Phase Verification:** Includes inverse rotation logic to accurately verify the teleportation of non-computational basis states ($|+\rangle$, $|-\rangle$, and $|+i\rangle$).
* **Data Serialization:** Execution results are serialized into structured JSON files (`sdc_master_results.json`, `tp_master_results.json`) to decouple heavy quantum compute from visualization.
* **Automated Plotting:** A dedicated visualization script to generate comparative Matplotlib histograms.

---

## Prerequisites

Ensure you have Python 3.8+ installed. You will need the following libraries:

```bash
pip install qiskit qiskit-aer qiskit-ibm-runtime matplotlib numpy
```

### IBM Quantum Access (Optional but Recommended)
To run the circuits on real hardware, you need an IBM Quantum API token.
1. Create an account at [IBM Quantum Platform](https://quantum.ibm.com/).
2. Copy your API token.
3. Create a file named `apikey.json` in the root directory of this project with the following structure:
```json
{
    "apikey": "YOUR_IBM_QUANTUM_API_TOKEN_HERE"
}
```

---

## Usage
You can use `make` if you have makefile installed and a working API from IBM Quantum Platform, or
### 1. Running the Simulations
Use `main.py` to execute the protocols.

**Run Superdense Coding (Local Simulation):**
```bash
python main.py -p sdc
```

**Run Quantum Teleportation (Local Simulation):**
```bash
python main.py -p tp
```

**Run on Real IBM Hardware:**
Append the `-r` (or `--real`) flag to route the payload to the least busy operational IBM QPU. *(Note: This requires the `apikey.json` file and may take time depending on the IBM cloud queue).*
```bash
python main.py -p sdc -r
python main.py -p tp -r
```

### 2. Generating Plots
Once the data is serialized into the JSON files, use the animation/plotting script to generate the comparative histograms.

```bash
python ani.py
```
This will output high-resolution `.png` files for each tested state, dynamically adjusting the layout based on whether real hardware data is present.

---

## Repository Structure

* `main.py`: The core quantum execution script containing circuit definitions and Qiskit Runtime logic.
* `ani.py`: The Matplotlib visualization script that parses JSON data into comparative histograms.
* `apikey.json`: *(User created)* Stores the IBM Quantum API credentials.
* `sdc_master_results.json`: Auto-generated payload containing SDC shot counts.
* `tp_master_results.json`: Auto-generated payload containing Teleportation shot counts.
* `QC_Assignment_Report.tex`: IEEE formatted LaTeX report discussing the methodology and results.
* `*_plot.png`: Auto-generated comparative histograms.

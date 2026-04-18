import json
import argparse
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_aer.primitives import SamplerV2 as AerSampler
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_ibm_runtime import SamplerV2 as RuntimeSampler
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

#Demonstrative person node.
class Person:
    def __init__(self, name, num_qubits, num_cbits=0):
        self.name = name
        self.qreg = QuantumRegister(num_qubits, f"{name}_q")
        self.creg = ClassicalRegister(num_cbits, f"{name}_c") if num_cbits > 0 else None

#Setup the super-dense coding circuit.
def setup_sdc_circuit(alice, bob, message):
    #Qunatum registers to store shared entangled pair, Bob's classical bit to store measurement.
    qc = QuantumCircuit(alice.qreg, bob.qreg, bob.creg)
    
    #Entangling pair..
    qc.h(alice.qreg[0])
    qc.cx(alice.qreg[0], bob.qreg[0])
    qc.barrier()

    #Alice encodes the message..
    if message == '01':
        qc.z(alice.qreg[0]) 
    elif message == '10':
        qc.x(alice.qreg[0]) 
    elif message == '11':
        qc.z(alice.qreg[0])
        qc.x(alice.qreg[0])
    qc.barrier()

    #Bob decodes and measures..
    qc.cx(alice.qreg[0], bob.qreg[0])
    qc.h(alice.qreg[0])
    qc.measure([alice.qreg[0], bob.qreg[0]], [bob.creg[0], bob.creg[1]])
    
    return qc

#Setup the teleportation circuit.
def setup_tp_circuit(alice, bob, state):
    qc = QuantumCircuit(alice.qreg, bob.qreg, alice.creg, bob.creg)
    
    #Preparing the Alice's 0th qubit state..
    if state == '+':
        qc.h(alice.qreg[0])
    elif state == '-':
        qc.x(alice.qreg[0])
        qc.h(alice.qreg[0])
    elif state == '+i':
        qc.h(alice.qreg[0])
        qc.s(alice.qreg[0])
    qc.barrier()

    #EPR pair generation (shared two-qubit system)..
    qc.h(alice.qreg[1])
    qc.cx(alice.qreg[1], bob.qreg[0])
    qc.barrier()

    #Alice's measurement preparation..
    qc.cx(alice.qreg[0], alice.qreg[1])
    qc.h(alice.qreg[0])
    qc.barrier()

    #Alice's Measurement..
    qc.measure([alice.qreg[0], alice.qreg[1]], [alice.creg[0], alice.creg[1]])
    qc.barrier()

    #Bob applies conditional corrections..
    with qc.if_test((alice.creg[1], 1)):
        qc.x(bob.qreg[0])
        
    with qc.if_test((alice.creg[0], 1)):
        qc.z(bob.qreg[0])
    qc.barrier()

    if state == '+':
        qc.h(bob.qreg[0])       
    elif state == '-':
        qc.h(bob.qreg[0])       
    elif state == '+i':
        qc.sdg(bob.qreg[0])     
        qc.h(bob.qreg[0])       

    #Bob's measurement..
    qc.measure(bob.qreg[0], bob.creg[0])
    return qc

#Simulate circuit or run on real IBM quantum computer.
def simulate_circuit(qc, real_flag, protocol):
    
    #Ideal simulator run...
    print("-> Executing Run 1: Ideal Local Simulation")
    ideal_sampler = AerSampler()
    ideal_pub_result = ideal_sampler.run([qc]).result()[0]
    ideal_counts = ideal_pub_result.data.Bob_c.get_counts()
    print(f"\tIdeal Counts: {ideal_counts}\n")
    
    #Noisy simulator run...
    print("-> Executing Run 2: Noisy Local Simulation")
    noise_model = NoiseModel()
    noise_model.add_all_qubit_quantum_error(depolarizing_error(0.05, 1), ['x', 'h', 'z', 's'])  
    noise_model.add_all_qubit_quantum_error(depolarizing_error(0.10, 2), ['cx'])                
    
    aer_sim = AerSimulator(noise_model=noise_model)
    pm_noisy = generate_preset_pass_manager(backend=aer_sim, optimization_level=1)
    isa_qc_noisy = pm_noisy.run(qc)
    noisy_result = aer_sim.run(isa_qc_noisy, shots=1024).result()
    raw_noisy_counts = noisy_result.get_counts()
    print(f"\tNoisy Counts: {raw_noisy_counts}\n")

    if protocol == 'tp':
        noisy_counts = {}
        for bitstring, count in raw_noisy_counts.items():
            bob_bit = bitstring.split()[0]  # Extracts just Bob_c
            noisy_counts[bob_bit] = noisy_counts.get(bob_bit, 0) + count
    else:
        noisy_counts = raw_noisy_counts
        
    print(f"\tNoisy Counts: {noisy_counts}\n")

    real_counts = None

    #Run on real IBM hardware..
    if real_flag:
        print("-> Executing Run 3: Real Hardware Payload")
        with open("apikey.json", "r") as f:
            api_info = json.load(f)
            
        service = QiskitRuntimeService(channel="ibm_quantum_platform", token=api_info["apikey"])
        backend = service.least_busy(simulator=False, operational=True)
        print(f"\tTargeting QPU: {backend.name}")

        #Transpile to hardware ISA..
        pm_real = generate_preset_pass_manager(backend=backend, optimization_level=1)
        isa_qc_real = pm_real.run(qc)
        
        real_sampler = RuntimeSampler(mode=backend)
        job = real_sampler.run([isa_qc_real], shots=1024)
        print(f"   Job queued. ID: {job.job_id()}")
        
        real_pub_result = job.result()[0] 
        real_counts = real_pub_result.data.Bob_c.get_counts()

    return ideal_counts, noisy_counts, real_counts

def main():
    parser = argparse.ArgumentParser(description="Quantum Communication Protocols")
    parser.add_argument("-r", "--real", action="store_true", 
                        help="Execute on real IBM Quantum hardware instead of local simulation")
    parser.add_argument("-p", "--protocol", choices=['sdc', 'tp'], required=True,
                        help="Select protocol: 'sdc' (Superdense Coding) or 'tp' (Teleportation)")
    args = parser.parse_args()

    master_payload = {
        "protocol": "Superdense Coding" if args.protocol == 'sdc' else "Teleportation",
        "runs": {}
    }

    if args.protocol == 'sdc':
        alice = Person("Alice", num_qubits=1)
        bob = Person("Bob", num_qubits=1, num_cbits=2)
        messages = ['00', '01', '10', '11']
        circuits = {msg: setup_sdc_circuit(alice, bob, msg) for msg in messages}

        for msg, qc in circuits.items():
            print(f"\n--- Simulating SDC for message: {msg} ---")
            ideal_c, noisy_c, real_c = simulate_circuit(qc, args.real, args.protocol)
            
            master_payload["runs"][msg] = {
                "ideal_execution": ideal_c,
                "noisy_execution": noisy_c,
                "real_execution": real_c
            }

        with open("json_files/sdc_master_results.json", "w") as f:
            json.dump(master_payload, f, indent=4)
        print("\n[+] SDC data serialized to sdc_master_results.json")

    #Teleport sequence.
    elif args.protocol == 'tp':
        alice = Person("Alice", num_qubits=2, num_cbits=2)
        bob = Person("Bob", num_qubits=1, num_cbits=1)

        states = ['0', '1', '+', '-', "+i"]
        circuits = {s: setup_tp_circuit(alice, bob, s) for s in states}
        
        for s, qc in circuits.items():
            print(f"\n--- Simulating Teleportation for state: {s} ---")
            ideal_c, noisy_c, real_c = simulate_circuit(qc, args.real, args.protocol)
            
            master_payload["runs"][s] = {
                "ideal_execution": ideal_c,
                "noisy_execution": noisy_c,
                "real_execution": real_c
            }

        with open("json_files/tp_master_results.json", "w") as f:
            json.dump(master_payload, f, indent=4)
        print("\n[+] Teleportation data serialized to tp_master_results.json")

if __name__ == "__main__":
    main()
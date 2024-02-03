import numpy as np

from qiskit import QuantumCircuit 
from qiskit.circuit import ParameterVector

def alternating_sq_2q_layers(num_qubits, depths = 1, two_q_gate_type = None, connectivity = None):
    """
    num_qubits: int
                number of qubits for quantum circuit
                
    depths: int
            number of repetitions for alternating layers
            it should be at least 1
            
    two_q_gate_type: str
                     type of two qubit entangling gates, RXX, RYY, RZX, RZZ
    
    connectivity: list
                  coupling maps for two qubit gates, all-to-all or custom connectivity can be used
    
    """
    
    qubits = [i for i in range(num_qubits)]
    num_params = (2+3*(depths-1))* num_qubits + len(connectivity) * 1 * depths # number of parameters needed for single qubit gate + two qubit gate (which equals to 1, always)
    params = ParameterVector('x', num_params)
    num_2q_gates = len(connectivity)
    
    circuit = QuantumCircuit(num_qubits)
    two_qubit_gate = getattr(circuit, two_q_gate_type.lower())
    
    params_counts = 0
    # initial arbitrary single qubit layer and two qubit layer
    for i, qubit in enumerate(qubits):
        circuit.rx(params[2*i], qubit)
        circuit.rz(params[2*i+1], qubit)
        params_counts += 2
    
    bias = params_counts
    for i in range(num_2q_gates):
        two_qubit_gate(params[i+bias], qubit1 = connectivity[i][0], qubit2 = connectivity[i][1])
        params_counts += 1
    
    if depths > 1: 
        for _ in range(depths-1):
            bias = params_counts
            for i, qubit in enumerate(qubits):
                circuit.rz(params[3*i + bias], qubit)
                circuit.rx(params[3*i+1 + bias], qubit)
                circuit.rz(params[3*i+2 + bias], qubit)
                params_counts += 3
                
            bias = params_counts
            for i in range(num_2q_gates):
                two_qubit_gate(params[i+bias], qubit1 = connectivity[i][0], qubit2 = connectivity[i][1])
                params_counts += 1
    else:
        pass
      
    return circuit
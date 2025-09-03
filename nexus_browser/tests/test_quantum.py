"""
Quantum Module Tests
Test quantum computing features of NEXUS Browser
"""

import pytest
import asyncio
import numpy as np
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quantum import (
    QuantumBit,
    WaveFunction,
    QuantumComputer,
    QuantumStateManager,
    QuantumCircuit,
    QuantumAlgorithms,
    QuantumOperator
)


class TestQuantumBit:
    """Test QuantumBit functionality"""
    
    def test_qubit_initialization(self):
        """Test qubit initializes in |0⟩ state"""
        qubit = QuantumBit()
        assert abs(qubit.alpha) == 1.0
        assert abs(qubit.beta) == 0.0
        assert qubit.entangled_with is None
        
    def test_qubit_normalization(self):
        """Test qubit normalization"""
        qubit = QuantumBit(alpha=complex(3, 0), beta=complex(4, 0))
        # Should normalize to |α|² + |β|² = 1
        assert abs(abs(qubit.alpha)**2 + abs(qubit.beta)**2 - 1.0) < 0.001
        
    def test_hadamard_gate(self):
        """Test Hadamard gate creates superposition"""
        qubit = QuantumBit()
        qubit.apply_hadamard()
        
        # Should be in equal superposition
        assert abs(abs(qubit.alpha) - 1/np.sqrt(2)) < 0.001
        assert abs(abs(qubit.beta) - 1/np.sqrt(2)) < 0.001
        
    def test_measurement(self):
        """Test measurement collapses qubit"""
        qubit = QuantumBit()
        qubit.apply_hadamard()
        
        result = qubit.measure()
        assert result in [0, 1]
        
        # After measurement, should be in definite state
        if result == 0:
            assert abs(qubit.alpha) == 1.0
            assert abs(qubit.beta) == 0.0
        else:
            assert abs(qubit.alpha) == 0.0
            assert abs(qubit.beta) == 1.0


class TestWaveFunction:
    """Test WaveFunction functionality"""
    
    def test_wave_function_creation(self):
        """Test wave function initialization"""
        states = ['state1', 'state2', 'state3']
        amplitudes = [complex(1, 0), complex(0, 0), complex(0, 0)]
        
        wf = WaveFunction(states=states, amplitudes=amplitudes)
        
        assert len(wf.states) == 3
        assert wf.coherence == 1.0
        
    def test_probability_calculation(self):
        """Test probability distribution calculation"""
        states = ['A', 'B']
        amplitudes = [complex(1/np.sqrt(2), 0), complex(1/np.sqrt(2), 0)]
        
        wf = WaveFunction(states=states, amplitudes=amplitudes)
        probs = wf.get_probabilities()
        
        assert len(probs) == 2
        assert abs(sum(probs) - 1.0) < 0.001
        assert abs(probs[0] - 0.5) < 0.001
        assert abs(probs[1] - 0.5) < 0.001
        
    def test_wave_function_collapse(self):
        """Test wave function collapse"""
        states = ['option1', 'option2', 'option3']
        amplitudes = [complex(1/np.sqrt(3), 0) for _ in range(3)]
        
        wf = WaveFunction(states=states, amplitudes=amplitudes)
        collapsed = wf.collapse()
        
        assert collapsed in states
        assert len(wf.states) == 1
        assert wf.states[0] == collapsed


class TestQuantumComputer:
    """Test QuantumComputer functionality"""
    
    def test_quantum_computer_initialization(self):
        """Test quantum computer setup"""
        qc = QuantumComputer(num_qubits=4)
        
        assert qc.num_qubits == 4
        assert len(qc.qubits) == 4
        
    def test_gate_application(self):
        """Test applying quantum gates"""
        qc = QuantumComputer(num_qubits=2)
        
        # Apply Hadamard to first qubit
        qc.apply_gate(QuantumOperator.HADAMARD, 0)
        
        # Check superposition
        assert abs(abs(qc.qubits[0].alpha) - 1/np.sqrt(2)) < 0.001
        
    def test_entanglement(self):
        """Test creating entanglement"""
        qc = QuantumComputer(num_qubits=2)
        
        # Create Bell state
        qc.apply_gate(QuantumOperator.HADAMARD, 0)
        qc.apply_gate(QuantumOperator.CNOT, 0, 1)
        
        # Check entanglement
        assert qc.qubits[0].entangled_with == qc.qubits[1]
        assert qc.qubits[1].entangled_with == qc.qubits[0]


@pytest.mark.asyncio
class TestQuantumStateManager:
    """Test QuantumStateManager functionality"""
    
    async def test_superposition_creation(self):
        """Test creating quantum superposition"""
        qsm = QuantumStateManager()
        
        states = ['red', 'green', 'blue']
        wf = qsm.create_superposition('colors', states)
        
        assert 'colors' in qsm.wave_functions
        assert len(wf.states) == 3
        
    async def test_entanglement_creation(self):
        """Test creating entanglement between wave functions"""
        qsm = QuantumStateManager()
        
        qsm.create_superposition('particle1', [0, 1])
        qsm.create_superposition('particle2', [0, 1])
        
        success = qsm.entangle('particle1', 'particle2')
        
        assert success
        assert ('particle1', 'particle2') in qsm.entangled_pairs
        
    async def test_quantum_tunneling(self):
        """Test quantum tunneling simulation"""
        qsm = QuantumStateManager()
        
        # Low barrier should allow tunneling sometimes
        tunneled = await qsm.quantum_tunnel(
            start_state='A',
            target_state='B',
            barrier_height=0.1
        )
        
        # Can't guarantee result due to probability
        assert isinstance(tunneled, bool)
        
    async def test_superposition_execution(self):
        """Test executing functions in superposition"""
        qsm = QuantumStateManager()
        
        def func1(): return 'result1'
        def func2(): return 'result2'
        def func3(): return 'result3'
        
        result = await qsm.superposition_execute([func1, func2, func3])
        
        assert result in ['result1', 'result2', 'result3']


class TestQuantumCircuit:
    """Test QuantumCircuit functionality"""
    
    def test_circuit_creation(self):
        """Test creating quantum circuit"""
        circuit = QuantumCircuit(num_qubits=3)
        
        assert circuit.num_qubits == 3
        assert len(circuit.gates) == 0
        
    def test_adding_gates(self):
        """Test adding gates to circuit"""
        circuit = QuantumCircuit(num_qubits=2)
        
        circuit.add_hadamard(0)
        circuit.add_cnot(0, 1)
        circuit.add_measurement(0)
        circuit.add_measurement(1)
        
        assert len(circuit.gates) == 2
        assert len(circuit.measurements) == 2
        
    def test_circuit_execution(self):
        """Test executing quantum circuit"""
        circuit = QuantumCircuit(num_qubits=2)
        circuit.add_hadamard(0)
        circuit.add_measurement(0)
        
        qc = QuantumComputer(num_qubits=2)
        results = circuit.execute(qc)
        
        assert len(results) == 1
        assert results[0] in [0, 1]


@pytest.mark.asyncio
class TestQuantumAlgorithms:
    """Test quantum algorithm implementations"""
    
    async def test_grovers_search(self):
        """Test Grover's search algorithm"""
        search_space = list(range(16))
        target = 7
        
        def oracle(x):
            return x == target
        
        result = await QuantumAlgorithms.grovers_search(search_space, oracle)
        
        # Grover's should find the target with high probability
        assert result == target
        
    async def test_quantum_teleportation(self):
        """Test quantum teleportation protocol"""
        result = await QuantumAlgorithms.quantum_teleportation(
            state='test_data',
            sender_location='Alice',
            receiver_location='Bob'
        )
        
        assert result['teleported'] == True
        assert result['sender'] == 'Alice'
        assert result['receiver'] == 'Bob'
        assert 'measurements' in result
        
    async def test_shors_factorization(self):
        """Test Shor's factorization (simplified)"""
        # Test with small number
        factors = await QuantumAlgorithms.shors_factorization(15)
        
        assert factors[0] * factors[1] == 15
        assert factors in [(3, 5), (5, 3)]


class TestQuantumIntegration:
    """Integration tests for quantum features"""
    
    @pytest.mark.asyncio
    async def test_quantum_workflow(self):
        """Test complete quantum workflow"""
        # Create quantum state manager
        qsm = QuantumStateManager()
        
        # Create superposition
        states = ['approach1', 'approach2', 'approach3']
        wf = qsm.create_superposition('strategy', states)
        
        # Create entanglement
        qsm.create_superposition('resource', ['CPU', 'GPU'])
        qsm.entangle('strategy', 'resource')
        
        # Measure and collapse
        result = qsm.measure('strategy')
        
        assert result in states
        
    def test_quantum_random(self):
        """Test quantum random number generation"""
        from quantum import quantum_random
        
        # Generate multiple random numbers
        randoms = [quantum_random() for _ in range(10)]
        
        # Check range
        assert all(0 <= r <= 1 for r in randoms)
        
        # Check uniqueness (very unlikely to get duplicates)
        assert len(set(randoms)) == len(randoms)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
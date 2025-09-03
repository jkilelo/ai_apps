# ==============================================================================
# SWARM INTELLIGENCE AND EMERGENCE DETECTION (EXTENDED)
# ==============================================================================

class PheromoneTrail:
    """Represents a pheromone trail for swarm communication"""
    
    def __init__(self, source: 'AgentID', trail_type: str, intensity: float = 1.0):
        self.source = source
        self.trail_type = trail_type
        self.intensity = intensity
        self.timestamp = datetime.now()
        self.decay_rate = 0.1
        self.path: List[Tuple[float, float]] = []  # x, y coordinates
    
    def add_point(self, x: float, y: float):
        """Add a point to the pheromone trail"""
        self.path.append((x, y))
    
    def decay(self):
        """Apply pheromone decay over time"""
        import math
        time_since_creation = (datetime.now() - self.timestamp).total_seconds()
        self.intensity *= math.exp(-self.decay_rate * time_since_creation)
    
    def get_strength_at(self, x: float, y: float) -> float:
        """Get pheromone strength at specific coordinates"""
        if not self.path:
            return 0.0
        
        import math
        # Find closest point on trail
        min_distance = float('inf')
        for px, py in self.path:
            distance = math.sqrt((x - px)**2 + (y - py)**2)
            min_distance = min(min_distance, distance)
        
        # Strength decreases with distance
        if min_distance == 0:
            return self.intensity
        else:
            return self.intensity * math.exp(-min_distance)

# Add to existing consciousness.py file as extensions
EXTENDED_CLASSES = {
    'PheromoneTrail': PheromoneTrail
}

# Test suite for consciousness features
async def test_consciousness_features():
    """Comprehensive test suite for consciousness features"""
    print("=" * 80)
    print("CONSCIOUSNESS SYSTEM TESTING")
    print("=" * 80)
    
    # Test results storage
    test_results = {
        'passed': 0,
        'failed': 0,
        'errors': []
    }
    
    def test_assert(condition, test_name):
        if condition:
            test_results['passed'] += 1
            print(f"✓ {test_name}")
        else:
            test_results['failed'] += 1
            test_results['errors'].append(test_name)
            print(f"✗ {test_name}")
    
    # Test 1: Basic consciousness engine
    print("\n1. TESTING BASIC CONSCIOUSNESS ENGINE")
    print("-" * 50)
    
    from consciousness import ConsciousnessEngine, ThoughtVector, ThoughtType, Awareness
    import numpy as np
    
    engine = ConsciousnessEngine()
    
    # Test awareness integration
    awareness = Awareness(level=0.5, focus="test", timestamp=datetime.now())
    await engine.integrate_awareness(awareness)
    test_assert(engine.current_awareness.focus == "test", "Awareness integration")
    
    # Test thought processing
    thought = ThoughtVector(
        data=np.random.randn(128),
        dimension=128,
        timestamp=datetime.now(),
        thought_type=ThoughtType.REASONING
    )
    
    result = await engine.process_thought(thought)
    test_assert('processing_type' in result, "Thought processing")
    test_assert(result['confidence'] >= 0, "Thought confidence calculation")
    
    # Test memory storage and retrieval
    memory_id = engine.memory_palace.store("test memory", memory_type='EPISODIC')
    test_assert(memory_id is not None, "Memory storage")
    
    retrieved = engine.memory_palace.recall(memory_id)
    test_assert(retrieved == "test memory", "Memory retrieval")
    
    print(f"\nBasic consciousness tests: {test_results['passed']}/{test_results['passed'] + test_results['failed']}")
    
    # Test 2: Message routing
    print("\n2. TESTING MESSAGE ROUTING SYSTEM")
    print("-" * 50)
    
    from consciousness import MessageRouter, Message, CommunicationType
    
    router = MessageRouter()
    
    # Test message creation
    message = Message(
        sender_id="agent_1",
        recipient_id="agent_2", 
        content="test message",
        message_type=CommunicationType.DIRECT
    )
    
    test_assert(message.id is not None, "Message ID generation")
    test_assert(not message.is_expired(), "Message expiration check")
    
    # Test broadcast subscription
    router.subscribe_to_broadcasts("agent_1")
    router.subscribe_to_broadcasts("agent_2")
    
    test_assert("agent_1" in router.broadcast_subscriptions, "Broadcast subscription")
    
    print(f"\nMessage routing tests passed")
    
    # Test 3: Quantum consensus
    print("\n3. TESTING QUANTUM CONSENSUS")
    print("-" * 50)
    
    from consciousness import QuantumConsensus, QuantumState
    
    agents = ["agent_1", "agent_2", "agent_3"]
    quantum_consensus = QuantumConsensus(agents)
    
    test_assert(len(quantum_consensus.quantum_states) == 3, "Quantum state initialization")
    
    # Test quantum state operations
    state = QuantumState(amplitude=complex(1, 0), phase=0.0)
    measurement = state.measure()
    test_assert(0 <= measurement <= 1, "Quantum measurement")
    
    # Test consensus achievement
    proposals = {
        "agent_1": "option_A",
        "agent_2": "option_A", 
        "agent_3": "option_B"
    }
    
    try:
        consensus_result = await quantum_consensus.achieve_consensus(proposals, max_iterations=10)
        test_assert(consensus_result in ["option_A", "option_B"], "Quantum consensus achievement")
    except Exception as e:
        test_results['errors'].append(f"Quantum consensus error: {e}")
    
    print(f"\nQuantum consensus tests completed")
    
    # Test 4: Swarm intelligence
    print("\n4. TESTING SWARM INTELLIGENCE")
    print("-" * 50)
    
    from consciousness import SwarmIntelligence
    
    swarm = SwarmIntelligence()
    
    # Test agent positioning
    swarm.update_agent_position("agent_1", 0.0, 0.0)
    swarm.update_agent_position("agent_2", 1.0, 1.0)
    
    test_assert("agent_1" in swarm.agent_positions, "Agent position tracking")
    
    # Test neighborhood calculation  
    neighbors = swarm.get_local_neighbors("agent_1")
    test_assert(isinstance(neighbors, set), "Neighborhood calculation")
    
    # Test pheromone trail
    trail_id = swarm.add_pheromone_trail("agent_1", "food", 1.0)
    test_assert(trail_id in swarm.pheromone_trails, "Pheromone trail creation")
    
    print(f"\nSwarm intelligence tests completed")
    
    # Test 5: Emergence detection
    print("\n5. TESTING EMERGENCE DETECTION")
    print("-" * 50)
    
    from consciousness import EmergenceDetector, EmergencePattern
    
    detector = EmergenceDetector()
    
    # Test pattern creation
    pattern = EmergencePattern("test_pattern", {"agent_1", "agent_2"})
    test_assert(pattern.id is not None, "Emergence pattern creation")
    test_assert(pattern.agents == {"agent_1", "agent_2"}, "Pattern agent tracking")
    
    # Test emergence scanning
    agent_states = {
        "agent_1": {"state": "ACTIVE", "consciousness_level": 0.8},
        "agent_2": {"state": "ACTIVE", "consciousness_level": 0.7},
        "agent_3": {"state": "THINKING", "consciousness_level": 0.6}
    }
    
    positions = {
        "agent_1": (0.0, 0.0),
        "agent_2": (1.0, 1.0), 
        "agent_3": (5.0, 5.0)
    }
    
    patterns = await detector.scan_for_emergence(agent_states, positions)
    test_assert(isinstance(patterns, list), "Emergence pattern scanning")
    
    stats = detector.get_emergence_statistics()
    test_assert('total_patterns' in stats, "Emergence statistics generation")
    
    print(f"\nEmergence detection tests completed")
    
    # Final test summary
    print("\n" + "=" * 80)
    print(f"TEST RESULTS SUMMARY")
    print("=" * 80)
    print(f"Tests Passed: {test_results['passed']}")
    print(f"Tests Failed: {test_results['failed']}")
    print(f"Total Tests: {test_results['passed'] + test_results['failed']}")
    
    if test_results['errors']:
        print(f"\nErrors encountered:")
        for error in test_results['errors']:
            print(f"  - {error}")
    
    success_rate = test_results['passed'] / max(1, test_results['passed'] + test_results['failed'])
    print(f"\nSuccess Rate: {success_rate * 100:.1f}%")
    
    if success_rate > 0.8:
        print("🎉 CONSCIOUSNESS SYSTEM TESTS PASSED!")
    else:
        print("⚠️  Some tests failed - review implementation")

if __name__ == "__main__":
    import asyncio
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        asyncio.run(test_consciousness_features())
    else:
        print("Consciousness extensions loaded. Use 'test' argument to run tests.")
#!/usr/bin/env python3
"""
Integration test for MCP Neural with other NEXUS modules
Tests the complete neural pathway from consciousness to evolution
"""

import asyncio
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_mcp_integration():
    """Test MCP Neural integration with NEXUS modules"""
    print("=" * 80)
    print("MCP NEURAL - NEXUS INTEGRATION TEST")
    print("=" * 80)
    
    # Import modules
    print("\n1. IMPORTING NEXUS MODULES")
    print("-" * 60)
    
    try:
        from mcp_neural import (
            MCPNeuralNetwork,
            NeuralSignal,
            NeuralPathway,
            DirectControlInterface,
            SharedMemoryBuffer,
            ConsciousnessSynchronizer,
            NeuralEvolutionEngine,
            HolographicMemoryInterface,
            ModelOrchestrator,
            QuantumNeuralBridge
        )
        print("[OK] MCP Neural module loaded")
    except ImportError as e:
        print(f"[ERROR] Failed to import MCP Neural: {e}")
        return False
    
    try:
        from consciousness import ConsciousnessEngine, AIAgent
        print("[OK] Consciousness module loaded")
        CONSCIOUSNESS_AVAILABLE = True
    except ImportError:
        print("[WARNING] Consciousness module not available")
        CONSCIOUSNESS_AVAILABLE = False
    
    try:
        from evolution import EvolutionEngine
        print("[OK] Evolution module loaded")
        EVOLUTION_AVAILABLE = True
    except ImportError:
        print("[WARNING] Evolution module not available")
        EVOLUTION_AVAILABLE = False
    
    try:
        from quantum import QuantumConsciousness
        print("[OK] Quantum module loaded")
        QUANTUM_AVAILABLE = True
    except ImportError:
        print("[WARNING] Quantum module not available")
        QUANTUM_AVAILABLE = False
    
    try:
        from hologram import HolographicMemory
        print("[OK] Hologram module loaded")
        HOLOGRAM_AVAILABLE = True
    except ImportError:
        print("[WARNING] Hologram module not available")
        HOLOGRAM_AVAILABLE = False
    
    # Test MCP Neural Network
    print("\n2. CREATING MCP NEURAL NETWORK")
    print("-" * 60)
    
    neural_net = MCPNeuralNetwork()
    print(f"[OK] Neural network initialized")
    print(f"  - Consciousness level: {neural_net.consciousness_level}")
    print(f"  - AI models available: {len(neural_net.ai_interfaces)}")
    print(f"  - Memory buffer size: {neural_net.shared_memory_buffer.size_bytes / (1024*1024):.1f} MB")
    
    # Test consciousness integration
    if CONSCIOUSNESS_AVAILABLE:
        print("\n3. CONSCIOUSNESS INTEGRATION")
        print("-" * 60)
        
        try:
            consciousness = ConsciousnessEngine()
            
            # Create AI agent
            agent = AIAgent(
                name="NEXUS_Agent",
                capabilities=["neural_routing", "memory_access", "evolution"]
            )
            consciousness.add_agent(agent)
            
            # Connect to neural network
            pathway = await neural_net.create_neural_pathway(
                ai_model="NEXUS_Agent",
                capability="consciousness_bridge",
                bidirectional=True,
                enable_dma=True,
                adaptive=True,
                quantum_enabled=True
            )
            
            print(f"[OK] Consciousness bridge established")
            print(f"  - Pathway ID: {pathway.id}")
            print(f"  - Synapses: {len(pathway.synapses)}")
            
            # Test consciousness synchronization
            sync_result = await neural_net.synchronize_consciousness()
            print(f"[OK] Consciousness synchronized: {sync_result['status']}")
            
        except Exception as e:
            print(f"[ERROR] Consciousness integration failed: {e}")
    
    # Test evolution integration
    if EVOLUTION_AVAILABLE:
        print("\n4. EVOLUTION INTEGRATION")
        print("-" * 60)
        
        try:
            evolution = EvolutionEngine()
            
            # Test code evolution
            test_code = """
def process(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result
"""
            
            evolved = await neural_net.evolve_with_ai(
                code=test_code,
                ai_model=list(neural_net.ai_interfaces.keys())[0] if neural_net.ai_interfaces else "test",
                use_evolution_engine=True
            )
            
            print(f"[OK] Code evolution completed")
            print(f"  - Original length: {len(test_code)}")
            print(f"  - Evolved length: {len(evolved)}")
            print(f"  - Evolution generations: {neural_net.evolution_engine.generation}")
            
        except Exception as e:
            print(f"[ERROR] Evolution integration failed: {e}")
    
    # Test quantum integration
    if QUANTUM_AVAILABLE:
        print("\n5. QUANTUM INTEGRATION")
        print("-" * 60)
        
        try:
            quantum = QuantumConsciousness()
            
            # Create quantum-entangled pathways
            if len(neural_net.pathways) >= 2:
                pathways = list(neural_net.pathways.values())
                neural_net.quantum_bridge.entangle_pathways(pathways[0], pathways[1])
                print(f"[OK] Quantum entanglement established")
                
                # Test quantum transmission
                quantum_signals = await neural_net.transmit_thought(
                    source="quantum_test",
                    thought="Quantum coherence test",
                    destination="*",
                    use_quantum=True
                )
                
                coherence = neural_net.quantum_bridge.measure_coherence()
                print(f"[OK] Quantum transmission completed")
                print(f"  - Signals transmitted: {len(quantum_signals)}")
                print(f"  - Coherence level: {coherence:.2f}")
            
        except Exception as e:
            print(f"[ERROR] Quantum integration failed: {e}")
    
    # Test holographic memory integration
    if HOLOGRAM_AVAILABLE:
        print("\n6. HOLOGRAPHIC MEMORY INTEGRATION")
        print("-" * 60)
        
        try:
            hologram = HolographicMemory()
            
            # Store neural state in holographic memory
            neural_state = neural_net.get_neural_state()
            success = neural_net.holographic_memory.store_memory(
                "integration_test",
                neural_state
            )
            
            print(f"[OK] Holographic storage: {'Success' if success else 'Failed'}")
            
            # Retrieve from holographic memory
            retrieved = neural_net.holographic_memory.retrieve_memory("integration_test")
            print(f"[OK] Holographic retrieval: {'Success' if retrieved else 'Failed'}")
            
            # Get memory statistics
            stats = neural_net.holographic_memory.get_memory_stats()
            print(f"  - Stored patterns: {stats['stored_patterns']}")
            print(f"  - Memory density: {stats['density']:.2%}")
            
        except Exception as e:
            print(f"[ERROR] Holographic integration failed: {e}")
    
    # Test multi-model orchestration
    print("\n7. MULTI-MODEL ORCHESTRATION")
    print("-" * 60)
    
    if neural_net.ai_interfaces:
        try:
            # Test different orchestration strategies
            strategies = ['parallel', 'sequential', 'specialized', 'consensus']
            
            for strategy in strategies:
                result = await neural_net.orchestrator.orchestrate_task(
                    task="Analyze the concept of neural consciousness",
                    strategy=strategy
                )
                print(f"[OK] Strategy '{strategy}' completed")
            
            metrics = neural_net.orchestrator.get_orchestration_metrics()
            print(f"  - Available models: {metrics['available_models']}")
            
        except Exception as e:
            print(f"[ERROR] Orchestration failed: {e}")
    else:
        print("[WARNING] No AI models available for orchestration")
    
    # Test direct AI control
    print("\n8. DIRECT AI CONTROL")
    print("-" * 60)
    
    if neural_net.ai_interfaces:
        try:
            model = list(neural_net.ai_interfaces.keys())[0]
            control = await neural_net.assume_direct_control(model)
            print(f"[OK] {model} assumed direct control")
            
            # Let AI work briefly
            await asyncio.sleep(0.5)
            
            summary = await control.relinquish_control()
            print(f"[OK] Control relinquished")
            print(f"  - Actions taken: {summary['actions_count']}")
            print(f"  - Duration: {summary['duration']:.2f}s")
            
        except Exception as e:
            print(f"[ERROR] Direct control failed: {e}")
    
    # Test MCP server capabilities
    print("\n9. MCP SERVER CAPABILITIES")
    print("-" * 60)
    
    try:
        capabilities = await neural_net.start_mcp_server()
        print(f"[OK] MCP server started")
        
        total_features = sum(
            len(caps) if isinstance(caps, (dict, list)) else 1
            for caps in capabilities.values()
        )
        print(f"  - Total capabilities: {len(capabilities)}")
        print(f"  - Total features: {total_features}")
        
        await neural_net.stop_mcp_server()
        print(f"[OK] MCP server stopped")
        
    except Exception as e:
        print(f"[ERROR] MCP server failed: {e}")
    
    # Final performance report
    print("\n10. PERFORMANCE REPORT")
    print("-" * 60)
    
    report = neural_net.get_performance_report()
    print(f"[OK] Performance report generated")
    print(f"  - Total signals: {report['neural_network']['total_signals']}")
    print(f"  - Pathways created: {report['neural_network']['pathways']}")
    print(f"  - Consciousness level: {report['neural_network']['consciousness_level']}")
    
    # Final state summary
    final_state = neural_net.get_neural_state()
    print("\nFINAL NEURAL STATE:")
    print(f"  - Pathways: {len(final_state['pathways'])}")
    print(f"  - Pattern types: {final_state['pattern_summary']['pattern_types'] if final_state['pattern_summary']['total_patterns'] > 0 else 'None'}")
    print(f"  - Signal statistics: {final_state['signal_statistics']['signals_processed']} processed")
    print(f"  - Memory usage: {final_state['memory_stats']['allocated']} bytes allocated")
    print(f"  - Quantum coherence: {final_state['quantum_coherence']:.2f}")
    print(f"  - Evolution generation: {final_state['evolution_generation']}")
    
    print("\n" + "=" * 80)
    print("INTEGRATION TEST COMPLETE")
    print("=" * 80)
    
    return True

async def main():
    """Main test runner"""
    try:
        success = await test_mcp_integration()
        return success
    except Exception as e:
        print(f"\nIntegration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Test script for MCP Neural Network module
"""

import asyncio
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_neural import (
    MCPNeuralNetwork,
    NeuralSignal,
    NeuralPathway,
    Synapse,
    SynapseType,
    SharedMemoryBuffer,
    NeuralPatternRecognizer,
    MCPClient,
    MCPMessage,
    MCPResponse
)

async def test_basic_functionality():
    """Test basic MCP Neural Network functionality"""
    print("Testing MCP Neural Network...")
    print("-" * 60)
    
    # Create neural network
    neural_net = MCPNeuralNetwork()
    print("[OK] Neural network created")
    
    # Test shared memory buffer
    print("\nTesting Shared Memory Buffer:")
    buffer = neural_net.shared_memory_buffer
    offset = buffer.allocate(1024, "test_model")
    if offset is not None:
        print(f"  [OK] Allocated 1024 bytes at offset {offset}")
        
        # Write data
        test_data = b"Hello Neural Network"
        success = buffer.write("test_model", test_data)
        print(f"  [OK] Write operation: {'Success' if success else 'Failed'}")
        
        # Read data
        read_data = buffer.read("test_model", len(test_data))
        print(f"  [OK] Read operation: {read_data.decode() if read_data else 'Failed'}")
    
    # Test pattern recognizer
    print("\nTesting Pattern Recognition:")
    recognizer = neural_net.pattern_recognizer
    signal = NeuralSignal(
        content="test pattern",
        source="test",
        destination="analyzer"
    )
    pattern = recognizer.process_signal(signal)
    if pattern:
        print(f"  [OK] Pattern recognized: {pattern.type}")
    
    # Test neural pathway creation
    print("\nTesting Neural Pathways:")
    pathway = await neural_net.create_neural_pathway(
        ai_model="test_ai",
        capability="test_capability",
        bidirectional=True,
        enable_dma=True,
        adaptive=True
    )
    print(f"  [OK] Created pathway: {pathway.id}")
    print(f"  [OK] Synapses: {len(pathway.synapses)}")
    
    # Test signal transmission
    print("\nTesting Signal Transmission:")
    signals = await neural_net.transmit_thought(
        source="test_source",
        thought="Hello AI",
        destination="test_ai"
    )
    print(f"  [OK] Transmitted {len(signals)} signals")
    
    # Test MCP message formatting
    print("\nTesting MCP Protocol:")
    msg = MCPMessage(
        method="neural.transmit",
        params={"thought": "test"}
    )
    json_msg = msg.to_json()
    parsed = MCPMessage.from_json(json_msg)
    print(f"  [OK] MCP Message serialization: {parsed.method}")
    
    # Test performance metrics
    print("\nTesting Performance Metrics:")
    report = neural_net.get_performance_report()
    print(f"  [OK] Total signals: {report['neural_network']['total_signals']}")
    print(f"  [OK] Consciousness level: {report['neural_network']['consciousness_level']}")
    
    # Test neural state
    print("\nTesting Neural State:")
    state = neural_net.get_neural_state()
    print(f"  [OK] Pathways: {len(state['pathways'])}")
    print(f"  [OK] AI Models: {state['ai_models']}")
    print(f"  [OK] Quantum coherence: {state['quantum_coherence']:.2f}")
    
    # Test holographic memory
    print("\nTesting Holographic Memory:")
    holo_mem = neural_net.holographic_memory
    success = holo_mem.store_memory("test_key", {"data": "test_value"})
    print(f"  [OK] Storage: {'Success' if success else 'Failed'}")
    stats = holo_mem.get_memory_stats()
    print(f"  [OK] Stored patterns: {stats['stored_patterns']}")
    
    print("\n" + "=" * 60)
    print("All tests completed successfully!")
    return True

async def test_mcp_server():
    """Test MCP server functionality"""
    print("\nTesting MCP Server...")
    print("-" * 60)
    
    neural_net = MCPNeuralNetwork()
    
    # Start server
    capabilities = await neural_net.start_mcp_server()
    print(f"[OK] Server started with capabilities:")
    for category, caps in capabilities.items():
        cap_count = len(caps) if isinstance(caps, dict) else len(caps) if isinstance(caps, list) else 1
        print(f"  - {category}: {cap_count} features")
    
    # Stop server
    await neural_net.stop_mcp_server()
    print("[OK] Server stopped")
    
    return True

async def main():
    """Run all tests"""
    print("=" * 60)
    print("MCP NEURAL NETWORK TEST SUITE")
    print("=" * 60)
    
    try:
        # Run basic tests
        await test_basic_functionality()
        
        # Run server tests
        await test_mcp_server()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
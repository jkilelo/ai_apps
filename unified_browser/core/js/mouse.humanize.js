/**
 * Simulate human-like mouse movements
 */
(function() {
    'use strict';
    
    // Initialize random mouse position
    let mouseX = Math.floor(Math.random() * window.innerWidth);
    let mouseY = Math.floor(Math.random() * window.innerHeight);
    let lastMoveTime = Date.now();
    
    // Simulate subtle mouse movements
    const simulateMouseMovement = function() {
        const now = Date.now();
        const timeSinceLastMove = now - lastMoveTime;
        
        // Only move if enough time has passed (100-300ms)
        if (timeSinceLastMove < 100 + Math.random() * 200) {
            return;
        }
        
        // Add realistic jitter with occasional larger movements
        let deltaX, deltaY;
        
        if (Math.random() < 0.1) {
            // 10% chance of larger movement
            deltaX = (Math.random() - 0.5) * 50;
            deltaY = (Math.random() - 0.5) * 50;
        } else {
            // Small jitter movement
            deltaX = (Math.random() - 0.5) * 10;
            deltaY = (Math.random() - 0.5) * 10;
        }
        
        // Update position with bounds checking
        mouseX = Math.max(0, Math.min(window.innerWidth, mouseX + deltaX));
        mouseY = Math.max(0, Math.min(window.innerHeight, mouseY + deltaY));
        
        // Occasionally dispatch mouse move event (2% chance)
        if (Math.random() < 0.02) {
            const event = new MouseEvent('mousemove', {
                clientX: mouseX,
                clientY: mouseY,
                screenX: mouseX,
                screenY: mouseY,
                bubbles: true,
                cancelable: true,
                view: window
            });
            document.dispatchEvent(event);
        }
        
        lastMoveTime = now;
    };
    
    // Run simulation at random intervals
    const runSimulation = function() {
        simulateMouseMovement();
        // Schedule next movement (100-500ms)
        setTimeout(runSimulation, 100 + Math.random() * 400);
    };
    
    // Start after a delay
    setTimeout(runSimulation, 1000);
    
    // Stop after 30 seconds to avoid performance impact
    setTimeout(function() {
        // Clear by setting a flag (cleaner than trying to clear timeouts)
        window._stopMouseSimulation = true;
    }, 30000);
})();
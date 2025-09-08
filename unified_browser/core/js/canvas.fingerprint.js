/**
 * Add noise to canvas operations to prevent fingerprinting
 */
(function() {
    'use strict';
    
    const originalGetContext = HTMLCanvasElement.prototype.getContext;
    
    HTMLCanvasElement.prototype.getContext = function(contextType, ...args) {
        const context = originalGetContext.apply(this, [contextType, ...args]);
        
        if (contextType === '2d') {
            const originalGetImageData = context.getImageData;
            
            context.getImageData = function(sx, sy, sw, sh) {
                const imageData = originalGetImageData.apply(this, [sx, sy, sw, sh]);
                
                // Add very subtle noise to defeat fingerprinting
                // Only modify a tiny fraction of pixels to avoid breaking functionality
                for (let i = 0; i < imageData.data.length; i += 4) {
                    if (Math.random() < 0.0001) { // 0.01% chance
                        // Add tiny variations (1-2 points)
                        imageData.data[i] = Math.min(255, Math.max(0, imageData.data[i] + (Math.random() * 2 - 1)));
                        imageData.data[i + 1] = Math.min(255, Math.max(0, imageData.data[i + 1] + (Math.random() * 2 - 1)));
                        imageData.data[i + 2] = Math.min(255, Math.max(0, imageData.data[i + 2] + (Math.random() * 2 - 1)));
                    }
                }
                
                return imageData;
            };
            
            // Also add noise to toDataURL
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            HTMLCanvasElement.prototype.toDataURL = function(...args) {
                // Add a tiny random pixel before converting
                const ctx = this.getContext('2d');
                if (ctx) {
                    const imageData = ctx.getImageData(0, 0, this.width, this.height);
                    // Modify one random pixel slightly
                    const pixelIndex = Math.floor(Math.random() * imageData.data.length / 4) * 4;
                    imageData.data[pixelIndex] = (imageData.data[pixelIndex] + 1) % 256;
                    ctx.putImageData(imageData, 0, 0);
                }
                return originalToDataURL.apply(this, args);
            };
        }
        
        return context;
    };
})();
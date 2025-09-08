/**
 * Override permission APIs to control access
 */
(function() {
    'use strict';
    
    // Override Permissions API
    if (navigator.permissions && navigator.permissions.query) {
        const originalQuery = navigator.permissions.query.bind(navigator.permissions);
        
        navigator.permissions.query = function(parameters) {
            // Deny most permissions by default for privacy
            const deniedPermissions = [
                'geolocation', 
                'notifications', 
                'push', 
                'midi', 
                'camera', 
                'microphone', 
                'background-sync', 
                'ambient-light-sensor',
                'accelerometer', 
                'gyroscope', 
                'magnetometer',
                'clipboard-read',
                'clipboard-write'
            ];
            
            if (parameters && deniedPermissions.includes(parameters.name)) {
                return Promise.resolve({ 
                    state: 'denied',
                    onchange: null 
                });
            }
            
            // For other permissions, use original
            return originalQuery(parameters);
        };
    }
    
    // Override geolocation
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition = function(success, error) {
            if (error) {
                error({ 
                    code: 1, 
                    message: 'User denied Geolocation' 
                });
            }
        };
        
        navigator.geolocation.watchPosition = function(success, error) {
            if (error) {
                error({ 
                    code: 1, 
                    message: 'User denied Geolocation' 
                });
            }
            return Math.floor(Math.random() * 10000);
        };
        
        navigator.geolocation.clearWatch = function() {
            // Do nothing
        };
    }
    
    // Override battery API
    if (navigator.getBattery) {
        navigator.getBattery = function() {
            return Promise.reject(new Error('Battery API is disabled'));
        };
    }
})();
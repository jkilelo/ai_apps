/**
 * Block WebRTC to prevent IP leakage
 */
(function() {
    'use strict';
    
    // Create a fake RTCPeerConnection that throws errors
    const RTCPeerConnectionBlocked = function() {
        throw new Error('WebRTC is disabled for privacy protection');
    };
    
    // Block all WebRTC constructors
    if (typeof window !== 'undefined') {
        window.RTCPeerConnection = RTCPeerConnectionBlocked;
        window.webkitRTCPeerConnection = RTCPeerConnectionBlocked;
        window.mozRTCPeerConnection = RTCPeerConnectionBlocked;
        window.RTCSessionDescription = RTCPeerConnectionBlocked;
        window.RTCIceCandidate = RTCPeerConnectionBlocked;
        
        // Also block media devices
        if (navigator.mediaDevices) {
            navigator.mediaDevices.getUserMedia = function() {
                return Promise.reject(new Error('Media devices are disabled'));
            };
            
            navigator.mediaDevices.enumerateDevices = function() {
                return Promise.resolve([]);
            };
        }
        
        // Block old getUserMedia
        if (navigator.getUserMedia) {
            navigator.getUserMedia = function() {
                throw new Error('getUserMedia is disabled');
            };
        }
    }
})();
/**
 * Gesture support for native app-like interactions
 */

export class GestureManager {
    constructor() {
        this.touchStartX = 0;
        this.touchStartY = 0;
        this.touchEndX = 0;
        this.touchEndY = 0;
        this.touchStartTime = 0;
        this.isScrolling = false;
        
        // Thresholds
        this.swipeThreshold = 50;
        this.swipeTimeLimit = 300;
        this.longPressTime = 500;
        
        // Callbacks
        this.callbacks = {
            swipeLeft: [],
            swipeRight: [],
            swipeUp: [],
            swipeDown: [],
            longPress: [],
            pinch: [],
            tap: []
        };
        
        this.init();
    }
    
    init() {
        // Touch events
        document.addEventListener('touchstart', this.handleTouchStart.bind(this), { passive: false });
        document.addEventListener('touchmove', this.handleTouchMove.bind(this), { passive: false });
        document.addEventListener('touchend', this.handleTouchEnd.bind(this));
        document.addEventListener('touchcancel', this.handleTouchCancel.bind(this));
        
        // Prevent pull-to-refresh on desktop
        if (!this.isMobile()) {
            document.body.style.overscrollBehavior = 'none';
        }
    }
    
    handleTouchStart(e) {
        const touch = e.touches[0];
        this.touchStartX = touch.clientX;
        this.touchStartY = touch.clientY;
        this.touchStartTime = Date.now();
        this.isScrolling = false;
        
        // Setup long press detection
        this.longPressTimer = setTimeout(() => {
            this.triggerLongPress(e);
        }, this.longPressTime);
        
        // Handle pinch gesture start
        if (e.touches.length === 2) {
            this.handlePinchStart(e);
        }
    }
    
    handleTouchMove(e) {
        if (!this.touchStartX || !this.touchStartY) return;
        
        const touch = e.touches[0];
        const deltaX = Math.abs(touch.clientX - this.touchStartX);
        const deltaY = Math.abs(touch.clientY - this.touchStartY);
        
        // Cancel long press if moved
        if (deltaX > 10 || deltaY > 10) {
            clearTimeout(this.longPressTimer);
        }
        
        // Detect if user is scrolling vertically
        if (deltaY > deltaX && deltaY > 10) {
            this.isScrolling = true;
        }
        
        // Handle pinch gesture
        if (e.touches.length === 2) {
            this.handlePinchMove(e);
            e.preventDefault();
        }
        
        // Prevent horizontal swipe if scrolling
        if (!this.isScrolling && deltaX > deltaY) {
            e.preventDefault();
        }
    }
    
    handleTouchEnd(e) {
        clearTimeout(this.longPressTimer);
        
        if (!this.touchStartX || !this.touchStartY) return;
        
        const touch = e.changedTouches[0];
        this.touchEndX = touch.clientX;
        this.touchEndY = touch.clientY;
        
        const timeElapsed = Date.now() - this.touchStartTime;
        
        // Detect swipe
        if (timeElapsed < this.swipeTimeLimit && !this.isScrolling) {
            this.detectSwipe();
        }
        
        // Detect tap
        const deltaX = Math.abs(this.touchEndX - this.touchStartX);
        const deltaY = Math.abs(this.touchEndY - this.touchStartY);
        
        if (deltaX < 10 && deltaY < 10 && timeElapsed < 200) {
            this.triggerTap(e);
        }
        
        // Reset
        this.touchStartX = 0;
        this.touchStartY = 0;
    }
    
    handleTouchCancel() {
        clearTimeout(this.longPressTimer);
        this.touchStartX = 0;
        this.touchStartY = 0;
    }
    
    detectSwipe() {
        const deltaX = this.touchEndX - this.touchStartX;
        const deltaY = this.touchEndY - this.touchStartY;
        const absDeltaX = Math.abs(deltaX);
        const absDeltaY = Math.abs(deltaY);
        
        if (absDeltaX > this.swipeThreshold || absDeltaY > this.swipeThreshold) {
            if (absDeltaX > absDeltaY) {
                // Horizontal swipe
                if (deltaX > 0) {
                    this.trigger('swipeRight', { distance: deltaX });
                } else {
                    this.trigger('swipeLeft', { distance: Math.abs(deltaX) });
                }
            } else {
                // Vertical swipe
                if (deltaY > 0) {
                    this.trigger('swipeDown', { distance: deltaY });
                } else {
                    this.trigger('swipeUp', { distance: Math.abs(deltaY) });
                }
            }
        }
    }
    
    handlePinchStart(e) {
        const touch1 = e.touches[0];
        const touch2 = e.touches[1];
        
        this.initialPinchDistance = Math.hypot(
            touch2.clientX - touch1.clientX,
            touch2.clientY - touch1.clientY
        );
    }
    
    handlePinchMove(e) {
        if (!this.initialPinchDistance) return;
        
        const touch1 = e.touches[0];
        const touch2 = e.touches[1];
        
        const currentDistance = Math.hypot(
            touch2.clientX - touch1.clientX,
            touch2.clientY - touch1.clientY
        );
        
        const scale = currentDistance / this.initialPinchDistance;
        
        this.trigger('pinch', { scale });
    }
    
    triggerLongPress(e) {
        const touch = e.touches[0];
        this.trigger('longPress', {
            x: touch.clientX,
            y: touch.clientY,
            target: e.target
        });
        
        // Haptic feedback
        this.vibrate([10]);
    }
    
    triggerTap(e) {
        const touch = e.changedTouches[0];
        this.trigger('tap', {
            x: touch.clientX,
            y: touch.clientY,
            target: e.target
        });
    }
    
    // Public API
    on(event, callback) {
        if (this.callbacks[event]) {
            this.callbacks[event].push(callback);
        }
    }
    
    off(event, callback) {
        if (this.callbacks[event]) {
            this.callbacks[event] = this.callbacks[event].filter(cb => cb !== callback);
        }
    }
    
    trigger(event, data) {
        if (this.callbacks[event]) {
            this.callbacks[event].forEach(callback => callback(data));
        }
    }
    
    // Utility methods
    vibrate(pattern = [10]) {
        if ('vibrate' in navigator) {
            navigator.vibrate(pattern);
        }
    }
    
    isMobile() {
        return /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
    }
    
    // Pull-to-refresh implementation
    enablePullToRefresh(onRefresh) {
        let startY = 0;
        let currentY = 0;
        let pulling = false;
        const threshold = 100;
        
        const pullIndicator = document.createElement('div');
        pullIndicator.className = 'pull-refresh-indicator';
        pullIndicator.innerHTML = `
            <div class="pull-refresh-spinner">
                <svg width="24" height="24" viewBox="0 0 24 24">
                    <path d="M12 2v6l4-4-4-4M4 12a8 8 0 0 0 8 8 8 8 0 0 0 8-8" 
                          stroke="currentColor" fill="none" stroke-width="2"/>
                </svg>
            </div>
        `;
        document.body.appendChild(pullIndicator);
        
        document.addEventListener('touchstart', (e) => {
            if (window.scrollY === 0) {
                startY = e.touches[0].clientY;
                pulling = true;
            }
        });
        
        document.addEventListener('touchmove', (e) => {
            if (!pulling) return;
            
            currentY = e.touches[0].clientY;
            const deltaY = currentY - startY;
            
            if (deltaY > 0 && window.scrollY === 0) {
                e.preventDefault();
                
                const progress = Math.min(deltaY / threshold, 1);
                const rotation = progress * 180;
                
                pullIndicator.style.transform = `translateY(${deltaY * 0.5}px)`;
                pullIndicator.style.opacity = progress;
                pullIndicator.querySelector('svg').style.transform = `rotate(${rotation}deg)`;
                
                if (progress === 1) {
                    this.vibrate([10]);
                }
            }
        });
        
        document.addEventListener('touchend', async () => {
            if (!pulling) return;
            
            const deltaY = currentY - startY;
            
            if (deltaY > threshold) {
                pullIndicator.classList.add('refreshing');
                await onRefresh();
                pullIndicator.classList.remove('refreshing');
            }
            
            pullIndicator.style.transform = '';
            pullIndicator.style.opacity = '0';
            pulling = false;
            startY = 0;
            currentY = 0;
        });
    }
}
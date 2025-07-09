/**
 * Spring physics animations for natural movement
 */

export class SpringAnimation {
    constructor(options = {}) {
        this.stiffness = options.stiffness || 180;
        this.damping = options.damping || 12;
        this.mass = options.mass || 1;
        this.restVelocity = options.restVelocity || 0.001;
        this.restDisplacement = options.restDisplacement || 0.001;
        this.overshootClamping = options.overshootClamping || false;
        
        this.animations = new Map();
    }
    
    animate(element, properties, options = {}) {
        const animationId = this.generateId();
        const animation = {
            element,
            properties: {},
            onUpdate: options.onUpdate,
            onComplete: options.onComplete
        };
        
        // Initialize property animations
        Object.keys(properties).forEach(prop => {
            const current = this.getCurrentValue(element, prop);
            const target = properties[prop];
            
            animation.properties[prop] = {
                from: current,
                to: target,
                current: current,
                velocity: 0,
                complete: false
            };
        });
        
        this.animations.set(animationId, animation);
        this.startAnimation(animationId);
        
        return animationId;
    }
    
    startAnimation(animationId) {
        const animation = this.animations.get(animationId);
        if (!animation) return;
        
        let lastTime = performance.now();
        
        const frame = (currentTime) => {
            const deltaTime = Math.min((currentTime - lastTime) / 1000, 0.064); // Cap at ~16ms
            lastTime = currentTime;
            
            let allComplete = true;
            
            // Update each property
            Object.keys(animation.properties).forEach(prop => {
                const propAnim = animation.properties[prop];
                
                if (!propAnim.complete) {
                    const distance = propAnim.to - propAnim.current;
                    const spring = distance * this.stiffness;
                    const damper = propAnim.velocity * this.damping;
                    const acceleration = (spring - damper) / this.mass;
                    
                    propAnim.velocity += acceleration * deltaTime;
                    propAnim.current += propAnim.velocity * deltaTime;
                    
                    // Overshoot clamping
                    if (this.overshootClamping) {
                        if ((propAnim.to > propAnim.from && propAnim.current > propAnim.to) ||
                            (propAnim.to < propAnim.from && propAnim.current < propAnim.to)) {
                            propAnim.current = propAnim.to;
                            propAnim.velocity = 0;
                        }
                    }
                    
                    // Check if complete
                    if (Math.abs(propAnim.velocity) < this.restVelocity &&
                        Math.abs(distance) < this.restDisplacement) {
                        propAnim.current = propAnim.to;
                        propAnim.velocity = 0;
                        propAnim.complete = true;
                    } else {
                        allComplete = false;
                    }
                    
                    // Apply the animation
                    this.applyValue(animation.element, prop, propAnim.current);
                }
            });
            
            // Call update callback
            if (animation.onUpdate) {
                animation.onUpdate(animation.properties);
            }
            
            // Continue or complete
            if (allComplete) {
                this.animations.delete(animationId);
                if (animation.onComplete) {
                    animation.onComplete();
                }
            } else {
                requestAnimationFrame(frame);
            }
        };
        
        requestAnimationFrame(frame);
    }
    
    getCurrentValue(element, property) {
        switch (property) {
            case 'x':
            case 'translateX':
                return this.getTransform(element, 'translateX');
            case 'y':
            case 'translateY':
                return this.getTransform(element, 'translateY');
            case 'scale':
                return this.getTransform(element, 'scale');
            case 'rotate':
                return this.getTransform(element, 'rotate');
            case 'opacity':
                return parseFloat(window.getComputedStyle(element).opacity);
            default:
                return parseFloat(window.getComputedStyle(element)[property]) || 0;
        }
    }
    
    getTransform(element, type) {
        const transform = window.getComputedStyle(element).transform;
        
        if (transform === 'none') {
            return type === 'scale' ? 1 : 0;
        }
        
        const matrix = new DOMMatrix(transform);
        
        switch (type) {
            case 'translateX':
                return matrix.m41;
            case 'translateY':
                return matrix.m42;
            case 'scale':
                return Math.sqrt(matrix.m11 * matrix.m11 + matrix.m12 * matrix.m12);
            case 'rotate':
                return Math.atan2(matrix.m12, matrix.m11) * (180 / Math.PI);
            default:
                return 0;
        }
    }
    
    applyValue(element, property, value) {
        switch (property) {
            case 'x':
            case 'translateX':
                this.updateTransform(element, 'translateX', value);
                break;
            case 'y':
            case 'translateY':
                this.updateTransform(element, 'translateY', value);
                break;
            case 'scale':
                this.updateTransform(element, 'scale', value);
                break;
            case 'rotate':
                this.updateTransform(element, 'rotate', value);
                break;
            case 'opacity':
                element.style.opacity = value;
                break;
            default:
                element.style[property] = value + 'px';
        }
    }
    
    updateTransform(element, type, value) {
        const transforms = this.parseTransform(element.style.transform);
        
        switch (type) {
            case 'translateX':
                transforms.translateX = value + 'px';
                break;
            case 'translateY':
                transforms.translateY = value + 'px';
                break;
            case 'scale':
                transforms.scale = value;
                break;
            case 'rotate':
                transforms.rotate = value + 'deg';
                break;
        }
        
        element.style.transform = this.buildTransform(transforms);
    }
    
    parseTransform(transform) {
        const transforms = {
            translateX: '0px',
            translateY: '0px',
            scale: 1,
            rotate: '0deg'
        };
        
        if (!transform) return transforms;
        
        const translateXMatch = transform.match(/translateX\(([^)]+)\)/);
        if (translateXMatch) transforms.translateX = translateXMatch[1];
        
        const translateYMatch = transform.match(/translateY\(([^)]+)\)/);
        if (translateYMatch) transforms.translateY = translateYMatch[1];
        
        const scaleMatch = transform.match(/scale\(([^)]+)\)/);
        if (scaleMatch) transforms.scale = parseFloat(scaleMatch[1]);
        
        const rotateMatch = transform.match(/rotate\(([^)]+)\)/);
        if (rotateMatch) transforms.rotate = rotateMatch[1];
        
        return transforms;
    }
    
    buildTransform(transforms) {
        return `translateX(${transforms.translateX}) translateY(${transforms.translateY}) scale(${transforms.scale}) rotate(${transforms.rotate})`;
    }
    
    generateId() {
        return `spring_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    
    // Preset animations
    bounceIn(element, options = {}) {
        element.style.opacity = '0';
        element.style.transform = 'scale(0)';
        
        return this.animate(element, {
            opacity: 1,
            scale: 1
        }, {
            ...options,
            stiffness: 200,
            damping: 10
        });
    }
    
    slideIn(element, direction = 'left', options = {}) {
        const distance = direction === 'left' || direction === 'right' ? window.innerWidth : window.innerHeight;
        const sign = direction === 'left' || direction === 'up' ? -1 : 1;
        const axis = direction === 'left' || direction === 'right' ? 'x' : 'y';
        
        element.style.transform = `translate${axis.toUpperCase()}(${sign * distance}px)`;
        
        return this.animate(element, {
            [axis]: 0
        }, options);
    }
    
    shake(element, options = {}) {
        const intensity = options.intensity || 10;
        const originalX = this.getCurrentValue(element, 'x');
        
        // Create shake sequence
        const shakeSequence = [
            { x: originalX + intensity },
            { x: originalX - intensity },
            { x: originalX + intensity / 2 },
            { x: originalX - intensity / 2 },
            { x: originalX }
        ];
        
        let index = 0;
        const nextShake = () => {
            if (index < shakeSequence.length) {
                this.animate(element, shakeSequence[index], {
                    onComplete: nextShake,
                    stiffness: 300,
                    damping: 8
                });
                index++;
            }
        };
        
        nextShake();
    }
}

// Export singleton instance
export const springAnimation = new SpringAnimation();

// Ripple effect for buttons
export function addRippleEffect(element) {
    element.addEventListener('click', function(e) {
        const ripple = document.createElement('span');
        ripple.className = 'ripple';
        
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        
        this.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 600);
    });
}
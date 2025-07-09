// State Manager Module - Simple state management without framework

export class StateManager {
    constructor() {
        this.state = new Map();
        this.listeners = new Map();
        this.history = [];
        this.maxHistory = 50;
    }
    
    // Get state value
    get(key) {
        return this.state.get(key);
    }
    
    // Set state value
    set(key, value) {
        const oldValue = this.state.get(key);
        this.state.set(key, value);
        
        // Add to history
        this.addToHistory({ key, oldValue, newValue: value, timestamp: Date.now() });
        
        // Notify listeners
        this.notify(key, value, oldValue);
        
        return this;
    }
    
    // Update state with partial values (for objects)
    update(key, updates) {
        const current = this.get(key);
        
        if (typeof current === 'object' && current !== null) {
            const newValue = { ...current, ...updates };
            this.set(key, newValue);
        } else {
            this.set(key, updates);
        }
        
        return this;
    }
    
    // Delete state value
    delete(key) {
        const oldValue = this.state.get(key);
        this.state.delete(key);
        
        // Add to history
        this.addToHistory({ key, oldValue, newValue: undefined, timestamp: Date.now() });
        
        // Notify listeners
        this.notify(key, undefined, oldValue);
        
        return this;
    }
    
    // Clear all state
    clear() {
        this.state.clear();
        this.history = [];
        this.listeners.clear();
    }
    
    // Subscribe to state changes
    subscribe(key, callback) {
        if (!this.listeners.has(key)) {
            this.listeners.set(key, new Set());
        }
        
        this.listeners.get(key).add(callback);
        
        // Return unsubscribe function
        return () => {
            const callbacks = this.listeners.get(key);
            if (callbacks) {
                callbacks.delete(callback);
                if (callbacks.size === 0) {
                    this.listeners.delete(key);
                }
            }
        };
    }
    
    // Subscribe to any state change
    subscribeAll(callback) {
        return this.subscribe('*', callback);
    }
    
    // Notify listeners
    notify(key, newValue, oldValue) {
        // Notify specific key listeners
        const callbacks = this.listeners.get(key);
        if (callbacks) {
            callbacks.forEach(callback => {
                try {
                    callback(newValue, oldValue, key);
                } catch (error) {
                    console.error('State listener error:', error);
                }
            });
        }
        
        // Notify global listeners
        const globalCallbacks = this.listeners.get('*');
        if (globalCallbacks) {
            globalCallbacks.forEach(callback => {
                try {
                    callback({ key, newValue, oldValue });
                } catch (error) {
                    console.error('Global state listener error:', error);
                }
            });
        }
    }
    
    // Add to history
    addToHistory(entry) {
        this.history.push(entry);
        
        // Limit history size
        if (this.history.length > this.maxHistory) {
            this.history = this.history.slice(-this.maxHistory);
        }
    }
    
    // Get history
    getHistory(key) {
        if (key) {
            return this.history.filter(entry => entry.key === key);
        }
        return [...this.history];
    }
    
    // Undo last change
    undo() {
        if (this.history.length === 0) return false;
        
        const lastEntry = this.history.pop();
        
        if (lastEntry.oldValue === undefined) {
            this.state.delete(lastEntry.key);
        } else {
            this.state.set(lastEntry.key, lastEntry.oldValue);
        }
        
        // Notify without adding to history
        this.notify(lastEntry.key, lastEntry.oldValue, lastEntry.newValue);
        
        return true;
    }
    
    // Create computed state
    computed(key, dependencies, computeFn) {
        // Initial computation
        const compute = () => {
            const values = dependencies.map(dep => this.get(dep));
            return computeFn(...values);
        };
        
        this.set(key, compute());
        
        // Subscribe to dependencies
        dependencies.forEach(dep => {
            this.subscribe(dep, () => {
                this.set(key, compute());
            });
        });
        
        return this;
    }
    
    // Persist state to localStorage
    persist(key, storageKey) {
        // Load from storage
        const stored = localStorage.getItem(storageKey);
        if (stored) {
            try {
                this.set(key, JSON.parse(stored));
            } catch (e) {
                console.error('Failed to parse stored state:', e);
            }
        }
        
        // Save on change
        this.subscribe(key, (value) => {
            if (value === undefined) {
                localStorage.removeItem(storageKey);
            } else {
                localStorage.setItem(storageKey, JSON.stringify(value));
            }
        });
        
        return this;
    }
    
    // Create a scoped state manager
    scope(prefix) {
        const scopedState = new StateManager();
        
        // Override methods to add prefix
        const originalSet = scopedState.set.bind(scopedState);
        const originalGet = scopedState.get.bind(scopedState);
        const originalDelete = scopedState.delete.bind(scopedState);
        
        scopedState.set = (key, value) => originalSet(`${prefix}.${key}`, value);
        scopedState.get = (key) => originalGet(`${prefix}.${key}`);
        scopedState.delete = (key) => originalDelete(`${prefix}.${key}`);
        
        return scopedState;
    }
    
    // Export state as object
    toObject() {
        return Object.fromEntries(this.state);
    }
    
    // Import state from object
    fromObject(obj) {
        Object.entries(obj).forEach(([key, value]) => {
            this.set(key, value);
        });
        return this;
    }
}

// Global state instance
export const globalState = new StateManager();

// React-like hooks for state (can be used in Web Components)
export function useState(initialValue) {
    const key = Symbol('state');
    globalState.set(key, initialValue);
    
    return [
        () => globalState.get(key),
        (newValue) => globalState.set(key, newValue),
        (callback) => globalState.subscribe(key, callback)
    ];
}

export function useReducer(reducer, initialState) {
    const [getState, setState, subscribe] = useState(initialState);
    
    const dispatch = (action) => {
        const currentState = getState();
        const newState = reducer(currentState, action);
        setState(newState);
    };
    
    return [getState, dispatch, subscribe];
}
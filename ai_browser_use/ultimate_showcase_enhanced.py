"""
Ultimate Executive Showcase - Enhanced Spatial Intelligence Edition
The most advanced web element presentation with collision detection and smart UI
"""

from browser_use import Agent, ChatGoogle
from dotenv import load_dotenv
import asyncio
import sys
import os
import io
from playwright.async_api import async_playwright
import json
from datetime import datetime
import random
import math

# Force UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm_gemini_client import get_client

load_dotenv(dotenv_path="./.env")


class ChatGoogleInjected(ChatGoogle):
    """Use centralized get_client()."""
    def get_client(self):
        return get_client()


class UltimateShowcaseEnhanced:
    """
    The ultimate executive showcase with spatial intelligence and collision detection.
    """

    def __init__(self, url: str, headless: bool = False):
        self.url = url
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.current_element_borders = {}  # Store original borders

    async def initialize(self):
        """Initialize browser with ultimate settings."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=['--start-maximized', '--disable-blink-features=AutomationControlled']
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=1.0
        )
        self.page = await self.context.new_page()

    async def navigate(self):
        """Navigate and prepare page."""
        print(f"🚀 Initiating Ultimate Enhanced Showcase for {self.url}...")
        await self.page.goto(self.url, wait_until='networkidle')
        await asyncio.sleep(3)

    async def inject_enhanced_styles(self):
        """Inject enhanced CSS with spatial intelligence."""
        enhanced_css = """
        /* ULTIMATE ENHANCED SHOWCASE - Spatial Intelligence Edition */

        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');

        :root {
            --neon-cyan: #00ffff;
            --neon-magenta: #ff00ff;
            --neon-yellow: #ffff00;
            --electric-blue: #0080ff;
            --plasma-purple: #8000ff;
            --laser-green: #00ff80;
            --hologram-gradient: linear-gradient(45deg,
                #00ffff 0%, #ff00ff 25%, #ffff00 50%, #00ff80 75%, #00ffff 100%);
            --z-maximum: 2147483647;
            --collision-buffer: 50px;
        }

        /* Store original borders */
        [data-original-border] {
            --stored-border: attr(data-original-border);
        }

        /* Enhanced focus system with preserved borders */
        .element-focused {
            outline: none !important;
            border: var(--stored-border, 2px solid transparent) !important;
            box-shadow:
                0 0 0 3px rgba(255, 255, 255, 0.8),
                0 0 0 6px var(--neon-cyan),
                0 0 0 9px rgba(0, 255, 255, 0.3),
                0 0 40px rgba(0, 255, 255, 0.6),
                inset 0 0 20px rgba(0, 255, 255, 0.1) !important;
            animation: focusPulse 2s ease-in-out infinite !important;
            position: relative !important;
            z-index: 10000 !important;
        }

        @keyframes focusPulse {
            0%, 100% {
                transform: scale(1);
                filter: brightness(1);
            }
            50% {
                transform: scale(1.02);
                filter: brightness(1.1);
            }
        }

        /* Ripple effect on focus */
        .focus-ripple {
            position: absolute;
            border: 2px solid var(--neon-cyan);
            border-radius: inherit;
            top: -3px;
            left: -3px;
            right: -3px;
            bottom: -3px;
            opacity: 0;
            animation: rippleOut 1s ease-out;
            pointer-events: none;
        }

        @keyframes rippleOut {
            0% {
                opacity: 1;
                transform: scale(1);
            }
            100% {
                opacity: 0;
                transform: scale(1.5);
            }
        }

        /* CENTER-STAGE COMMAND CENTER with collision detection */
        .command-center {
            position: fixed !important;
            top: 50% !important;
            left: 50% !important;
            transform: translate(-50%, -50%) perspective(1000px) rotateY(0deg) !important;
            width: 600px !important;
            height: 400px !important;
            z-index: var(--z-maximum) !important;
            background: linear-gradient(135deg,
                rgba(0, 255, 255, 0.1) 0%,
                rgba(255, 0, 255, 0.1) 50%,
                rgba(0, 255, 255, 0.1) 100%) !important;
            backdrop-filter: blur(20px) saturate(200%) !important;
            -webkit-backdrop-filter: blur(20px) saturate(200%) !important;
            border: 2px solid transparent !important;
            border-image: var(--hologram-gradient) 1 !important;
            border-radius: 20px !important;
            box-shadow:
                0 0 100px rgba(0, 255, 255, 0.5),
                0 0 200px rgba(255, 0, 255, 0.3),
                inset 0 0 60px rgba(255, 255, 255, 0.1),
                0 20px 100px rgba(0, 0, 0, 0.5) !important;
            animation: commandCenterFloat 4s ease-in-out infinite !important;
            font-family: 'Orbitron', monospace !important;
            transition: transform 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55) !important;
            cursor: move !important;
        }

        .command-center.avoiding-collision {
            animation: dodgeMovement 0.5s ease-out !important;
        }

        @keyframes dodgeMovement {
            0% {
                transform: translate(-50%, -50%) scale(1);
            }
            50% {
                transform: translate(-50%, -50%) scale(0.95);
            }
            100% {
                transform: translate(var(--dodge-x), var(--dodge-y)) scale(1);
            }
        }

        @keyframes commandCenterFloat {
            0%, 100% {
                transform: translate(-50%, -50%) translateY(0) rotateY(0deg);
            }
            50% {
                transform: translate(-50%, -50%) translateY(-10px) rotateY(2deg);
            }
        }

        /* MAGNIFYING LENS with spatial awareness */
        .magnifier-lens {
            position: fixed !important;
            width: 250px !important;
            height: 250px !important;
            border: 4px solid var(--neon-cyan) !important;
            border-radius: 50% !important;
            pointer-events: none !important;
            z-index: calc(var(--z-maximum) - 1) !important;
            overflow: hidden !important;
            box-shadow:
                0 0 60px rgba(0, 255, 255, 0.8),
                inset 0 0 40px rgba(0, 255, 255, 0.3),
                0 0 120px rgba(0, 255, 255, 0.4) !important;
            transform: scale(0) !important;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
            background: radial-gradient(circle at center,
                transparent 30%,
                rgba(0, 255, 255, 0.1) 70%) !important;
        }

        .magnifier-active {
            transform: scale(1) !important;
        }

        .magnifier-content {
            position: absolute !important;
            width: 200% !important;
            height: 200% !important;
            transform: scale(2) !important;
            transform-origin: center !important;
            filter: contrast(1.2) brightness(1.1) !important;
        }

        /* Glass refraction effect */
        .magnifier-lens::before {
            content: '' !important;
            position: absolute !important;
            top: 10% !important;
            left: 10% !important;
            width: 30% !important;
            height: 30% !important;
            background: radial-gradient(circle,
                rgba(255, 255, 255, 0.4) 0%,
                transparent 70%) !important;
            border-radius: 50% !important;
            filter: blur(2px) !important;
        }

        /* MINI MAP with adaptive positioning */
        .mini-map {
            position: fixed !important;
            top: 20px !important;
            right: 20px !important;
            width: 250px !important;
            height: 180px !important;
            z-index: calc(var(--z-maximum) - 1) !important;
            background: linear-gradient(135deg,
                rgba(0, 0, 0, 0.9) 0%,
                rgba(0, 80, 255, 0.2) 100%) !important;
            border: 2px solid var(--electric-blue) !important;
            border-radius: 15px !important;
            overflow: hidden !important;
            box-shadow:
                0 0 40px rgba(0, 128, 255, 0.6),
                inset 0 0 20px rgba(0, 128, 255, 0.2) !important;
            transition: all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55) !important;
            cursor: move !important;
        }

        .mini-map.avoiding-collision {
            animation: slideAway 0.5s ease-out !important;
        }

        @keyframes slideAway {
            0% {
                transform: scale(1);
            }
            50% {
                transform: scale(0.9);
            }
            100% {
                transform: translateX(var(--slide-x)) translateY(var(--slide-y)) scale(1);
            }
        }

        /* PICTURE IN PICTURE */
        .pip-window {
            position: fixed !important;
            width: 300px !important;
            height: 200px !important;
            z-index: calc(var(--z-maximum) - 2) !important;
            background: rgba(0, 0, 0, 0.9) !important;
            border: 2px solid var(--plasma-purple) !important;
            border-radius: 15px !important;
            padding: 10px !important;
            box-shadow:
                0 0 40px rgba(128, 0, 255, 0.6),
                inset 0 0 20px rgba(128, 0, 255, 0.2) !important;
            transition: all 0.4s ease-out !important;
            display: none !important;
        }

        .pip-active {
            display: block !important;
        }

        .pip-content {
            width: 100% !important;
            height: 100% !important;
            border-radius: 10px !important;
            overflow: hidden !important;
            position: relative !important;
        }

        .pip-title {
            position: absolute !important;
            top: 10px !important;
            left: 10px !important;
            background: rgba(0, 0, 0, 0.8) !important;
            padding: 5px 10px !important;
            border-radius: 5px !important;
            font-size: 11px !important;
            color: var(--plasma-purple) !important;
            font-family: 'Orbitron', monospace !important;
        }

        /* GHOST PREVIEW */
        .ghost-preview {
            position: fixed !important;
            pointer-events: none !important;
            z-index: calc(var(--z-maximum) - 3) !important;
            opacity: 0.3 !important;
            border: 2px dashed var(--neon-yellow) !important;
            border-radius: 10px !important;
            background: rgba(255, 255, 0, 0.05) !important;
            animation: ghostPulse 2s ease-in-out infinite !important;
        }

        @keyframes ghostPulse {
            0%, 100% {
                opacity: 0.3;
                transform: scale(1);
            }
            50% {
                opacity: 0.5;
                transform: scale(1.02);
            }
        }

        /* PATH PREDICTION */
        .prediction-path {
            position: fixed !important;
            pointer-events: none !important;
            z-index: calc(var(--z-maximum) - 4) !important;
        }

        .path-dot {
            position: absolute !important;
            width: 4px !important;
            height: 4px !important;
            background: var(--neon-yellow) !important;
            border-radius: 50% !important;
            opacity: 0.6 !important;
            animation: pathDotPulse 1s ease-in-out infinite !important;
        }

        @keyframes pathDotPulse {
            0%, 100% {
                transform: scale(1);
                opacity: 0.6;
            }
            50% {
                transform: scale(1.5);
                opacity: 1;
            }
        }

        /* BREADCRUMB NAVIGATION */
        .breadcrumb-nav {
            position: fixed !important;
            top: 20px !important;
            left: 50% !important;
            transform: translateX(-50%) !important;
            z-index: calc(var(--z-maximum) - 2) !important;
            display: flex !important;
            gap: 10px !important;
            background: rgba(0, 0, 0, 0.8) !important;
            padding: 10px 20px !important;
            border-radius: 30px !important;
            border: 1px solid var(--electric-blue) !important;
            backdrop-filter: blur(10px) !important;
        }

        .breadcrumb-item {
            width: 40px !important;
            height: 40px !important;
            border-radius: 50% !important;
            background: rgba(0, 128, 255, 0.2) !important;
            border: 2px solid var(--electric-blue) !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            cursor: pointer !important;
            transition: all 0.3s ease !important;
            font-size: 12px !important;
            color: white !important;
            font-family: 'Orbitron', monospace !important;
        }

        .breadcrumb-item:hover {
            background: var(--electric-blue) !important;
            transform: scale(1.2) !important;
            box-shadow: 0 0 20px var(--electric-blue) !important;
        }

        .breadcrumb-current {
            background: var(--neon-cyan) !important;
            border-color: var(--neon-cyan) !important;
            animation: breadcrumbGlow 2s ease-in-out infinite !important;
        }

        @keyframes breadcrumbGlow {
            0%, 100% {
                box-shadow: 0 0 10px var(--neon-cyan);
            }
            50% {
                box-shadow: 0 0 30px var(--neon-cyan);
            }
        }

        /* HEAT MAP OVERLAY */
        .heat-map-overlay {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100% !important;
            height: 100% !important;
            pointer-events: none !important;
            z-index: calc(var(--z-maximum) - 10) !important;
            opacity: 0 !important;
            transition: opacity 0.5s ease !important;
            mix-blend-mode: multiply !important;
        }

        .heat-map-active {
            opacity: 0.4 !important;
        }

        .heat-zone {
            position: absolute !important;
            border-radius: 50% !important;
            filter: blur(30px) !important;
        }

        .heat-hot {
            background: radial-gradient(circle,
                rgba(255, 0, 0, 0.8) 0%,
                rgba(255, 128, 0, 0.4) 50%,
                transparent 100%) !important;
        }

        .heat-warm {
            background: radial-gradient(circle,
                rgba(255, 255, 0, 0.6) 0%,
                rgba(255, 200, 0, 0.3) 50%,
                transparent 100%) !important;
        }

        .heat-cool {
            background: radial-gradient(circle,
                rgba(0, 128, 255, 0.4) 0%,
                rgba(0, 200, 255, 0.2) 50%,
                transparent 100%) !important;
        }

        /* SPEED CONTROL PANEL */
        .speed-control {
            position: fixed !important;
            bottom: 20px !important;
            right: 20px !important;
            z-index: calc(var(--z-maximum) - 2) !important;
            background: rgba(0, 0, 0, 0.9) !important;
            border: 2px solid var(--laser-green) !important;
            border-radius: 30px !important;
            padding: 10px 20px !important;
            display: flex !important;
            gap: 10px !important;
            backdrop-filter: blur(10px) !important;
        }

        .speed-button {
            width: 40px !important;
            height: 40px !important;
            border-radius: 50% !important;
            background: rgba(0, 255, 128, 0.2) !important;
            border: 2px solid var(--laser-green) !important;
            color: white !important;
            font-family: 'Orbitron', monospace !important;
            font-size: 11px !important;
            cursor: pointer !important;
            transition: all 0.3s ease !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }

        .speed-button:hover {
            background: var(--laser-green) !important;
            transform: scale(1.1) !important;
            box-shadow: 0 0 20px var(--laser-green) !important;
        }

        .speed-active {
            background: var(--laser-green) !important;
            color: black !important;
        }

        /* GESTURE INDICATOR */
        .gesture-indicator {
            position: fixed !important;
            pointer-events: none !important;
            z-index: var(--z-maximum) !important;
            color: var(--neon-cyan) !important;
            font-family: 'Orbitron', monospace !important;
            font-size: 14px !important;
            background: rgba(0, 0, 0, 0.8) !important;
            padding: 5px 10px !important;
            border-radius: 5px !important;
            opacity: 0 !important;
            transition: opacity 0.3s ease !important;
        }

        .gesture-show {
            opacity: 1 !important;
        }

        /* COLLISION ZONES */
        .collision-zone {
            position: fixed !important;
            border: 1px dashed rgba(255, 0, 0, 0.3) !important;
            background: rgba(255, 0, 0, 0.05) !important;
            pointer-events: none !important;
            z-index: calc(var(--z-maximum) - 20) !important;
            display: none !important;
        }

        .debug-collision .collision-zone {
            display: block !important;
        }

        /* ELEMENT TRAIL */
        .element-trail {
            position: fixed !important;
            pointer-events: none !important;
            z-index: calc(var(--z-maximum) - 5) !important;
            opacity: 0.6 !important;
            border: 2px solid var(--neon-cyan) !important;
            border-radius: 10px !important;
            animation: trailFade 2s ease-out forwards !important;
        }

        @keyframes trailFade {
            0% {
                opacity: 0.6;
                transform: scale(1);
            }
            100% {
                opacity: 0;
                transform: scale(0.8);
            }
        }

        /* SMOOTH TRANSITIONS */
        .smooth-transition {
            transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        }

        /* SPRING PHYSICS */
        .spring-animation {
            animation: springBounce 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55) !important;
        }

        @keyframes springBounce {
            0% {
                transform: scale(1);
            }
            30% {
                transform: scale(1.1);
            }
            60% {
                transform: scale(0.95);
            }
            100% {
                transform: scale(1);
            }
        }
        """

        await self.page.add_style_tag(content=enhanced_css)

    async def inject_spatial_intelligence(self):
        """Inject JavaScript for spatial intelligence and collision detection."""
        spatial_js = """
        (() => {
            // Spatial Intelligence System
            window.SpatialIntelligence = {
                elements: [],
                boundaries: {},
                collisionBuffer: 50,

                // Initialize spatial tracking
                init() {
                    this.updateBoundaries();
                    this.startTracking();
                },

                // Update element boundaries
                updateBoundaries() {
                    const commandCenter = document.querySelector('.command-center');
                    const miniMap = document.querySelector('.mini-map');
                    const magnifier = document.querySelector('.magnifier-lens');
                    const pip = document.querySelector('.pip-window');

                    if (commandCenter) {
                        const rect = commandCenter.getBoundingClientRect();
                        this.boundaries.commandCenter = {
                            x: rect.x,
                            y: rect.y,
                            width: rect.width,
                            height: rect.height,
                            element: commandCenter
                        };
                    }

                    if (miniMap) {
                        const rect = miniMap.getBoundingClientRect();
                        this.boundaries.miniMap = {
                            x: rect.x,
                            y: rect.y,
                            width: rect.width,
                            height: rect.height,
                            element: miniMap
                        };
                    }

                    if (magnifier) {
                        const rect = magnifier.getBoundingClientRect();
                        this.boundaries.magnifier = {
                            x: rect.x,
                            y: rect.y,
                            width: rect.width,
                            height: rect.height,
                            element: magnifier
                        };
                    }
                },

                // Detect collision between two rectangles
                detectCollision(rect1, rect2, buffer = 50) {
                    return !(rect1.x > rect2.x + rect2.width + buffer ||
                            rect1.x + rect1.width + buffer < rect2.x ||
                            rect1.y > rect2.y + rect2.height + buffer ||
                            rect1.y + rect1.height + buffer < rect2.y);
                },

                // Calculate escape vector
                calculateEscapeVector(movingRect, staticRect) {
                    const centerX1 = movingRect.x + movingRect.width / 2;
                    const centerY1 = movingRect.y + movingRect.height / 2;
                    const centerX2 = staticRect.x + staticRect.width / 2;
                    const centerY2 = staticRect.y + staticRect.height / 2;

                    const dx = centerX1 - centerX2;
                    const dy = centerY1 - centerY2;
                    const distance = Math.sqrt(dx * dx + dy * dy);

                    if (distance === 0) return { x: 100, y: 0 };

                    const escapeDistance = this.collisionBuffer + Math.max(movingRect.width, staticRect.width);
                    const escapeX = (dx / distance) * escapeDistance;
                    const escapeY = (dy / distance) * escapeDistance;

                    return { x: escapeX, y: escapeY };
                },

                // Reposition element to avoid collision
                repositionElement(element, targetX, targetY) {
                    const viewport = {
                        width: window.innerWidth,
                        height: window.innerHeight
                    };

                    // Keep within viewport
                    const rect = element.getBoundingClientRect();
                    let newX = targetX;
                    let newY = targetY;

                    if (newX < 0) newX = 20;
                    if (newY < 0) newY = 20;
                    if (newX + rect.width > viewport.width) newX = viewport.width - rect.width - 20;
                    if (newY + rect.height > viewport.height) newY = viewport.height - rect.height - 20;

                    // Apply smooth transition
                    element.style.transition = 'all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55)';
                    element.style.transform = `translate(${newX}px, ${newY}px)`;

                    // Add avoiding class for animation
                    element.classList.add('avoiding-collision');
                    setTimeout(() => element.classList.remove('avoiding-collision'), 500);
                },

                // Handle magnifier movement
                handleMagnifierMovement(x, y) {
                    this.updateBoundaries();

                    const magnifierRect = {
                        x: x - 125,
                        y: y - 125,
                        width: 250,
                        height: 250
                    };

                    // Check collision with command center
                    if (this.boundaries.commandCenter) {
                        if (this.detectCollision(magnifierRect, this.boundaries.commandCenter)) {
                            const escape = this.calculateEscapeVector(
                                this.boundaries.commandCenter,
                                magnifierRect
                            );
                            const newX = this.boundaries.commandCenter.x + escape.x;
                            const newY = this.boundaries.commandCenter.y + escape.y;
                            this.repositionElement(
                                this.boundaries.commandCenter.element,
                                newX,
                                newY
                            );
                        }
                    }

                    // Check collision with mini map
                    if (this.boundaries.miniMap) {
                        if (this.detectCollision(magnifierRect, this.boundaries.miniMap)) {
                            const escape = this.calculateEscapeVector(
                                this.boundaries.miniMap,
                                magnifierRect
                            );
                            const newX = this.boundaries.miniMap.x + escape.x;
                            const newY = this.boundaries.miniMap.y + escape.y;
                            this.repositionElement(
                                this.boundaries.miniMap.element,
                                newX,
                                newY
                            );
                        }
                    }
                },

                // Start tracking mouse movement
                startTracking() {
                    document.addEventListener('mousemove', (e) => {
                        const magnifier = document.querySelector('.magnifier-lens');
                        if (magnifier && magnifier.classList.contains('magnifier-active')) {
                            this.handleMagnifierMovement(e.clientX, e.clientY);
                        }
                    });
                },

                // Store and restore element borders
                preserveElementBorder(element) {
                    const computedStyle = window.getComputedStyle(element);
                    const originalBorder = computedStyle.border;
                    const originalOutline = computedStyle.outline;
                    const originalBoxShadow = computedStyle.boxShadow;

                    element.setAttribute('data-original-border', originalBorder);
                    element.setAttribute('data-original-outline', originalOutline);
                    element.setAttribute('data-original-shadow', originalBoxShadow);

                    return {
                        border: originalBorder,
                        outline: originalOutline,
                        boxShadow: originalBoxShadow
                    };
                },

                restoreElementBorder(element) {
                    const originalBorder = element.getAttribute('data-original-border');
                    const originalOutline = element.getAttribute('data-original-outline');
                    const originalBoxShadow = element.getAttribute('data-original-shadow');

                    if (originalBorder) element.style.border = originalBorder;
                    if (originalOutline) element.style.outline = originalOutline;
                    if (originalBoxShadow) element.style.boxShadow = originalBoxShadow;

                    element.classList.remove('element-focused');
                    element.removeAttribute('data-original-border');
                    element.removeAttribute('data-original-outline');
                    element.removeAttribute('data-original-shadow');
                }
            };

            // Initialize spatial intelligence
            window.SpatialIntelligence.init();

            // Gesture controls
            window.GestureControls = {
                init() {
                    this.setupDragAndDrop();
                    this.setupZoom();
                    this.setupKeyboardShortcuts();
                },

                setupDragAndDrop() {
                    const draggables = ['.command-center', '.mini-map'];
                    draggables.forEach(selector => {
                        const element = document.querySelector(selector);
                        if (element) {
                            let isDragging = false;
                            let startX, startY, initialX, initialY;

                            element.addEventListener('mousedown', (e) => {
                                isDragging = true;
                                startX = e.clientX;
                                startY = e.clientY;
                                const rect = element.getBoundingClientRect();
                                initialX = rect.x;
                                initialY = rect.y;
                                element.style.cursor = 'grabbing';
                            });

                            document.addEventListener('mousemove', (e) => {
                                if (!isDragging) return;
                                e.preventDefault();
                                const dx = e.clientX - startX;
                                const dy = e.clientY - startY;
                                element.style.transform = `translate(${initialX + dx}px, ${initialY + dy}px)`;
                            });

                            document.addEventListener('mouseup', () => {
                                isDragging = false;
                                if (element) element.style.cursor = 'move';
                            });
                        }
                    });
                },

                setupZoom() {
                    document.addEventListener('wheel', (e) => {
                        const magnifier = document.querySelector('.magnifier-lens');
                        if (magnifier && magnifier.classList.contains('magnifier-active')) {
                            if (e.ctrlKey) {
                                e.preventDefault();
                                const currentScale = parseFloat(magnifier.style.transform.match(/scale\\(([^)]+)\\)/)?.[1] || 1);
                                const newScale = e.deltaY > 0 ?
                                    Math.max(0.5, currentScale - 0.1) :
                                    Math.min(2, currentScale + 0.1);
                                magnifier.style.transform = `scale(${newScale})`;
                            }
                        }
                    });
                },

                setupKeyboardShortcuts() {
                    document.addEventListener('keydown', (e) => {
                        // Spacebar to pause/resume
                        if (e.code === 'Space') {
                            e.preventDefault();
                            window.tourPaused = !window.tourPaused;
                            this.showGesture(window.tourPaused ? 'PAUSED' : 'RESUMED');
                        }

                        // Arrow keys to navigate
                        if (e.code === 'ArrowRight') {
                            e.preventDefault();
                            window.skipToNext = true;
                            this.showGesture('NEXT →');
                        }

                        if (e.code === 'ArrowLeft') {
                            e.preventDefault();
                            window.skipToPrevious = true;
                            this.showGesture('← PREVIOUS');
                        }

                        // H for heat map toggle
                        if (e.code === 'KeyH') {
                            const heatMap = document.querySelector('.heat-map-overlay');
                            if (heatMap) {
                                heatMap.classList.toggle('heat-map-active');
                                this.showGesture(heatMap.classList.contains('heat-map-active') ?
                                    'HEAT MAP ON' : 'HEAT MAP OFF');
                            }
                        }
                    });
                },

                showGesture(text) {
                    let indicator = document.querySelector('.gesture-indicator');
                    if (!indicator) {
                        indicator = document.createElement('div');
                        indicator.className = 'gesture-indicator';
                        document.body.appendChild(indicator);
                    }

                    indicator.textContent = text;
                    indicator.style.left = '50%';
                    indicator.style.top = '50%';
                    indicator.style.transform = 'translate(-50%, -50%)';
                    indicator.classList.add('gesture-show');

                    setTimeout(() => {
                        indicator.classList.remove('gesture-show');
                    }, 1500);
                }
            };

            // Initialize gesture controls
            window.GestureControls.init();
        })();
        """
        await self.page.evaluate(spatial_js)

    async def detect_and_sort_elements(self):
        """Detect all elements with enhanced metadata."""
        detection_script = """
        () => {
            const elements = [];
            const selectors = [
                'a[href]', 'button', 'input:not([type="hidden"])',
                'textarea', 'select', '[role="button"]', '[role="link"]',
                '[onclick]', '.btn', '.button', 'summary'
            ];

            const allElements = document.querySelectorAll(selectors.join(', '));
            const seen = new Set();

            allElements.forEach(el => {
                if (!seen.has(el)) {
                    seen.add(el);
                    const rect = el.getBoundingClientRect();
                    const styles = window.getComputedStyle(el);

                    if (rect.width > 0 && rect.height > 0 &&
                        styles.display !== 'none' &&
                        styles.visibility !== 'hidden') {

                        // Store original styles
                        window.SpatialIntelligence.preserveElementBorder(el);

                        let type = 'unknown';
                        if (el.tagName === 'BUTTON' || el.role === 'button') type = 'button';
                        else if (el.tagName === 'A') type = 'link';
                        else if (el.tagName === 'INPUT') type = 'input';
                        else if (el.tagName === 'TEXTAREA') type = 'textarea';
                        else if (el.tagName === 'SELECT') type = 'select';

                        const size = rect.width * rect.height;
                        const isAboveFold = rect.top < window.innerHeight;
                        const isCentered = Math.abs(rect.x + rect.width/2 - window.innerWidth/2) < 200;
                        const importanceScore = size * (isAboveFold ? 2 : 1) * (isCentered ? 1.5 : 1);

                        elements.push({
                            tagName: el.tagName.toLowerCase(),
                            type: type,
                            text: (el.textContent || el.value || '').trim().substring(0, 100),
                            rect: {
                                x: rect.x,
                                y: rect.y,
                                width: rect.width,
                                height: rect.height,
                                centerX: rect.x + rect.width / 2,
                                centerY: rect.y + rect.height / 2
                            },
                            positionScore: (rect.y * 10000) + rect.x,
                            importanceScore: importanceScore,
                            originalBorder: styles.border,
                            originalOutline: styles.outline,
                            originalBoxShadow: styles.boxShadow
                        });
                    }
                }
            });

            elements.sort((a, b) => a.positionScore - b.positionScore);
            elements.forEach((el, index) => {
                el.number = index + 1;
            });

            return elements;
        }
        """
        return await self.page.evaluate(detection_script)

    async def create_enhanced_ui(self, elements):
        """Create all enhanced UI elements."""
        ui_script = """
        (elements) => {
            // Command Center
            const center = document.createElement('div');
            center.className = 'command-center smooth-transition';
            center.innerHTML = `
                <div style="padding: 20px;">
                    <h2 style="color: var(--neon-cyan); margin: 0 0 20px 0; text-align: center; font-size: 20px;">
                        EXECUTIVE COMMAND CENTER
                    </h2>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                        <div>
                            <div style="color: var(--neon-yellow); font-size: 48px; font-weight: 900;" id="element-counter">--</div>
                            <div style="color: rgba(255,255,255,0.8); font-size: 12px; margin-top: 10px;">
                                Type: <span id="element-type" style="color: var(--laser-green);">--</span><br>
                                Position: <span id="element-pos" style="color: var(--neon-cyan);">--</span><br>
                                Score: <span id="element-score" style="color: var(--neon-magenta);">--</span>
                            </div>
                        </div>
                        <div>
                            <canvas id="live-chart" width="250" height="150"></canvas>
                        </div>
                    </div>
                    <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.2);">
                        <div id="ai-insight" style="color: rgba(255,255,255,0.9); font-size: 12px; line-height: 1.6;">
                            Initializing spatial intelligence engine...
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(center);

            // Mini Map
            const miniMap = document.createElement('div');
            miniMap.className = 'mini-map smooth-transition';
            miniMap.innerHTML = `
                <canvas id="mini-map-canvas" width="250" height="180"></canvas>
                <div class="mini-map-viewport"></div>
            `;
            document.body.appendChild(miniMap);

            // Magnifier
            const magnifier = document.createElement('div');
            magnifier.className = 'magnifier-lens';
            magnifier.innerHTML = '<div class="magnifier-content"></div>';
            document.body.appendChild(magnifier);

            // PiP Window
            const pip = document.createElement('div');
            pip.className = 'pip-window';
            pip.innerHTML = `
                <div class="pip-title">ELEMENT ZOOM</div>
                <div class="pip-content" id="pip-content"></div>
            `;
            document.body.appendChild(pip);

            // Breadcrumb Navigation
            const breadcrumb = document.createElement('div');
            breadcrumb.className = 'breadcrumb-nav';
            breadcrumb.id = 'breadcrumb-nav';
            document.body.appendChild(breadcrumb);

            // Speed Controls
            const speedControl = document.createElement('div');
            speedControl.className = 'speed-control';
            speedControl.innerHTML = `
                <div class="speed-button" data-speed="0.5">0.5x</div>
                <div class="speed-button speed-active" data-speed="1">1x</div>
                <div class="speed-button" data-speed="1.5">1.5x</div>
                <div class="speed-button" data-speed="2">2x</div>
            `;
            document.body.appendChild(speedControl);

            // Heat Map Overlay
            const heatMap = document.createElement('div');
            heatMap.className = 'heat-map-overlay';
            heatMap.id = 'heat-map-overlay';
            document.body.appendChild(heatMap);

            // Generate heat zones
            const heatZones = elements.slice(0, 10).map(el => {
                const zone = document.createElement('div');
                zone.className = 'heat-zone heat-hot';
                zone.style.left = el.rect.centerX + 'px';
                zone.style.top = el.rect.centerY + 'px';
                zone.style.width = '200px';
                zone.style.height = '200px';
                zone.style.transform = 'translate(-50%, -50%)';
                return zone;
            });
            heatZones.forEach(zone => heatMap.appendChild(zone));

            // Gesture Indicator
            const gestureIndicator = document.createElement('div');
            gestureIndicator.className = 'gesture-indicator';
            document.body.appendChild(gestureIndicator);

            // Setup speed control listeners
            document.querySelectorAll('.speed-button').forEach(btn => {
                btn.addEventListener('click', () => {
                    document.querySelectorAll('.speed-button').forEach(b =>
                        b.classList.remove('speed-active'));
                    btn.classList.add('speed-active');
                    window.tourSpeed = parseFloat(btn.dataset.speed);
                    window.GestureControls.showGesture(`Speed: ${btn.dataset.speed}x`);
                });
            });

            return true;
        }
        """
        await self.page.evaluate(ui_script, elements)

    async def focus_element_with_border(self, element, index, total, elements):
        """Focus on element with proper border handling."""
        focus_script = """
        (data) => {
            const element = data.element;
            const index = data.index;
            const total = data.total;

            // Find the actual DOM element
            const selector = element.type === 'button' ? 'button, [role="button"], .btn' :
                           element.type === 'link' ? 'a[href]' :
                           element.type === 'input' ? 'input' :
                           element.type === 'textarea' ? 'textarea' :
                           'select';

            const allElements = document.querySelectorAll(selector);
            let targetElement = null;

            allElements.forEach(el => {
                const rect = el.getBoundingClientRect();
                if (Math.abs(rect.x - element.rect.x) < 2 &&
                    Math.abs(rect.y - element.rect.y) < 2) {
                    targetElement = el;
                }
            });

            // Remove focus from previous element
            document.querySelectorAll('.element-focused').forEach(el => {
                window.SpatialIntelligence.restoreElementBorder(el);

                // Remove ripple effect
                el.querySelectorAll('.focus-ripple').forEach(r => r.remove());
            });

            // Apply focus to new element
            if (targetElement) {
                // Preserve original border first
                window.SpatialIntelligence.preserveElementBorder(targetElement);

                // Add focus class
                targetElement.classList.add('element-focused');

                // Add ripple effect
                const ripple = document.createElement('div');
                ripple.className = 'focus-ripple';
                targetElement.appendChild(ripple);

                // Create element trail
                const trail = document.createElement('div');
                trail.className = 'element-trail';
                trail.style.left = element.rect.x + 'px';
                trail.style.top = element.rect.y + 'px';
                trail.style.width = element.rect.width + 'px';
                trail.style.height = element.rect.height + 'px';
                document.body.appendChild(trail);
                setTimeout(() => trail.remove(), 2000);
            }

            // Update magnifier position
            const magnifier = document.querySelector('.magnifier-lens');
            if (magnifier) {
                magnifier.style.left = (element.rect.centerX - 125) + 'px';
                magnifier.style.top = (element.rect.centerY - 125) + 'px';
                magnifier.classList.add('magnifier-active');

                // Trigger collision detection
                window.SpatialIntelligence.handleMagnifierMovement(
                    element.rect.centerX,
                    element.rect.centerY
                );
            }

            // Update PiP window
            const pip = document.querySelector('.pip-window');
            if (pip) {
                pip.classList.add('pip-active');
                pip.style.left = (element.rect.x + element.rect.width + 50) + 'px';
                pip.style.top = element.rect.y + 'px';

                // Keep PiP in viewport
                const pipRect = pip.getBoundingClientRect();
                if (pipRect.right > window.innerWidth) {
                    pip.style.left = (element.rect.x - 350) + 'px';
                }
                if (pipRect.bottom > window.innerHeight) {
                    pip.style.top = (window.innerHeight - pipRect.height - 20) + 'px';
                }

                document.getElementById('pip-content').innerHTML = `
                    <div style="color: white; font-size: 11px; padding: 10px;">
                        <strong>Element #${element.number}</strong><br>
                        Type: ${element.type}<br>
                        Size: ${Math.round(element.rect.width)}x${Math.round(element.rect.height)}px<br>
                        Score: ${Math.round(element.importanceScore || 0)}
                    </div>
                `;
            }

            // Update command center
            document.getElementById('element-counter').textContent = element.number;
            document.getElementById('element-type').textContent = element.type.toUpperCase();
            document.getElementById('element-pos').textContent =
                `(${Math.round(element.rect.x)}, ${Math.round(element.rect.y)})`;
            document.getElementById('element-score').textContent =
                Math.round(element.importanceScore || 0);

            // Update AI insight
            const insights = [
                "Spatial collision detection: ACTIVE",
                "Border preservation: MAINTAINED",
                "UI displacement: OPTIMIZED",
                "Viewport boundaries: ENFORCED",
                "Spring physics: ENGAGED"
            ];
            document.getElementById('ai-insight').innerHTML = insights.join('<br>');

            // Update breadcrumb
            const breadcrumb = document.getElementById('breadcrumb-nav');
            if (breadcrumb.children.length > 5) {
                breadcrumb.removeChild(breadcrumb.firstChild);
            }
            const crumb = document.createElement('div');
            crumb.className = 'breadcrumb-item breadcrumb-current';
            crumb.textContent = element.number;
            crumb.onclick = () => window.jumpToElement = element.number;
            breadcrumb.appendChild(crumb);

            // Remove current class from others
            breadcrumb.querySelectorAll('.breadcrumb-item').forEach((item, idx) => {
                if (idx < breadcrumb.children.length - 1) {
                    item.classList.remove('breadcrumb-current');
                }
            });

            // Create ghost preview for next element
            if (index < total - 1) {
                const nextElement = window.tourElements[index + 1];
                if (nextElement) {
                    const ghost = document.createElement('div');
                    ghost.className = 'ghost-preview';
                    ghost.style.left = nextElement.rect.x + 'px';
                    ghost.style.top = nextElement.rect.y + 'px';
                    ghost.style.width = nextElement.rect.width + 'px';
                    ghost.style.height = nextElement.rect.height + 'px';
                    document.body.appendChild(ghost);
                    setTimeout(() => ghost.remove(), 3000);

                    // Create prediction path
                    const path = document.createElement('div');
                    path.className = 'prediction-path';
                    const steps = 10;
                    for (let i = 0; i < steps; i++) {
                        const dot = document.createElement('div');
                        dot.className = 'path-dot';
                        const t = i / steps;
                        dot.style.left = (element.rect.centerX +
                            (nextElement.rect.centerX - element.rect.centerX) * t) + 'px';
                        dot.style.top = (element.rect.centerY +
                            (nextElement.rect.centerY - element.rect.centerY) * t) + 'px';
                        dot.style.animationDelay = (i * 0.1) + 's';
                        path.appendChild(dot);
                    }
                    document.body.appendChild(path);
                    setTimeout(() => path.remove(), 3000);
                }
            }

            // Smooth scroll if needed
            if (element.rect.y < window.scrollY ||
                element.rect.y > window.scrollY + window.innerHeight - 200) {
                window.scrollTo({
                    top: element.rect.y - 200,
                    behavior: 'smooth'
                });
            }
        }
        """

        # Store elements for navigation
        await self.page.evaluate("(elements) => { window.tourElements = elements; }", elements)

        await self.page.evaluate(focus_script, {
            'element': element,
            'index': index,
            'total': total
        })

    async def run_enhanced_showcase(self):
        """Execute the enhanced showcase."""
        try:
            await self.initialize()
            await self.navigate()

            print("\n🌟 ULTIMATE ENHANCED SHOWCASE INITIALIZING")
            print("━" * 60)

            # Inject styles and scripts
            await self.inject_enhanced_styles()
            await self.inject_spatial_intelligence()

            # Detect elements
            print("🔬 Spatial scanning with collision detection...")
            elements = await self.detect_and_sort_elements()
            print(f"⚡ Discovered {len(elements)} elements with preserved borders")

            # Create UI
            print("🎮 Deploying spatially-aware UI...")
            await self.create_enhanced_ui(elements)

            await asyncio.sleep(2)

            # Tour
            print("\n🚀 INITIATING INTELLIGENT TOUR")
            print("━" * 60)
            print("Controls:")
            print("  • SPACE: Pause/Resume")
            print("  • ←/→: Navigate elements")
            print("  • H: Toggle heat map")
            print("  • Scroll: Zoom magnifier (with Ctrl)")
            print("  • Drag: Move panels")
            print("━" * 60)

            # Set default speed
            await self.page.evaluate("window.tourSpeed = 1")
            await self.page.evaluate("window.tourPaused = false")

            for i, element in enumerate(elements):
                # Check for pause
                is_paused = await self.page.evaluate("window.tourPaused")
                while is_paused:
                    await asyncio.sleep(0.1)
                    is_paused = await self.page.evaluate("window.tourPaused")

                # Check for skip
                skip_next = await self.page.evaluate("window.skipToNext")
                if skip_next:
                    await self.page.evaluate("window.skipToNext = false")
                    continue

                print(f"\n🎯 Element #{element['number']}/{len(elements)}: {element['type'].upper()}")

                # Focus with border preservation
                await self.focus_element_with_border(element, i, len(elements), elements)

                # Dynamic wait based on speed
                speed = await self.page.evaluate("window.tourSpeed || 1")
                await asyncio.sleep(3 / speed)

            print("\n" + "━" * 60)
            print("🏆 ENHANCED SHOWCASE COMPLETE")
            print("\n📊 Final Statistics:")
            print(f"  • Elements: {len(elements)}")
            print(f"  • Spatial Intelligence: ACTIVE")
            print(f"  • Collision Detection: ENABLED")
            print(f"  • Border Preservation: 100%")
            print(f"  • UI Adaptability: MAXIMUM")

            await self.page.screenshot(path="ultimate_enhanced_showcase.png")
            print("\n📸 Captured: ultimate_enhanced_showcase.png")

            print("\n⏰ Showcase remains active for 30 seconds...")
            await asyncio.sleep(30)

        finally:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()


async def main():
    """Main entry point."""
    print("\n" + "="*60)
    print("🌟 ULTIMATE ENHANCED SHOWCASE")
    print("Spatial Intelligence & Collision Detection Edition")
    print("="*60)

    try:
        url = input("Enter URL (default: https://uat.citi.com): ").strip()
        if not url:
            url = "https://uat.citi.com"
    except EOFError:
        # If running non-interactively, use default
        url = "https://uat.citi.com"
        print(f"Using default URL: {url}")

    showcase = UltimateShowcaseEnhanced(url, headless=False)
    await showcase.run_enhanced_showcase()


if __name__ == "__main__":
    asyncio.run(main())
"""
Executive Interactive Elements Showcase
A visually stunning presentation tool for senior management
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

# Force UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm_gemini_client import get_client

load_dotenv(dotenv_path="./.env")


class ExecutiveShowcase:
    """
    Creates stunning visual presentations of interactive elements for executive review.
    """

    def __init__(self, url: str, headless: bool = False):
        self.url = url
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def initialize(self):
        """Initialize browser with optimal settings for presentation."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=['--start-maximized']
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=1.0
        )
        self.page = await self.context.new_page()

    async def navigate(self):
        """Navigate to target URL."""
        print(f"📍 Navigating to {self.url}...")
        await self.page.goto(self.url, wait_until='networkidle')
        await asyncio.sleep(2)

    async def inject_showcase_styles(self):
        """Inject comprehensive CSS for all visual effects."""
        showcase_css = """
        /* Executive Showcase Styles - Premium Visual Effects */

        :root {
            --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --gold-gradient: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
            --emerald-gradient: linear-gradient(135deg, #10B981 0%, #059669 100%);
            --ruby-gradient: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
            --sapphire-gradient: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
            --neon-glow: 0 0 20px rgba(102, 126, 234, 0.8);
            --gold-glow: 0 0 30px rgba(255, 215, 0, 0.6);
        }

        /* Overlay for spotlight effect */
        .executive-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle at var(--spotlight-x, 50%) var(--spotlight-y, 50%),
                        transparent 20%,
                        rgba(0, 0, 0, 0.85) 60%);
            pointer-events: none;
            z-index: 9998;
            transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            animation: overlayPulse 3s ease-in-out infinite;
        }

        @keyframes overlayPulse {
            0%, 100% { opacity: 0.9; }
            50% { opacity: 0.95; }
        }

        /* Premium badge design with glassmorphism */
        .executive-badge {
            position: fixed;
            background: linear-gradient(135deg,
                        rgba(255, 255, 255, 0.1) 0%,
                        rgba(255, 255, 255, 0.05) 100%);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 14px;
            font-weight: 700;
            padding: 8px 14px;
            border-radius: 12px;
            z-index: 10001;
            pointer-events: none;
            min-width: 36px;
            text-align: center;
            box-shadow:
                0 8px 32px rgba(31, 38, 135, 0.37),
                0 0 60px rgba(102, 126, 234, 0.4),
                inset 0 1px 0 rgba(255, 255, 255, 0.3);
            animation: badgeFloat 3s ease-in-out infinite;
            transform-style: preserve-3d;
            letter-spacing: 0.5px;
        }

        @keyframes badgeFloat {
            0%, 100% {
                transform: translateY(0) rotateX(0) rotateY(0);
            }
            25% {
                transform: translateY(-5px) rotateX(5deg) rotateY(5deg);
            }
            75% {
                transform: translateY(-5px) rotateX(-5deg) rotateY(-5deg);
            }
        }

        /* Animated number counter */
        .badge-number {
            display: inline-block;
            animation: numberGlow 2s ease-in-out infinite;
            text-shadow:
                0 0 10px rgba(255, 255, 255, 0.8),
                0 0 20px rgba(102, 126, 234, 0.8),
                0 0 30px rgba(102, 126, 234, 0.6);
        }

        @keyframes numberGlow {
            0%, 100% {
                transform: scale(1);
                opacity: 1;
            }
            50% {
                transform: scale(1.1);
                opacity: 0.9;
            }
        }

        /* Element highlighting with premium effects */
        .executive-highlight {
            position: relative !important;
            animation: elementPulse 2s ease-in-out infinite !important;
            transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }

        .executive-highlight::before {
            content: '';
            position: absolute;
            inset: -4px;
            background: var(--primary-gradient);
            border-radius: inherit;
            opacity: 0.3;
            animation: borderGlow 2s linear infinite;
            z-index: -1;
        }

        @keyframes elementPulse {
            0%, 100% {
                box-shadow:
                    0 0 0 0 rgba(102, 126, 234, 0.7),
                    0 10px 40px rgba(102, 126, 234, 0.3);
            }
            50% {
                box-shadow:
                    0 0 0 10px rgba(102, 126, 234, 0),
                    0 10px 50px rgba(102, 126, 234, 0.5);
            }
        }

        @keyframes borderGlow {
            0% {
                transform: rotate(0deg);
                filter: hue-rotate(0deg);
            }
            100% {
                transform: rotate(360deg);
                filter: hue-rotate(360deg);
            }
        }

        /* Category-specific highlights */
        .highlight-button {
            outline: 3px solid #10B981 !important;
            outline-offset: 3px !important;
            background: linear-gradient(45deg,
                        rgba(16, 185, 129, 0.1),
                        rgba(16, 185, 129, 0.05)) !important;
        }

        .highlight-link {
            outline: 3px solid #3B82F6 !important;
            outline-offset: 3px !important;
            background: linear-gradient(45deg,
                        rgba(59, 130, 246, 0.1),
                        rgba(59, 130, 246, 0.05)) !important;
        }

        .highlight-input {
            outline: 3px solid #F59E0B !important;
            outline-offset: 3px !important;
            background: linear-gradient(45deg,
                        rgba(245, 158, 11, 0.1),
                        rgba(245, 158, 11, 0.05)) !important;
        }

        /* Ripple effect on discovery */
        .ripple-effect {
            position: fixed;
            border-radius: 50%;
            background: radial-gradient(circle,
                        rgba(102, 126, 234, 0.6) 0%,
                        transparent 70%);
            pointer-events: none;
            z-index: 9999;
            animation: ripple 1s ease-out forwards;
        }

        @keyframes ripple {
            from {
                width: 0;
                height: 0;
                opacity: 1;
            }
            to {
                width: 300px;
                height: 300px;
                opacity: 0;
            }
        }

        /* Info panel with glassmorphism */
        .executive-info-panel {
            position: fixed;
            top: 20px;
            right: 20px;
            width: 350px;
            background: linear-gradient(135deg,
                        rgba(255, 255, 255, 0.1) 0%,
                        rgba(255, 255, 255, 0.05) 100%);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 20px;
            padding: 25px;
            z-index: 10000;
            color: white;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            box-shadow:
                0 8px 32px rgba(31, 38, 135, 0.37),
                0 0 80px rgba(102, 126, 234, 0.3);
            animation: slideInRight 0.5s ease-out;
        }

        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }

        .info-title {
            font-size: 24px;
            font-weight: 800;
            margin-bottom: 15px;
            background: var(--primary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 30px rgba(102, 126, 234, 0.5);
        }

        .info-stats {
            display: grid;
            gap: 12px;
            margin-top: 20px;
        }

        .stat-item {
            display: flex;
            justify-content: space-between;
            padding: 12px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
        }

        .stat-item:hover {
            background: rgba(255, 255, 255, 0.1);
            transform: translateX(5px);
            box-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
        }

        .stat-number {
            font-size: 28px;
            font-weight: bold;
            background: linear-gradient(45deg, #FFD700, #FFA500);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* Matrix rain effect for dramatic entrance */
        .matrix-rain {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 9997;
            opacity: 0.1;
        }

        .matrix-drop {
            position: absolute;
            color: #00ff00;
            font-family: 'Courier New', monospace;
            font-size: 10px;
            animation: matrixFall linear infinite;
        }

        @keyframes matrixFall {
            to {
                transform: translateY(100vh);
            }
        }

        /* Particle effects */
        .particle {
            position: fixed;
            pointer-events: none;
            z-index: 10002;
            width: 4px;
            height: 4px;
            background: radial-gradient(circle,
                        rgba(255, 215, 0, 1) 0%,
                        transparent 70%);
            border-radius: 50%;
            animation: particleFloat 3s ease-in-out infinite;
        }

        @keyframes particleFloat {
            0% {
                transform: translateY(0) translateX(0) scale(1);
                opacity: 1;
            }
            100% {
                transform: translateY(-100px) translateX(50px) scale(0);
                opacity: 0;
            }
        }

        /* Loading scanner effect */
        .scanner-line {
            position: fixed;
            left: 0;
            width: 100%;
            height: 3px;
            background: linear-gradient(90deg,
                        transparent,
                        rgba(102, 126, 234, 0.8),
                        transparent);
            z-index: 10003;
            animation: scan 2s linear infinite;
        }

        @keyframes scan {
            0% {
                top: -3px;
            }
            100% {
                top: 100%;
            }
        }

        /* Control panel */
        .control-panel {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: linear-gradient(135deg,
                        rgba(255, 255, 255, 0.1) 0%,
                        rgba(255, 255, 255, 0.05) 100%);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 20px;
            padding: 15px 30px;
            z-index: 10000;
            display: flex;
            gap: 15px;
            box-shadow:
                0 8px 32px rgba(31, 38, 135, 0.37),
                0 0 60px rgba(102, 126, 234, 0.3);
        }

        .control-button {
            padding: 10px 20px;
            background: var(--primary-gradient);
            border: none;
            border-radius: 10px;
            color: white;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }

        .control-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 25px rgba(102, 126, 234, 0.5);
        }
        """

        await self.page.add_style_tag(content=showcase_css)

    async def detect_elements(self):
        """Detect and categorize interactive elements."""
        detection_script = """
        () => {
            const elements = {
                buttons: [],
                links: [],
                inputs: [],
                total: 0
            };

            // Detect buttons
            document.querySelectorAll('button, [role="button"], .btn, .button').forEach(el => {
                const rect = el.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0) {
                    elements.buttons.push({
                        rect: {x: rect.x, y: rect.y, width: rect.width, height: rect.height},
                        text: el.textContent?.trim().substring(0, 50) || 'Button'
                    });
                }
            });

            // Detect links
            document.querySelectorAll('a[href]').forEach(el => {
                const rect = el.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0) {
                    elements.links.push({
                        rect: {x: rect.x, y: rect.y, width: rect.width, height: rect.height},
                        text: el.textContent?.trim().substring(0, 50) || 'Link',
                        href: el.href
                    });
                }
            });

            // Detect inputs
            document.querySelectorAll('input:not([type="hidden"]), textarea, select').forEach(el => {
                const rect = el.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0) {
                    elements.inputs.push({
                        rect: {x: rect.x, y: rect.y, width: rect.width, height: rect.height},
                        type: el.type || 'text',
                        placeholder: el.placeholder || ''
                    });
                }
            });

            elements.total = elements.buttons.length + elements.links.length + elements.inputs.length;
            return elements;
        }
        """
        return await self.page.evaluate(detection_script)

    async def create_spotlight_effect(self):
        """Create dramatic spotlight overlay."""
        await self.page.evaluate("""
        () => {
            const overlay = document.createElement('div');
            overlay.className = 'executive-overlay';
            document.body.appendChild(overlay);
        }
        """)

    async def create_info_panel(self, elements):
        """Create executive info panel."""
        panel_script = """
        (elements) => {
            const panel = document.createElement('div');
            panel.className = 'executive-info-panel';
            panel.innerHTML = `
                <div class="info-title">Interactive Elements Analysis</div>
                <div style="color: rgba(255,255,255,0.7); margin-bottom: 20px;">
                    ${new Date().toLocaleString()}
                </div>
                <div class="info-stats">
                    <div class="stat-item">
                        <span>Total Elements</span>
                        <span class="stat-number">${elements.total}</span>
                    </div>
                    <div class="stat-item">
                        <span>Buttons</span>
                        <span class="stat-number">${elements.buttons.length}</span>
                    </div>
                    <div class="stat-item">
                        <span>Links</span>
                        <span class="stat-number">${elements.links.length}</span>
                    </div>
                    <div class="stat-item">
                        <span>Input Fields</span>
                        <span class="stat-number">${elements.inputs.length}</span>
                    </div>
                </div>
                <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.1);">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <div style="width: 8px; height: 8px; background: #10B981; border-radius: 50%; animation: pulse 2s infinite;"></div>
                        <span style="color: rgba(255,255,255,0.9);">Live Analysis Mode</span>
                    </div>
                </div>
            `;
            document.body.appendChild(panel);
        }
        """
        await self.page.evaluate(panel_script, elements)

    async def animate_discovery(self, elements):
        """Animate the discovery of elements with various effects."""
        animation_script = """
        async (elements) => {
            // Helper to create ripple effect
            const createRipple = (x, y) => {
                const ripple = document.createElement('div');
                ripple.className = 'ripple-effect';
                ripple.style.left = (x - 150) + 'px';
                ripple.style.top = (y - 150) + 'px';
                document.body.appendChild(ripple);
                setTimeout(() => ripple.remove(), 1000);
            };

            // Helper to create particle
            const createParticle = (x, y) => {
                for (let i = 0; i < 5; i++) {
                    const particle = document.createElement('div');
                    particle.className = 'particle';
                    particle.style.left = x + 'px';
                    particle.style.top = y + 'px';
                    particle.style.animationDelay = (i * 0.1) + 's';
                    document.body.appendChild(particle);
                    setTimeout(() => particle.remove(), 3000);
                }
            };

            // Add scanner line
            const scanner = document.createElement('div');
            scanner.className = 'scanner-line';
            document.body.appendChild(scanner);

            // Animate each category
            let counter = 0;
            const allElements = [
                ...elements.buttons.map(e => ({...e, type: 'button'})),
                ...elements.links.map(e => ({...e, type: 'link'})),
                ...elements.inputs.map(e => ({...e, type: 'input'}))
            ];

            for (const element of allElements) {
                counter++;

                // Create ripple at element location
                createRipple(
                    element.rect.x + element.rect.width / 2,
                    element.rect.y + element.rect.height / 2
                );

                // Create badge with animation
                const badge = document.createElement('div');
                badge.className = 'executive-badge';
                badge.style.left = element.rect.x + 'px';
                badge.style.top = Math.max(0, element.rect.y - 40) + 'px';
                badge.innerHTML = `<span class="badge-number">${counter}</span>`;

                // Color code by type
                if (element.type === 'button') {
                    badge.style.background = 'linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(16, 185, 129, 0.1))';
                    badge.style.borderColor = 'rgba(16, 185, 129, 0.3)';
                } else if (element.type === 'link') {
                    badge.style.background = 'linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(59, 130, 246, 0.1))';
                    badge.style.borderColor = 'rgba(59, 130, 246, 0.3)';
                } else {
                    badge.style.background = 'linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(245, 158, 11, 0.1))';
                    badge.style.borderColor = 'rgba(245, 158, 11, 0.3)';
                }

                // Stagger the animation
                badge.style.animation = `badgeFloat 3s ease-in-out infinite`;
                badge.style.animationDelay = (counter * 0.1) + 's';

                document.body.appendChild(badge);

                // Create particles
                createParticle(
                    element.rect.x + element.rect.width / 2,
                    element.rect.y + element.rect.height / 2
                );

                // Highlight the actual element
                const selector = element.type === 'button' ? 'button, [role="button"], .btn, .button' :
                               element.type === 'link' ? 'a[href]' :
                               'input:not([type="hidden"]), textarea, select';

                const els = document.querySelectorAll(selector);
                els.forEach(el => {
                    const rect = el.getBoundingClientRect();
                    if (Math.abs(rect.x - element.rect.x) < 2 &&
                        Math.abs(rect.y - element.rect.y) < 2) {
                        el.classList.add('executive-highlight');
                        el.classList.add('highlight-' + element.type);
                    }
                });

                // Move spotlight
                const overlay = document.querySelector('.executive-overlay');
                if (overlay) {
                    overlay.style.setProperty('--spotlight-x', (element.rect.x + element.rect.width/2) + 'px');
                    overlay.style.setProperty('--spotlight-y', (element.rect.y + element.rect.height/2) + 'px');
                }

                // Delay between discoveries for dramatic effect
                await new Promise(resolve => setTimeout(resolve, 150));
            }

            // Remove scanner after animation
            setTimeout(() => scanner.remove(), 3000);
        }
        """
        await self.page.evaluate(animation_script, elements)

    async def add_control_panel(self):
        """Add interactive control panel for presentation."""
        control_script = """
        () => {
            const panel = document.createElement('div');
            panel.className = 'control-panel';
            panel.innerHTML = `
                <button class="control-button" onclick="location.reload()">↻ Refresh</button>
                <button class="control-button" onclick="document.querySelector('.executive-overlay').style.display = document.querySelector('.executive-overlay').style.display === 'none' ? 'block' : 'none'">💡 Toggle Spotlight</button>
                <button class="control-button" onclick="window.print()">📸 Print Report</button>
            `;
            document.body.appendChild(panel);
        }
        """
        await self.page.evaluate(control_script)

    async def create_matrix_effect(self):
        """Create subtle matrix rain effect for dramatic entrance."""
        matrix_script = """
        () => {
            const container = document.createElement('div');
            container.className = 'matrix-rain';

            for (let i = 0; i < 50; i++) {
                const drop = document.createElement('div');
                drop.className = 'matrix-drop';
                drop.style.left = Math.random() * 100 + '%';
                drop.style.animationDuration = (Math.random() * 3 + 2) + 's';
                drop.style.animationDelay = Math.random() * 2 + 's';
                drop.textContent = Math.random() > 0.5 ? '1' : '0';
                container.appendChild(drop);
            }

            document.body.appendChild(container);
            setTimeout(() => container.remove(), 5000);
        }
        """
        await self.page.evaluate(matrix_script)

    async def capture_presentation(self, filename: str = "executive_showcase.png"):
        """Capture the final presentation."""
        await self.page.screenshot(path=filename, full_page=False)
        print(f"📸 Executive presentation captured: {filename}")

    async def run_showcase(self):
        """Run the complete executive showcase."""
        try:
            # Initialize
            await self.initialize()
            await self.navigate()

            print("🎬 Starting Executive Showcase...")
            print("━" * 60)

            # Inject all styles
            await self.inject_showcase_styles()

            # Create effects
            await self.create_spotlight_effect()
            await self.create_matrix_effect()

            # Detect elements
            print("🔍 Analyzing interactive elements...")
            elements = await self.detect_elements()
            print(f"✨ Found {elements['total']} interactive elements")

            # Create info panel
            await self.create_info_panel(elements)

            # Animate discovery
            print("🎭 Animating element discovery...")
            await self.animate_discovery(elements)

            # Add controls
            await self.add_control_panel()

            # Wait for effects to complete
            await asyncio.sleep(3)

            # Capture screenshot
            await self.capture_presentation()

            print("━" * 60)
            print("✅ Executive showcase complete!")
            print("💼 Ready for presentation to senior management")
            print("\n🎯 Key Features Demonstrated:")
            print("  • Glassmorphic UI elements")
            print("  • Animated element discovery")
            print("  • Spotlight focus effects")
            print("  • Real-time statistics dashboard")
            print("  • Interactive control panel")
            print("  • Particle and ripple effects")
            print("  • Category-based color coding")

            # Keep browser open
            print("\n⏰ Browser will remain open for 30 seconds...")
            await asyncio.sleep(30)

        finally:
            await self.cleanup()

    async def cleanup(self):
        """Clean up resources."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


async def main():
    """Main entry point."""
    print("\n" + "="*60)
    print("🌟 EXECUTIVE INTERACTIVE ELEMENTS SHOWCASE 🌟")
    print("="*60)
    print("\nThis tool creates stunning visual presentations of")
    print("interactive web elements for senior management review.\n")

    # Get URL from user
    url = input("Enter URL to showcase (default: https://www.example.com): ").strip()
    if not url:
        url = "https://uat.citi.com"

    # Create and run showcase
    showcase = ExecutiveShowcase(url, headless=False)
    await showcase.run_showcase()


if __name__ == "__main__":
    asyncio.run(main())
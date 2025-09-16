# Development Container Dockerfile for UI Testing Framework V3
ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim-bullseye

# Install system dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    # Build essentials
    build-essential \
    # Git
    git \
    # Chrome dependencies
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    xdg-utils \
    # Development tools
    curl \
    vim \
    sudo \
    # SQLite for storage
    sqlite3 \
    # Clean up
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome for Playwright (non-headless testing)
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Set up Python environment
USER $USERNAME
ENV PATH="/home/${USERNAME}/.local/bin:${PATH}"

# Install Python packages
RUN pip install --user --no-cache-dir \
    # Core dependencies
    playwright>=1.40.0 \
    langgraph>=0.0.20 \
    pydantic>=2.5.0 \
    # Testing
    pytest>=7.4.0 \
    pytest-asyncio>=0.21.0 \
    pytest-cov>=4.1.0 \
    pytest-mock>=3.12.0 \
    # Code quality
    black>=23.12.0 \
    ruff>=0.1.9 \
    mypy>=1.8.0 \
    # Development tools
    ipython>=8.18.0 \
    rich>=13.7.0 \
    httpx>=0.25.0 \
    # LLM providers (optional)
    openai>=1.6.0 \
    anthropic>=0.8.0 \
    google-generativeai>=0.3.0

# Install Playwright browsers
RUN playwright install chromium firefox webkit \
    && playwright install-deps

# Set up workspace
WORKDIR /workspace

# Create necessary directories
RUN mkdir -p /workspace/data /workspace/logs /workspace/config

# Set environment variables
ENV PYTHONPATH=/workspace
ENV PLAYWRIGHT_BROWSERS_PATH=/home/${USERNAME}/.cache/ms-playwright
ENV HEADLESS=false

# Copy configuration files if they exist
COPY --chown=${USERNAME}:${USERNAME} config/*.toml /workspace/config/ 2>/dev/null || true

# Entry point
CMD ["/bin/bash"]
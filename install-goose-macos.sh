#!/bin/bash

echo "=== Goose CLI Installation for macOS (via TreeTee) ==="
echo ""
echo "This script installs Goose AI coding assistant on macOS."
echo "Goose provides AI-powered coding assistance directly in your terminal."
echo ""

# Detect architecture
ARCH=$(uname -m)
if [ "$ARCH" == "arm64" ]; then
    echo "Detected: Apple Silicon (M1/M2/M3)"
elif [ "$ARCH" == "x86_64" ]; then
    echo "Detected: Intel Mac"
else
    echo "Warning: Unknown architecture: $ARCH"
fi

echo ""

# Check if already installed
if command -v goose &> /dev/null; then
    CURRENT_VERSION=$(goose --version 2>/dev/null | head -1)
    echo "Goose CLI is already installed: $CURRENT_VERSION"
    read -p "Do you want to update to the latest version? (y/N): " UPDATE
    if [[ ! $UPDATE =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
    echo "Updating Goose CLI..."
    goose update
    exit 0
fi

echo "=== Installation Method ==="
echo ""
echo "Choose installation method:"
echo "1. Homebrew (recommended)"
echo "2. Direct download (curl script)"
echo ""
read -p "Select method (1 or 2): " METHOD

if [ "$METHOD" == "1" ]; then
    # Homebrew installation
    echo ""
    echo "=== Installing via Homebrew ==="
    echo ""

    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo "Homebrew is not installed."
        echo "Install Homebrew first: https://brew.sh"
        echo ""
        read -p "Install Homebrew now? (y/N): " INSTALL_BREW
        if [[ $INSTALL_BREW =~ ^[Yy]$ ]]; then
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        else
            echo "Please install Homebrew and try again."
            exit 1
        fi
    fi

    echo "Installing Goose CLI via Homebrew..."
    if brew install block-goose-cli; then
        echo "✓ Goose CLI installed successfully"
    else
        echo "✗ Installation failed"
        exit 1
    fi

elif [ "$METHOD" == "2" ]; then
    # Direct download installation
    echo ""
    echo "=== Installing via direct download ==="
    echo ""

    echo "Downloading Goose CLI..."
    if curl -fsSL https://github.com/block/goose/releases/download/stable/download_cli.sh | bash; then
        echo "✓ Goose CLI installed successfully"
    else
        echo "✗ Installation failed"
        echo "Please check your internet connection and try again"
        exit 1
    fi

else
    echo "Invalid selection. Exiting."
    exit 1
fi

echo ""
echo "=== Verifying Installation ==="
echo ""

# Verify installation
if command -v goose &> /dev/null; then
    GOOSE_VERSION=$(goose --version 2>/dev/null | head -1)
    echo "✓ Goose CLI is installed: $GOOSE_VERSION"
    GOOSE_PATH=$(which goose)
    echo "  Installation path: $GOOSE_PATH"
else
    echo "✗ Goose CLI installation could not be verified"
    echo "  You may need to reload your shell or add Goose to PATH"
    echo ""
    echo "Try: source ~/.zshrc  (or ~/.bash_profile)"
    exit 1
fi

# Check .config directory permissions (important for M3 Macs)
if [ ! -d "$HOME/.config" ]; then
    echo ""
    echo "Creating ~/.config directory..."
    mkdir -p "$HOME/.config"
fi

if [ -w "$HOME/.config" ]; then
    echo "✓ ~/.config directory has write permissions"
else
    echo "⚠️  Warning: ~/.config directory may not have write permissions"
    echo "   Fixing permissions..."
    chmod u+w "$HOME/.config"
fi

echo ""
echo "=== Initial Configuration ==="
echo ""

# Check if already configured
if [ -f "$HOME/.config/goose/profiles.yaml" ]; then
    echo "Goose is already configured."
    echo "Configuration file: $HOME/.config/goose/profiles.yaml"
    echo ""
    read -p "Do you want to reconfigure? (y/N): " RECONFIG
    if [[ ! $RECONFIG =~ ^[Yy]$ ]]; then
        echo "Skipping configuration."
        echo ""
        echo "=== Installation Complete! ==="
        echo ""
        echo "Start chatting with Goose:"
        echo "  goose session start"
        echo ""
        echo "Or configure later:"
        echo "  goose configure"
        exit 0
    fi
fi

echo "Goose supports multiple AI providers:"
echo "  - Anthropic Claude (recommended, best performance)"
echo "  - OpenAI GPT"
echo "  - OpenRouter (multiple models, easy OAuth)"
echo "  - Tetrate Agent Router (\$10 free credits)"
echo "  - Local models via Docker Model Runner"
echo ""

read -p "Do you want to configure Goose now? (y/N): " CONFIG_NOW

if [[ $CONFIG_NOW =~ ^[Yy]$ ]]; then
    echo ""
    echo "Running goose configure..."
    echo "You'll need an API key from your chosen provider."
    echo ""
    goose configure
else
    echo ""
    echo "Skipping configuration for now."
    echo "You can configure later by running: goose configure"
fi

echo ""
echo "=== Installation Complete! ==="
echo ""
echo "Next steps:"
echo "1. If not configured, run: goose configure"
echo "2. Start a Goose session: goose session start"
echo "3. Chat with your AI coding assistant!"
echo ""
echo "Documentation: https://block.github.io/goose/"
echo "GitHub: https://github.com/block/goose"
echo ""
echo "Example usage:"
echo '  goose session start --profile default'
echo '  > "help me debug this Python script"'
echo '  > "create a FastAPI endpoint for user authentication"'
echo ""

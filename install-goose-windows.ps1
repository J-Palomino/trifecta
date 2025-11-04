# Goose CLI Installation for Windows (via DaisyChain)
# PowerShell script for installing Goose AI coding assistant

Write-Host "=== Goose CLI Installation for Windows (via DaisyChain) ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "This script installs Goose AI coding assistant on Windows."
Write-Host "Goose provides AI-powered coding assistance directly in your terminal."
Write-Host ""

# Check if already installed
$gooseInstalled = Get-Command goose -ErrorAction SilentlyContinue
if ($gooseInstalled) {
    Write-Host "Goose CLI is already installed" -ForegroundColor Green
    $currentVersion = & goose --version 2>$null | Select-Object -First 1
    Write-Host "Current version: $currentVersion"
    Write-Host ""
    $update = Read-Host "Do you want to update to the latest version? (y/N)"
    if ($update -match "^[Yy]$") {
        Write-Host "Updating Goose CLI..." -ForegroundColor Yellow
        & goose update
    } else {
        Write-Host "Installation cancelled."
        exit 0
    }
    exit 0
}

Write-Host "=== Installing Goose CLI ===" -ForegroundColor Cyan
Write-Host ""

# Download and run the installation script
Write-Host "Downloading Goose CLI installation script..." -ForegroundColor Yellow

try {
    # Download the install script
    $scriptUrl = "https://raw.githubusercontent.com/block/goose/main/download_cli.ps1"
    $scriptPath = "$env:TEMP\download_goose.ps1"

    Invoke-WebRequest -Uri $scriptUrl -OutFile $scriptPath -ErrorAction Stop

    Write-Host "Running installation script..." -ForegroundColor Yellow

    # Execute the downloaded script
    & $scriptPath

    # Clean up
    Remove-Item $scriptPath -ErrorAction SilentlyContinue

    Write-Host "Installation script completed successfully" -ForegroundColor Green
} catch {
    Write-Host "Installation failed: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Alternative installation methods:" -ForegroundColor Yellow
    Write-Host "1. Use WSL (Windows Subsystem for Linux):"
    Write-Host "   wsl curl -fsSL https://github.com/block/goose/releases/download/stable/download_cli.sh | bash"
    Write-Host ""
    Write-Host "2. Use Git Bash:"
    Write-Host "   curl -fsSL https://github.com/block/goose/releases/download/stable/download_cli.sh | bash"
    Write-Host ""
    Write-Host "3. Manual download from:"
    Write-Host "   https://github.com/block/goose/releases"
    exit 1
}

Write-Host ""
Write-Host "=== Verifying Installation ===" -ForegroundColor Cyan
Write-Host ""

# Refresh PATH
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Verify installation
$gooseCommand = Get-Command goose -ErrorAction SilentlyContinue
if ($gooseCommand) {
    $version = & goose --version 2>$null | Select-Object -First 1
    Write-Host "Goose CLI is installed: $version" -ForegroundColor Green
    Write-Host "Installation path: $($gooseCommand.Source)" -ForegroundColor Gray
} else {
    Write-Host "Goose CLI installation could not be verified" -ForegroundColor Red
    Write-Host "You may need to:"
    Write-Host "1. Restart your PowerShell/terminal"
    Write-Host "2. Add Goose to your PATH manually"
    Write-Host "3. Check the installation at: $env:USERPROFILE\.goose"
    exit 1
}

Write-Host ""
Write-Host "=== Initial Configuration ===" -ForegroundColor Cyan
Write-Host ""

# Check if already configured
$configPath = "$env:USERPROFILE\.config\goose\profiles.yaml"
if (Test-Path $configPath) {
    Write-Host "Goose is already configured." -ForegroundColor Green
    Write-Host "Configuration file: $configPath"
    Write-Host ""
    $reconfig = Read-Host "Do you want to reconfigure? (y/N)"
    if ($reconfig -notmatch "^[Yy]$") {
        Write-Host "Skipping configuration."
        Write-Host ""
        Write-Host "=== Installation Complete! ===" -ForegroundColor Green
        Write-Host ""
        Write-Host "Start chatting with Goose:"
        Write-Host "  goose session start"
        Write-Host ""
        Write-Host "Or configure later:"
        Write-Host "  goose configure"
        exit 0
    }
}

Write-Host "Goose supports multiple AI providers:" -ForegroundColor Yellow
Write-Host "  - Anthropic Claude (recommended, best performance)"
Write-Host "  - OpenAI GPT"
Write-Host "  - OpenRouter (multiple models, easy OAuth)"
Write-Host "  - Tetrate Agent Router (`$10 free credits)"
Write-Host "  - Local models via Docker Model Runner"
Write-Host ""

$configNow = Read-Host "Do you want to configure Goose now? (y/N)"

if ($configNow -match "^[Yy]$") {
    Write-Host ""
    Write-Host "Running goose configure..." -ForegroundColor Yellow
    Write-Host "You'll need an API key from your chosen provider."
    Write-Host ""
    & goose configure
} else {
    Write-Host ""
    Write-Host "Skipping configuration for now."
    Write-Host "You can configure later by running: goose configure"
}

Write-Host ""
Write-Host "=== Installation Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. If not configured, run: goose configure"
Write-Host "2. Start a Goose session: goose session start"
Write-Host "3. Chat with your AI coding assistant!"
Write-Host ""
Write-Host "Documentation: https://block.github.io/goose/"
Write-Host "GitHub: https://github.com/block/goose"
Write-Host ""
Write-Host "Example usage:" -ForegroundColor Yellow
Write-Host '  goose session start --profile default'
Write-Host '  > "help me debug this Python script"'
Write-Host '  > "create a FastAPI endpoint for user authentication"'
Write-Host ""

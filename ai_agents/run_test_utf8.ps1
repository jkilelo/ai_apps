# PowerShell script to run tests with full UTF-8 support

# Set console to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# Set environment variables for UTF-8
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
$env:PYTHONLEGACYWINDOWSFSENCODING = "0"
$env:PYTHONLEGACYWINDOWSSTDIO = "0"
$env:LC_ALL = "en_US.UTF-8"
$env:LANG = "en_US.UTF-8"
$env:LANGUAGE = "en_US.UTF-8"
$env:PYTHONUNBUFFERED = "1"

# Set console code page to UTF-8
chcp 65001 | Out-Null

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "UTF-8 Environment Configuration" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "PYTHONIOENCODING=$env:PYTHONIOENCODING"
Write-Host "PYTHONUTF8=$env:PYTHONUTF8"
Write-Host "Console OutputEncoding: $([Console]::OutputEncoding.EncodingName)"
Write-Host "Console Code Page: 65001 (UTF-8)"
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Run the Python script with UTF-8 support
& python ai_agents/run_with_utf8.py

# Keep window open
Write-Host "`nPress any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
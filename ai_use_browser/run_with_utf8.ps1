# PowerShell script to run Python with UTF-8 encoding

# Set environment variables for UTF-8
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

# Set console output encoding to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "Running Python with UTF-8 encoding..." -ForegroundColor Green
python main.py $args
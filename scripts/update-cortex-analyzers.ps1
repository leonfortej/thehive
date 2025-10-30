# Cortex Analyzers/Responders Auto-Update Script for Windows
# This script pulls the latest changes from GitHub and restarts Cortex

param(
    [string]$RepoPath = "C:\thehive",
    [string]$DockerComposePath = "C:\docker\thehive\testing",
    [string]$LogFile = "C:\docker\thehive\testing\cortex-sync.log",
    [switch]$RestartCortex = $true
)

# Function to write log with timestamp
function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] $Message"
    Write-Host $logMessage
    Add-Content -Path $LogFile -Value $logMessage
}

# Start logging
Write-Log "========================================"
Write-Log "Starting Cortex analyzer/responder update"

# Navigate to repository directory
if (-not (Test-Path $RepoPath)) {
    Write-Log "ERROR: Cannot access $RepoPath"
    exit 1
}

Set-Location $RepoPath

# Get current commit hash
try {
    $beforeCommit = git rev-parse HEAD
    Write-Log "Current commit: $beforeCommit"
} catch {
    Write-Log "ERROR: Failed to get current commit: $_"
    exit 1
}

# Pull latest changes
Write-Log "Pulling latest changes from GitHub..."
try {
    $gitOutput = git pull origin main 2>&1 | Out-String
    Write-Log "Git pull output: $gitOutput"

    # Get new commit hash
    $afterCommit = git rev-parse HEAD

    if ($beforeCommit -ne $afterCommit) {
        Write-Log "Repository updated: $beforeCommit -> $afterCommit"

        # Check if requirements.txt changed
        $changedFiles = git diff --name-only $beforeCommit $afterCommit
        if ($changedFiles -match "requirements.txt") {
            Write-Log "requirements.txt changed, you may need to rebuild analyzer Docker images"
        }

        # Restart Cortex if requested
        if ($RestartCortex) {
            Write-Log "Restarting Cortex container..."
            Set-Location $DockerComposePath

            try {
                $restartOutput = docker-compose restart cortex 2>&1 | Out-String
                Write-Log "Cortex restart output: $restartOutput"
                Write-Log "Cortex restarted successfully"
            } catch {
                Write-Log "ERROR: Failed to restart Cortex: $_"
            }

            Set-Location $RepoPath
        } else {
            Write-Log "Skipping Cortex restart (use -RestartCortex to enable)"
            Write-Log "Please restart Cortex manually or refresh in the UI"
        }
    } else {
        Write-Log "Repository already up to date"
    }
} catch {
    Write-Log "ERROR: Git pull failed: $_"
    exit 1
}

Write-Log "Update check completed"
Write-Log "========================================"
Write-Log ""

# Return to original directory
Set-Location $PSScriptRoot

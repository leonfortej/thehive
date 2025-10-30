#!/bin/bash
#
# Cortex Analyzers/Responders Auto-Update Script
# This script pulls the latest changes from GitHub and optionally refreshes Cortex
#

# Configuration
REPO_DIR="/opt/CustomAnalyzers"  # Adjust this to where you clone the repo on your Docker host
LOG_FILE="/var/log/cortex-sync.log"
CORTEX_URL="http://localhost:9001"  # Adjust to your Cortex URL
CORTEX_API_KEY=""  # Add your Cortex API key here if you want automatic refresh

# Timestamp function
timestamp() {
    date "+%Y-%m-%d %H:%M:%S"
}

# Start logging
echo "========================================" | tee -a "$LOG_FILE"
echo "[$(timestamp)] Starting Cortex analyzer/responder update" | tee -a "$LOG_FILE"

# Navigate to repository directory
cd "$REPO_DIR" || {
    echo "[$(timestamp)] ERROR: Cannot access $REPO_DIR" | tee -a "$LOG_FILE"
    exit 1
}

# Get current commit hash
BEFORE_COMMIT=$(git rev-parse HEAD)
echo "[$(timestamp)] Current commit: $BEFORE_COMMIT" | tee -a "$LOG_FILE"

# Pull latest changes
echo "[$(timestamp)] Pulling latest changes from GitHub..." | tee -a "$LOG_FILE"
GIT_OUTPUT=$(git pull origin main 2>&1)
GIT_EXIT_CODE=$?

if [ $GIT_EXIT_CODE -eq 0 ]; then
    echo "[$(timestamp)] Git pull successful" | tee -a "$LOG_FILE"
    echo "$GIT_OUTPUT" >> "$LOG_FILE"

    # Get new commit hash
    AFTER_COMMIT=$(git rev-parse HEAD)

    if [ "$BEFORE_COMMIT" != "$AFTER_COMMIT" ]; then
        echo "[$(timestamp)] Repository updated: $BEFORE_COMMIT -> $AFTER_COMMIT" | tee -a "$LOG_FILE"

        # Update Python dependencies if requirements.txt changed
        if git diff --name-only "$BEFORE_COMMIT" "$AFTER_COMMIT" | grep -q "requirements.txt"; then
            echo "[$(timestamp)] requirements.txt changed, updating dependencies..." | tee -a "$LOG_FILE"
            pip3 install -r requirements.txt >> "$LOG_FILE" 2>&1
        fi

        # Trigger Cortex refresh if API key is configured
        if [ -n "$CORTEX_API_KEY" ]; then
            echo "[$(timestamp)] Triggering Cortex analyzer refresh..." | tee -a "$LOG_FILE"

            # Refresh analyzers
            ANALYZER_REFRESH=$(curl -s -X POST \
                -H "Authorization: Bearer $CORTEX_API_KEY" \
                -H "Content-Type: application/json" \
                "$CORTEX_URL/api/organization/analyzer/_search" 2>&1)

            # Refresh responders
            RESPONDER_REFRESH=$(curl -s -X POST \
                -H "Authorization: Bearer $CORTEX_API_KEY" \
                -H "Content-Type: application/json" \
                "$CORTEX_URL/api/organization/responder/_search" 2>&1)

            echo "[$(timestamp)] Cortex refresh triggered" | tee -a "$LOG_FILE"
        else
            echo "[$(timestamp)] CORTEX_API_KEY not set, skipping automatic refresh" | tee -a "$LOG_FILE"
            echo "[$(timestamp)] Please refresh analyzers manually in Cortex UI or restart Cortex" | tee -a "$LOG_FILE"
        fi

    else
        echo "[$(timestamp)] Repository already up to date" | tee -a "$LOG_FILE"
    fi
else
    echo "[$(timestamp)] ERROR: Git pull failed with exit code $GIT_EXIT_CODE" | tee -a "$LOG_FILE"
    echo "$GIT_OUTPUT" | tee -a "$LOG_FILE"
    exit 1
fi

echo "[$(timestamp)] Update check completed" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "" >> "$LOG_FILE"

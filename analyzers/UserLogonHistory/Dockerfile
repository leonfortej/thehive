FROM python:3.12-slim

# Metadata
LABEL maintainer="TheHive Development Team"
LABEL description="UserLogonHistory Analyzer for TheHive Cortex"
LABEL version="1.0.0"

# Set working directory
WORKDIR /worker

# Copy common utilities
COPY common /worker/common

# Copy analyzer files
COPY analyzers/UserLogonHistory /worker/analyzers/UserLogonHistory

# Install dependencies
RUN pip install --no-cache-dir -r /worker/analyzers/UserLogonHistory/requirements.txt

# Set the entrypoint
ENTRYPOINT ["python", "/worker/analyzers/UserLogonHistory/userlogonhistory.py"]

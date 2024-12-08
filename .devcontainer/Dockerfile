# FROM mcr.microsoft.com/devcontainers/python:1-3.11-bookworm
FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye

# Update the package manager
RUN apt-get update -y

# Set the working directory
WORKDIR /workspaces

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Install HTTPie
RUN pip install --no-cache-dir httpie

# Default command for debugging
CMD ["/usr/bin/zsh"]

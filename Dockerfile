# Stage 1: Build the executable using a full Python image
FROM python:3.9.19-slim AS builder

# Install necessary system dependencies including binutils for PyInstaller
RUN apt-get update && apt-get install -y \
    firefox-esr \
    binutils \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Install Firefox dependencies
# RUN apt-get update && apt-get install -y \
#     wget \
#     firefox-esr \
#     xvfb \
#     libxrender1 \
#     libxtst6 \
#     libxi6 \
#     && rm -rf /var/lib/apt/lists/*

# Copy project files
WORKDIR /app
COPY requirements.txt ./
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install PyInstaller and build the executable
RUN pip install pyinstaller
RUN pyinstaller prod.spec


# Stage 2: Create a smaller image
# FROM debian:buster-slim

# Install Firefox and Xvfb
# RUN apt-get update && apt-get install -y \
#     firefox-esr \
#     xvfb \
#     && rm -rf /var/lib/apt/lists/*

# Copy the built executable from the builder stage
# COPY --from=builder /app/dist/fb-group-scraper /usr/local/bin/fb-group-scraper

# Set up entrypoint
ENTRYPOINT ["/app/dist/fb-group-scraper"]
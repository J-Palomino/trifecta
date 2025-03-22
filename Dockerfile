# Use the official Node.js 18 image as a parent image
FROM node:18-slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up the application
WORKDIR /app

# Copy package files first to leverage Docker cache
COPY package*.json ./
RUN npm install meshcentral

# Copy the rest of the application
COPY . .

# Set execute permissions for the startup script
RUN chmod +x /app/start.sh

# Expose ports
EXPOSE 80 443 8080 8443

# Set environment variables
ENV NODE_ENV=production \
    PYTHONUNBUFFERED=1

# Run the startup script
CMD ["/app/start.sh"] 
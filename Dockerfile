# Use the official Node.js 18 image as a parent image
FROM node:18-slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    gettext-base \
    wget \
    gnupg \
    && wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | apt-key add - \
    && echo "deb http://repo.mongodb.org/apt/debian bullseye/mongodb-org/6.0 main" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list \
    && apt-get update \
    && apt-get install -y mongodb-database-tools \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up the application
WORKDIR /app

# Copy package files first to leverage Docker cache
COPY package*.json ./
RUN npm install meshcentral

# Copy the rest of the application
COPY . .

# Make entrypoint script executable
RUN chmod +x docker-entrypoint.sh

# Expose ports
EXPOSE 80 443

# Set environment variables
ENV NODE_ENV=production \
    PYTHONUNBUFFERED=1

# Use entrypoint script to generate config and start MeshCentral
ENTRYPOINT ["./docker-entrypoint.sh"] 
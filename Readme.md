# MeshCentral with Redirect Handler for Railway

This repository contains a MeshCentral setup with a custom redirect handler designed to work smoothly on Railway.app.

## Features

- MeshCentral server running in WAN mode
- Custom Python redirect handler to prevent redirect loops
- Docker setup for easy deployment

## Deployment to Railway

### Option 1: Railway CLI

1. Install the Railway CLI:
   ```
   npm install -g @railway/cli
   ```

2. Login to Railway:
   ```
   railway login
   ```

3. Link to your Railway project:
   ```
   railway link
   ```

4. Deploy:
   ```
   railway up
   ```

### Option 2: GitHub Repository Deployment

1. Fork this repository to your GitHub account
2. Connect to Railway.app and create a new project
3. Choose "Deploy from GitHub repo"
4. Select your forked repository
5. Railway will automatically build and deploy the application

### Option 3: Deploy from Template

1. Click the "Deploy on Railway" button
2. Follow the instructions to set up your project

## Custom Domain Setup

1. In the Railway Dashboard, go to Settings
2. Under "Domains", add your custom domain
3. Update the DNS records as instructed by Railway
4. The application will automatically use your custom domain

## Environment Variables

You can configure the following environment variables in Railway:

- `HOSTNAME`: Your domain name (defaults to your Railway subdomain)
- `NODE_ENV`: Set to "production" for production environments

## Troubleshooting

### Redirect Loops

If you encounter redirect loops, check the logs for detailed information about the request and response flow.

### Certificate Issues

The application automatically uses Railway's TLS certificates. If you encounter certificate issues, ensure your custom domain is properly set up in Railway's dashboard.

## Local Development

To run the application locally:

```
docker-compose up
```

This will start MeshCentral and the redirect handler, making them accessible at:
- HTTP: http://localhost:80
- HTTPS: https://localhost:443
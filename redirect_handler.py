import asyncio
import os
from urllib.parse import urlparse, urlunparse
from aiohttp import web
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Configuration
HTTPS_PORT = 8443
HTTPS_HOST = None  # Will be auto-detected from request

async def handle_redirect(request):
    """
    Redirect all HTTP requests to HTTPS on port 8443
    """
    # Get the original host from the request
    original_host = request.headers.get('Host', '')
    
    # Extract the hostname (without port)
    hostname = original_host.split(':')[0] if ':' in original_host else original_host
    
    # Build the target HTTPS URL
    target_url = urlunparse((
        'https',                          # scheme
        f"{hostname}:{HTTPS_PORT}",       # netloc with port 8443
        request.path,                     # path
        '',                               # params
        request.query_string,             # query
        ''                                # fragment
    ))
    
    logger.info(f"Redirecting: {request.url} → {target_url}")
    
    # Perform a 302 redirect
    return web.HTTPFound(target_url)

async def on_shutdown(app):
    """Handler for application shutdown"""
    logger.info("HTTP redirect server shutting down")

async def start_server():
    """Start the HTTP to HTTPS redirect server"""
    # Create the application
    app = web.Application()
    
    # Register the on_shutdown handler BEFORE anything else
    app.on_shutdown.append(on_shutdown)
    
    # Set up routes - catch all paths
    app.router.add_get('/', handle_redirect)
    app.router.add_get('/{path:.*}', handle_redirect)
    
    # Start the server
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Listen on all interfaces on port 80
    site = web.TCPSite(runner, '0.0.0.0', 80)
    await site.start()
    
    logger.info(f"HTTP redirect server started on port 80, redirecting to port {HTTPS_PORT}")
    logger.info(f"Process ID: {os.getpid()}")
    
    # Keep the server running
    try:
        while True:
            await asyncio.sleep(3600)  # Sleep for an hour
    except asyncio.CancelledError:
        logger.info("Server shutdown requested")
    finally:
        await runner.cleanup()

def main():
    """Main entry point"""
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        logger.info("HTTP redirect server stopped by user")

if __name__ == "__main__":
    main() 
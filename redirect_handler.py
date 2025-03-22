import aiohttp
from aiohttp import web
import re
import asyncio
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Regular expression to match URLs with :443 in them
PORT_RE = re.compile(r':443(/.*)?$')

async def handle_request(request):
    """Handle incoming requests and fix redirect loops"""
    # Log the request
    logger.info(f"Received request: {request.method} {request.path}")
    logger.info(f"Headers: {request.headers}")
    
    # Check for Railway-specific headers
    railway_headers = {k: v for k, v in request.headers.items() if k.lower().startswith('x-railway')}
    if railway_headers:
        logger.info(f"Railway headers: {railway_headers}")
    
    # Check if we need to fix a URL with :443 in it
    if PORT_RE.search(request.path) or ":443" in request.url.path:
        # Remove :443 from the path
        fixed_path = PORT_RE.sub(r'\1', request.path)
        logger.info(f"Redirecting from {request.path} to {fixed_path}")
        # Use absolute URL without port to avoid further redirects
        hostname = os.environ.get('HOSTNAME', 'tee.up.railway.app')
        return web.HTTPFound(f"https://{hostname}{fixed_path}")
    
    # Forward the request to the real server
    target_url = f"http://localhost:8443{request.path}"
    
    async with aiohttp.ClientSession() as session:
        try:
            # Forward the request with the same method and headers
            method = request.method
            headers = {k: v for k, v in request.headers.items() 
                      if k.lower() not in ('host', 'content-length')}
            # Add X-Forwarded headers to help MeshCentral understand the request
            headers['X-Forwarded-Proto'] = 'https'
            headers['X-Forwarded-Host'] = os.environ.get('HOSTNAME', 'tee.up.railway.app')
            headers['X-Forwarded-For'] = request.headers.get('X-Forwarded-For', request.remote)
            
            # Get the body if it exists
            body = await request.read() if request.body_exists else None
            
            # Log the forwarded request
            logger.info(f"Forwarding {method} request to {target_url}")
            logger.info(f"With headers: {headers}")
            
            async with session.request(
                method, 
                target_url, 
                headers=headers, 
                data=body, 
                allow_redirects=False
            ) as resp:
                # Check if the response is a redirect
                if 300 <= resp.status < 400 and 'Location' in resp.headers:
                    location = resp.headers['Location']
                    logger.info(f"Received redirect to {location}")
                    
                    # Check if the redirect contains :443
                    if ':443' in location:
                        fixed_location = location.replace(':443', '')
                        logger.info(f"Fixed redirect location: {fixed_location}")
                        return web.HTTPFound(fixed_location)
                
                # Create a response with the same status and headers
                response = web.StreamResponse(status=resp.status)
                
                # Copy headers, excluding some that will be set by aiohttp
                for key, value in resp.headers.items():
                    if key.lower() not in ('content-length', 'transfer-encoding', 'content-encoding', 'connection'):
                        if key.lower() == 'location' and ':443' in value:
                            # Fix location headers to avoid redirect loops
                            response.headers[key] = value.replace(':443', '')
                        else:
                            response.headers[key] = value
                
                # Start the response
                await response.prepare(request)
                
                # Stream the body
                async for data in resp.content.iter_any():
                    await response.write(data)
                
                await response.write_eof()
                return response
                
        except Exception as e:
            logger.error(f"Error forwarding request: {e}")
            return web.HTTPInternalServerError(text=str(e))

async def start_server():
    """Start the redirect handler server"""
    app = web.Application()
    app.router.add_route('*', '/{path:.*}', handle_request)
    
    # Setup the server
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Listen on port 443 for HTTPS and 80 for HTTP
    https_site = web.TCPSite(runner, '0.0.0.0', 443)
    http_site = web.TCPSite(runner, '0.0.0.0', 80)
    
    await https_site.start()
    await http_site.start()
    
    logger.info("Redirect handler running on ports 80 and 443")
    
    # Keep the server running
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(start_server()) 
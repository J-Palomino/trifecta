import aiohttp
import asyncio

async def check_nginx_setup():
    """Check if NGINX is properly handling the redirects"""
    print("Checking NGINX setup...")
    
    async with aiohttp.ClientSession() as session:
        # First try to access the server directly
        try:
            url = "http://localhost"
            print(f"Checking: {url}")
            async with session.get(url, allow_redirects=False) as response:
                print(f"Status: {response.status}")
                print(f"Headers: {dict(response.headers)}")
                if response.status in [301, 302]:
                    print(f"Redirect to: {response.headers.get('Location')}")
        except Exception as e:
            print(f"Error: {str(e)}")
        
        # Then try to access HTTPS
        try:
            url = "https://localhost:443"
            print(f"\nChecking: {url}")
            async with session.get(url, allow_redirects=False, ssl=False) as response:
                print(f"Status: {response.status}")
                print(f"Headers: {dict(response.headers)}")
        except Exception as e:
            print(f"Error: {str(e)}")
        
        # Finally check for URL with port in path
        try:
            url = "https://localhost:443/:443/"
            print(f"\nChecking URL with port in path: {url}")
            async with session.get(url, allow_redirects=False, ssl=False) as response:
                print(f"Status: {response.status}")
                print(f"Headers: {dict(response.headers)}")
                if response.status in [301, 302]:
                    print(f"Redirect to: {response.headers.get('Location')}")
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(check_nginx_setup()) 
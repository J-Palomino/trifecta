import aiohttp
import asyncio

async def check_redirects(url, max_redirects=10):
    print(f"Checking redirect chain for {url}")
    redirect_count = 0
    current_url = url
    history = []
    
    async with aiohttp.ClientSession() as session:
        while redirect_count < max_redirects:
            try:
                print(f"Requesting: {current_url}")
                async with session.get(current_url, allow_redirects=False) as response:
                    history.append({
                        "url": current_url,
                        "status": response.status,
                        "headers": dict(response.headers)
                    })
                    
                    if 300 <= response.status < 400:
                        location = response.headers.get('Location')
                        if not location:
                            print(f"Redirect status {response.status} but no Location header!")
                            break
                            
                        print(f"Redirect #{redirect_count+1}: {current_url} → {location} (HTTP {response.status})")
                        current_url = location if location.startswith('http') else f"{url.split('/')[0]}//{url.split('/')[2]}{location}"
                        redirect_count += 1
                    else:
                        print(f"Final destination: {current_url} (HTTP {response.status})")
                        break
            except Exception as e:
                print(f"Error: {str(e)}")
                history.append({
                    "url": current_url,
                    "error": str(e)
                })
                break
        
        if redirect_count >= max_redirects:
            print("Too many redirects detected!")
        
        print("\nFull redirect history:")
        for i, step in enumerate(history):
            print(f"Step {i+1}:")
            print(f"  URL: {step['url']}")
            if 'status' in step:
                print(f"  Status: {step['status']}")
                if 'headers' in step:
                    print(f"  Headers:")
                    for key, value in step['headers'].items():
                        print(f"    {key}: {value}")
            else:
                print(f"  Error: {step['error']}")
            print("")

if __name__ == "__main__":
    asyncio.run(check_redirects("https://tee.up.railway.app")) 
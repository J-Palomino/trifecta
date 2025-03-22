import ssl
import socket
import aiohttp
import asyncio
import datetime

async def check_certificate(hostname, port=443):
    print(f"Checking SSL certificate for {hostname}:{port}...")
    
    # First try to connect directly
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                
                subject = dict(x[0] for x in cert['subject'])
                issued_to = subject.get('commonName', 'N/A')
                
                issuer = dict(x[0] for x in cert['issuer'])
                issued_by = issuer.get('commonName', 'N/A')
                
                valid_from = cert['notBefore']
                valid_until = cert['notAfter']
                
                print(f"Certificate Information:")
                print(f"  Issued to: {issued_to}")
                print(f"  Issued by: {issued_by}")
                print(f"  Valid from: {valid_from}")
                print(f"  Valid until: {valid_until}")
                
                san = cert.get('subjectAltName', [])
                if san:
                    print(f"  Subject Alternative Names:")
                    for type_id, name in san:
                        print(f"    {name}")
                
                return True
    except Exception as e:
        print(f"Direct connection error: {str(e)}")
    
    # Try using aiohttp
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://{hostname}") as response:
                print(f"HTTPS response status: {response.status}")
                return response.status < 400
    except Exception as e:
        print(f"HTTPS request error: {str(e)}")
        return False

if __name__ == "__main__":
    domain = "tee.up.railway.app"
    asyncio.run(check_certificate(domain)) 
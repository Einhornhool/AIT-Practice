from aiocoap import *
import asyncio

async def request_resources():
    protocol = await Context.create_client_context()

    request = Message(code=GET, uri='coap://[2001:67c:254:b0b2:affe:4000:0:1]/.well-known/core')

    try:
        response = await protocol.request(request).response
    except Exception as e:
        print('Failed to fetch resource:')
        print(e)

    if not response.code.is_successful():
        print(f'Request failed: {response.code}')
        return

    request = Message(code=GET, uri='coap://[2001:67c:254:b0b2:affe:4000:0:1]/endpoint-lookup/')

    try:
        response = await protocol.request(request).response
    except Exception as e:
        print('Failed to fetch resource:')
        print(e)

    print(f'Result: {response.payload}')

if __name__ == '__main__':
    asyncio.run(request_resources())
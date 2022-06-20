from aiocoap import *
import asyncio
import re

def get_address(payload):
    payload = payload.split(";")
    for s in payload:
        if re.match("^base", s):
            print(f'String: {s}')
            split= s.split("=")[1]
            print(f'String: {split}')
            return split

async def send_request(request, protocol):
    try:
        response = await protocol.request(request).response
    except Exception as e:
        print('Failed to fetch resource:')
        print(e)

    if response.code.is_successful():
        return response.payload
    return None

async def request_resources():
    protocol = await Context.create_client_context()

    request = Message(code=GET, uri='coap://[2001:67c:254:b0b2:affe:4000:0:1]/.well-known/core')
    payload = send_request(request, protocol)

    if payload == None:
        print(f'/.well-ḱnown/core request failed')
        return

    request = Message(code=GET, uri='coap://[2001:67c:254:b0b2:affe:4000:0:1]/endpoint-lookup/')
    payload = send_request(request, payload)
    if payload == None:
        print(f'/endpoint-lookup/ request failed')
        return

    print(f"Payload: {payload}")

    addr = get_address(str(payload))
    print(f'Address {addr}')

    request = Message(code=GET, uri=addr)
    payload = send_request(request, payload)
    if payload == None:
        print(f'Resource request failed')
        return

    print(f'Result: {payload}')

if __name__ == '__main__':
    asyncio.run(request_resources())
from aiocoap import *
import asyncio
import json

def get_addresses_and_resources(payload):
    d = {}
    payload = payload.decode().replace('<', '').replace('>', '').split(',')
    for p in payload:
        p = p.split("]")
        addr = f'{p[0]}]'
        if addr not in d.keys():
            d[addr] = {'btn' : [], 'led' : [], 'sensor' : []}
        t = p[1].split('/')[1]
        d[addr][t].append(p[1])
    return d

async def get_value(request, protocol):
    response = None
    try:
        response = await protocol.request(request).response
    except Exception as e:
        print('Failed to fetch resource:')
        print(e)

    if response.code.is_successful():
        return response.payload
    return None

async def put_value(val, addr, protocol):
    payload = bytes(str(val), 'ascii')
    request = Message(code=PUT, payload=payload, uri=f'{addr}')

    response = await protocol.request(request).response
    if not response.code.is_successful():
        print("PUT failed")

async def query_all_sensors(sensors, protocol):
    for addr in sensors.keys():
        print(f'Address: {addr}')
        for s in sensors[addr]['sensors']:
            request = Message(code=GET, uri=f'{addr}{s}')
            payload = await get_value(request, protocol)
            print(f'{s}: {payload.decode()}')

async def query_accel(addr, protocol):
    request = Message(code=GET, uri=f'{addr}/sensor/acce')
    payload = await get_value(request, protocol)
    if payload != None:
        return json.loads(payload.decode().replace('\x00', ''))

async def all_leds_on(addr, leds, protocol):
    for l in leds:
        await put_value(1, f'{addr}{l}', protocol)

async def all_leds_of(addr, leds, protocol):
    for l in leds:
        await put_value(0, f'{addr}{l}', protocol)


async def request_resources():
    protocol = await Context.create_client_context()

    request = Message(code=GET, uri='coap://[2001:67c:254:b0b2:affe:45fc:fd31:5fde]/.well-known/core')
    payload = await get_value(request, protocol)

    if payload == None:
        print(f'/.well-ḱnown/core request failed')
        return

    request = Message(code=GET, uri='coap://[2001:67c:254:b0b2:affe:4000:0:1]/resource-lookup/')
    payload = await get_value(request, protocol)

    if payload == None:
        print(f'/resource-lookup/ request failed')
        return

    resources = get_addresses_and_resources(payload)
    print(f"Resources: {resources}")

    for a in resources.keys():
        await all_leds_on(a, resources[a]['led'], protocol)

    print("Starting Loop")
    while True:
        for a in resources.keys():
            acce = await query_accel(a, protocol)
            print(f"{acce}")
            print(type(acce))
            if acce["d"][2] < -1:
                await all_leds_of(a, resources[a]['led'], protocol)

    # protocol.shutdown()

if __name__ == '__main__':
    asyncio.run(request_resources())
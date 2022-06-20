from aiocoap import *
import asyncio
import re
import json

def get_address(payload):
    addr = []
    for p in payload:
        p = p.split(";")
        for s in p:
            if re.match("^base", s):
                addr.append(s.split("=")[1].replace('"', ''))
    return addr

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

async def get_all_sensors(addr, protocol):
    ret = {}
    for a in addr:
        request = Message(code=GET, uri=f'{a}/.well-known/core')
        payload = await get_value(request, protocol)
        if payload == None:
            print(f'Resource request failed')
            return

        sensors = payload.decode().replace('<', '').replace('>', '').split(',')
        btn = [s for s in sensors if re.match('^/btn', s)]
        leds = [s for s in sensors if re.match('^/led', s)]
        sens = [s for s in sensors if re.match('^/sensor', s)]
        ret[a] = {
            'btn' : btn,
            'leds' : leds,
            'sensors' : sens}
    return ret

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
        return payload.decode()['d']

async def all_leds_on(addr, leds, protocol):
    for l in leds:
        await put_value(1, f'{addr}{l}', protocol)

async def all_leds_of(addr, leds, protocol):
    for l in leds:
        await put_value(0, f'{addr}{l}', protocol)


async def request_resources():
    protocol = await Context.create_client_context()

    print("Request 1")
    request = Message(code=GET, uri='coap://[2001:67c:254:b0b2:affe:45fc:fd31:5fde]/.well-known/core')
    payload = await get_value(request, protocol)

    if payload == None:
        print(f'/.well-ḱnown/core request failed')
        return

    print("Request 2")
    request = Message(code=GET, uri='coap://[2001:67c:254:b0b2:affe:4000:0:1]/endpoint-lookup/')
    payload = await get_value(request, protocol)

    if payload == None:
        print(f'/endpoint-lookup/ request failed')
        return

    # print(f"Payload: {payload.decode()}")

    addr = get_address(payload.decode().split(','))

    print("Request 3")
    sensors = await get_all_sensors(addr, protocol)

    for a in sensors.keys():
        await all_leds_on(a, sensors[a]['leds'], protocol)
    # await query_all_sensors(sensors, protocol)

    while True:
        for a in sensors.keys():
            acce = await query_accel(a, protocol)
            if acce[2] < -1:
                await all_leds_of(addr, sensors[a]['leds'], protocol)

if __name__ == '__main__':
    asyncio.run(request_resources())
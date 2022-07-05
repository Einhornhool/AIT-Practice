from aiocoap import *
import curses
import asyncio

from datetime import datetime

playing_field = """
    +–––+---+–––+
    |   |   |   |
    +–––+–––+–––+
    |   |   |   |
    +–––+–––+–––+
    |   |   |   |
    +–––+–––+–––+
"""

field_pos = {   '00': (2, 6),
                '01': (2, 10),
                '02': (2, 14),
                '10': (4, 6),
                '11': (4, 10),
                '12': (4, 14),
                '20': (6, 6),
                '21': (6, 10),
                '22': (6, 14)
}

async def get_addr(protocol):
    addr = "coap://[2001:67c:254:b0b2:affe:4000:0:1]/"
    response = await protocol.request(Message(code=GET, uri=addr + "endpoint-lookup/")).response

    resp_str = str(response.payload)

    addr_mc = []
    for splitted in resp_str.split('base="'):
        if splitted[:4] == 'coap':
            addr_mc.append(splitted[:splitted.find('"')])

    return addr_mc

async def get_sensors(protocol, addr_mc):
    response = await protocol.request(Message(code=GET, uri=addr_mc + "/.well-known/core")).response
    # print("response: {}". format(response.payload))

    sensor_list = str(response.payload)[2:]
    sensor_array = []
    for s in sensor_list.split(","):
        s_repl = s.replace("<", "").replace(">", "").replace("'", "")
        sensor_array.append(s_repl)
        # print(s_repl)

    return sensor_array


async def read_sensor(protocol, addr, sensor):
    response = await protocol.request(Message(code=GET, uri=addr + sensor)).response
    # print("sensor: " + sensor + " --- response: {}". format(response.payload))
    return response.payload



async def tictactoe(protocol, addr_mc):
    screen = curses.initscr()
    ttt_ar = [['','','']
             ,['','','']
             ,['','','']]

    end = 0
    p = 1
    sym = 'X' if p == 1 else 'O'

    while end == 0:

        # print('Current field:', ttt_ar)
        # print('Current player:', p)
        screen.addstr(0, 0, playing_field)
        screen.addstr(7, 0, f'Player: {p}')

        c_loc = await cursor_loc(protocol, addr_mc, screen)
        screen.move(field_pos[c_loc][1], field_pos[c_loc][0])

        if ttt_ar[int(c_loc[:1])][int(c_loc[1:])] == '':
            ttt_ar[int(c_loc[:1])][int(c_loc[1:])] = sym
            end = await ttt_end(ttt_ar, p)
            if p == 1:
                p = 2
            else:
                p = 1
        else:
            # print('ACTION NOT ALLOWED!')
            pass
        screen.refresh()

    if end == 1:
        screen.addstr(8, 0, 'Player 1 wins!')
    elif end == 2:
        screen.addstr(8, 0, 'Player 2 wins!')
    elif end == 3:
        screen.addstr(8, 0, 'Draw!')

async def ttt_end(ar, p):
    # Check rows
    if (ar[0][0] + ar[0][1] + ar[0][2]) in ['111','222'] or (ar[1][0] + ar[1][1] + ar[1][2]) in ['111','222'] or (ar[2][0] + ar[2][1] + ar[2][2]) in ['111','222']:
        return p

    # Check columns
    if (ar[0][0] + ar[1][0] + ar[2][0]) in ['111','222'] or (ar[0][1] + ar[1][1] + ar[2][1]) in ['111','222'] or (ar[0][2] + ar[1][2] + ar[2][2]) in ['111','222']:
        return p

    # Check diagonal
    if (ar[0][0] + ar[1][1] + ar[2][2]) in ['111','222'] or (ar[0][2] + ar[1][1] + ar[2][0]) in ['111','222']:
        return p

    # Check draw
    if '0' not in (ar[0][0] + ar[0][1] + ar[0][2] + ar[1][0] + ar[1][1] + ar[1][2] + ar[2][0] + ar[2][1] + ar[2][2]):
        return 3

    return 0

async def cursor_loc(protocol, addr_mc, screen):

    # 0,0,1 = normalzustand
    # 0,0,-1 = umgedreht
    # 0,1,0 = 90° links
    # 0,-1,0 = 90° rechts
    # -1,0,0 = 90° vorne
    # 1,0,0 = 90° hinten

    dir = 0
    cur_loc = '00'

    while dir == 0:

        # print('cur_loc =', cur_loc)
        screen.addstr(9, 0, 'READ IN...')
        screen.addstr(9, 0, '3')
        await asyncio.sleep(1)
        screen.addstr(9, 0, '2')
        await asyncio.sleep(1)
        screen.addstr(9, 0, '1')
        await asyncio.sleep(1)

        read = await read_sensor(protocol, addr_mc, '/saul/mma8x5x/SENSE_ACCEL')
        read = str(read)

        read = read[read.find('"d":')+5 : read.find(']')]

        # print('READ SUCCESSFUL:', read)

        x,y,z = read.split(',')

        # print('x:', x, '; y:', y, '; z:', z)

        x = float(x)
        y = float(y)
        z = float(z)

        # Normalzustand
        if x < 0.5 and y < 0.5 and z > 0.5:
            # print('No Direction!')

        # Links
        if x < 0.5 and y > 0.5 and z < 0.5:
            cur_loc = await add_dir(cur_loc, 1)

        # Rechts
        if x < 0.5 and y < -0.5 and z < 0.5:
            cur_loc = await add_dir(cur_loc, 2)

        # Oben
        if x > 0.5 and y < 0.5 and z < 0.5:
            cur_loc = await add_dir(cur_loc, 3)

        # Unten
        if x < -0.5 and y < 0.5 and z < 0.5:
            cur_loc = await add_dir(cur_loc, 4)

        # Umgedreht
        if x < 0.5 and y < 0.5 and z < -0.5:
            return cur_loc

async def add_dir(cur_loc, dir):
    x = int(cur_loc[:1])
    y = int(cur_loc[1:])

    if   dir == 1 : y = y - 1  # Links
    elif dir == 2 : y = y + 1  # Rechts
    elif dir == 3 : x = x - 1  # Oben
    elif dir == 4 : x = x + 1  # Unten

    if x == -1 : x = 2
    if x == 3  : x = 0

    if y == -1 : y = 2
    if y == 3  : y = 0

    return str(x) + str(y)


async def main():
    protocol = await Context.create_client_context()

    addr_mc_ar = await get_addr(protocol)
    # print(addr_mc_ar)

    addr_mc = addr_mc_ar[0]

    #sensor_array = await get_sensors(protocol, addr_mc)

    await read_sensor(protocol, addr_mc, '/saul/mma8x5x/SENSE_ACCEL')

    await tictactoe(protocol, addr_mc)

    await protocol.shutdown()


if __name__ == '__main__':
    asyncio.run(main())

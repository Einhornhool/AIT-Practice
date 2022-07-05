# from asciimatics.screen import Screen, ManagedScreen
# from time import sleep

# class TestScreen(Screen):
#     def __init__(self):
#         super(TestScreen, self).__init__()

# def demo(screen: Screen=None):
#     screen.print_at('Hello World', 0, 0)
#     screen.refresh()
#     sleep(5)

# TestScreen.wrapper(demo)

import curses
from time import sleep
from aiocoap import *
import asyncio
from curses import wrapper
import ttt_game

ttt_ar = [  ['','',''],
            ['','',''],
            ['','','']]

# curser_loc = '00'

# player = 1

cur_loc = '00'

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
async def cursor_loc(protocol, addr_mc, screen, player):

    # 0,0,1 = normalzustand
    # 0,0,-1 = umgedreht
    # 0,1,0 = 90° links
    # 0,-1,0 = 90° rechts
    # -1,0,0 = 90° vorne
    # 1,0,0 = 90° hinten

    dir = 0
    cur_loc = '00'
    direction = 'No Direction'

    while dir == 0:
        screen.move(10, 0)
        screen.clrtoeol()
        screen.move(9, 0)
        screen.clrtoeol()

        screen.addstr(0, 0, playing_field)
        screen.addstr(8, 0, f'Player: {player}')
        screen.addstr(10, 0, f'Direction: {direction}')
        screen.move(field_pos[cur_loc][0], field_pos[cur_loc][1])

        # print('cur_loc =', cur_loc)
        screen.addstr(9, 0, 'READ IN...')
        screen.addstr(9, 12, '3')
        screen.move(field_pos[cur_loc][0], field_pos[cur_loc][1])
        screen.refresh()
        await asyncio.sleep(1)
        screen.addstr(9, 12, '2')
        screen.move(field_pos[cur_loc][0], field_pos[cur_loc][1])
        screen.refresh()
        await asyncio.sleep(1)
        screen.addstr(9, 12, '1')
        screen.move(field_pos[cur_loc][0], field_pos[cur_loc][1])
        screen.refresh()
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
            direction = 'No Direction!'

        # Links
        if x < 0.5 and y > 0.5 and z < 0.5:
            cur_loc = add_dir(cur_loc, 1)
            direction = 'Left!'

        # Rechts
        if x < 0.5 and y < -0.5 and z < 0.5:
            cur_loc = add_dir(cur_loc, 2)
            direction = 'Right!'

        # Oben
        if x > 0.5 and y < 0.5 and z < 0.5:
            cur_loc = add_dir(cur_loc, 3)
            direction = 'Up!'

        # Unten
        if x < -0.5 and y < 0.5 and z < 0.5:
            cur_loc = add_dir(cur_loc, 4)
            direction = 'Down!'
        screen.refresh()

        # Umgedreht
        if x < 0.5 and y < 0.5 and z < -0.5:
            return cur_loc

def add_dir(cur_loc, dir):
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

async def ttt_end(ar, p):
    # Check rows
    if (ar[0][0] + ar[0][1] + ar[0][2]) in ['XXX','OOO'] or (ar[1][0] + ar[1][1] + ar[1][2]) in ['XXX','OOO'] or (ar[2][0] + ar[2][1] + ar[2][2]) in ['XXX','OOO']:
        return p

    # Check columns
    if (ar[0][0] + ar[1][0] + ar[2][0]) in ['XXX','OOO'] or (ar[0][1] + ar[1][1] + ar[2][1]) in ['XXX','OOO'] or (ar[0][2] + ar[1][2] + ar[2][2]) in ['XXX','OOO']:
        return p

    # Check diagonal
    if (ar[0][0] + ar[1][1] + ar[2][2]) in ['XXX','OOO'] or (ar[0][2] + ar[1][1] + ar[2][0]) in ['XXX','OOO']:
        return p

    # Check draw
    if len((ar[0][0] + ar[0][1] + ar[0][2] + ar[1][0] + ar[1][1] + ar[1][2] + ar[2][0] + ar[2][1] + ar[2][2])) == 9:
        return 3

    return 0

async def tictactoe(protocol, addr_mc, screen):
    end = 0
    p = 1
    sym = 'X' if p == 1 else 'O'

    while end == 0:
        screen.addstr(0, 0, playing_field)

        for k in field_pos.keys():
            screen.addstr(field_pos[k][0], field_pos[k][1], f'{ttt_ar[int(k[0])][int(k[1])]}')

        screen.move(field_pos[cur_loc][0], field_pos[cur_loc][1])
        screen.addstr(8, 0, f'Player: {p}')
        screen.refresh()

        set_loc = '00'
        set_loc = await cursor_loc(protocol, addr_mc, screen, p)

        if ttt_ar[int(set_loc[:1])][int(set_loc[1:])] == '':
            ttt_ar[int(set_loc[:1])][int(set_loc[1:])] = sym
            end = await ttt_end(ttt_ar, p)
            screen.addstr(21, 0, f'End {end}')
            screen.refresh()
            await asyncio.sleep(3)
            if p == 1:
                p = 2
            else:
                p = 1
        else:
            screen.addstr(11, 0, 'ACTION NOT ALLOWED!')
            await asyncio.sleep(3)
        screen.refresh()

    if end == 1:
        screen.addstr(9, 0, 'Player 1 wins!')
    elif end == 2:
        screen.addstr(9, 0, 'Player 2 wins!')
    elif end == 3:
        screen.addstr(9, 0, 'Draw!')
    screen.refresh()

async def read_sensor(protocol, addr, sensor):
    response = await protocol.request(Message(code=GET, uri=addr + sensor)).response
    return response.payload

async def get_addr(protocol):
    addr = "coap://[2001:67c:254:b0b2:affe:4000:0:1]/"
    response = await protocol.request(Message(code=GET, uri=addr + "endpoint-lookup/")).response

    resp_str = str(response.payload)

    addr_mc = []
    for splitted in resp_str.split('base="'):
        if splitted[:4] == 'coap':
            addr_mc.append(splitted[:splitted.find('"')])

    return addr_mc

async def ttt_main(screen):
    protocol = await Context.create_client_context()
    addr_mc_ar = await get_addr(protocol)
    addr_mc = addr_mc_ar[0]

    await read_sensor(protocol, addr_mc, '/saul/mma8x5x/SENSE_ACCEL')

    await tictactoe(protocol, addr_mc, screen)
    # screen.clear()

    # while True:
    #     screen.addstr(0, 0, playing_field)
    #     for p in field_pos.keys():
    #         screen.addstr(field_pos[p][0], field_pos[p][1], f'{ttt_array[int(p[0])][int(p[1])]}')
    #         screen.move(field_pos[curser_loc][0], field_pos[curser_loc][1])
    #     screen.refresh()

def main(screen):
    return asyncio.run(ttt_main(screen))

if __name__ == '__main__':
    wrapper(main)
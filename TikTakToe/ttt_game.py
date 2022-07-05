import curses
from time import sleep
from aiocoap import *
import asyncio
from curses import wrapper
#import ttt_sc_test

ttt_ar = [  ['','',''],
            ['','',''],
            ['','','']]

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

    cur_loc = '00'
    direction = '             '

    while True:
        # update screen
        screen.addstr(0, 0, playing_field)
        screen.addstr(8, 0, f'Player: {player}')
        screen.addstr(10, 0, f'Direction: {direction}')
        #screen.addstr(20, 0, f'ttt_ar: {ttt_ar}')
        screen.move(field_pos[cur_loc][0], field_pos[cur_loc][1])

        # set X and O
        for k in field_pos.keys():
            screen.addstr(field_pos[k][0], field_pos[k][1], f'{ttt_ar[int(k[0])][int(k[1])]}')

        # 3, 2, 1 - Counter
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

        # read sensor
        read = await read_sensor(protocol, addr_mc, '/saul/mma8x5x/SENSE_ACCEL')
        read = str(read)

        read = read[read.find('"d":')+5 : read.find(']')]

        x,y,z = read.split(',')

        x = float(x)
        y = float(y)
        z = float(z)

        # 0,0,1 = normalzustand
        # 0,0,-1 = umgedreht
        # 0,1,0 = 90° links
        # 0,-1,0 = 90° rechts
        # -1,0,0 = 90° vorne
        # 1,0,0 = 90° hinten

        # Normalzustand
        if x < 0.5 and y < 0.5 and z > 0.5:
            direction = 'No Direction!'

        # Links
        if x < 0.5 and y > 0.5 and z < 0.5:
            cur_loc = add_dir(cur_loc, 1)
            direction = 'Left!        '

        # Rechts
        if x < 0.5 and y < -0.5 and z < 0.5:
            cur_loc = add_dir(cur_loc, 2)
            direction = 'Right!       '

        # Oben
        if x > 0.5 and y < 0.5 and z < 0.5:
            cur_loc = add_dir(cur_loc, 3)
            direction = 'Up!          '

        # Unten
        if x < -0.5 and y < 0.5 and z < 0.5:
            cur_loc = add_dir(cur_loc, 4)
            direction = 'Down!        '

        # set direction and clear 'Action not allowed!'
        screen.addstr(11, 0, '                   ')
        screen.refresh()

        # while-escape
        # Umgedreht
        if x < 0.5 and y < 0.5 and z < -0.5:
            direction = 'Click!       '
            screen.addstr(10, 0, f'Direction: {direction}')
            screen.refresh()
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

async def tictactoe(protocol, mc_p1, mc_p2, screen):
    end = 0
    p = 1
    sym = 'X'
    active_mc = mc_p1

    while end == 0:

        set_loc = await cursor_loc(protocol, active_mc, screen, p)

        if ttt_ar[int(set_loc[:1])][int(set_loc[1:])] == '':
            ttt_ar[int(set_loc[:1])][int(set_loc[1:])] = sym
            end = await ttt_end(ttt_ar, p)
            if p == 1:
                p = 2
                sym = 'O'
                active_mc = mc_p2

            else:
                p = 1
                sym = 'X'
                active_mc = mc_p1

        else:
            screen.addstr(11, 0, 'ACTION NOT ALLOWED!')

    for k in field_pos.keys():
        screen.addstr(field_pos[k][0], field_pos[k][1], f'{ttt_ar[int(k[0])][int(k[1])]}')

    if end == 1:
        screen.addstr(9, 0, 'Player 1 wins!    ')
    elif end == 2:
        screen.addstr(9, 0, 'Player 2 wins!    ')
    elif end == 3:
        screen.addstr(9, 0, 'Draw!             ')
    screen.refresh()
    await asyncio.sleep(5)

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

async def player_led(protocol, addr, player):
    led_list = ['/saul/LED(blue)/ACT_SWITCH', '/saul/LED(green)/ACT_SWITCH', '/saul/LED(red)/ACT_SWITCH']
    if player == '1':
        # Red on
        payload = bytes(str(1), 'ascii')
        request = Message(code=PUT, payload=payload, uri=str(addr + led_list[2]))
        response = await protocol.request(request).response

        # Others off
        payload = bytes(str(0), 'ascii')
        request = Message(code=PUT, payload=payload, uri=str(addr + led_list[0]))
        response = await protocol.request(request).response
        request = Message(code=PUT, payload=payload, uri=str(addr + led_list[1]))
        response = await protocol.request(request).response

    elif player == '2':
        # Green on
        payload = bytes(str(1), 'ascii')
        request = Message(code=PUT, payload=payload, uri=str(addr + led_list[1]))
        response = await protocol.request(request).response

        # Others off
        payload = bytes(str(0), 'ascii')
        request = Message(code=PUT, payload=payload, uri=str(addr + led_list[0]))
        response = await protocol.request(request).response
        request = Message(code=PUT, payload=payload, uri=str(addr + led_list[2]))
        response = await protocol.request(request).response

async def ttt_main(screen):

    screen.addstr(2, 0, 'Initializing!')
    screen.addstr(13, 0, 'Player 1: RED!')
    screen.addstr(14, 0, 'Player 2: GREEN!')
    screen.refresh()

    protocol = await Context.create_client_context()
    addr_mc_ar = await get_addr(protocol)

    mc_p1 = addr_mc_ar[0]
    mc_p2 = addr_mc_ar[1]

    await player_led(protocol, mc_p1, '1')
    await player_led(protocol, mc_p2, '2')

    await tictactoe(protocol, mc_p1, mc_p2, screen)

    await protocol.shutdown()


def main(screen):
    return asyncio.run(ttt_main(screen))

if __name__ == '__main__':
    wrapper(main)
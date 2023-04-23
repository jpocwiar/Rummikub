import random
from dataclasses import dataclass
import xml.etree.ElementTree as ET

import socketio
import argparse
from aiohttp import web

parser = argparse.ArgumentParser()
parser.add_argument('--players', type=int, default=4, help='number of players')
args = parser.parse_args()

game_states = {
    'waiting': 'WAITING',
    'ongoing': 'ONGOING',
    'ended': 'ENDED'
}

state = {
    'xml': '',
    'state': game_states['waiting'],
    'players': [],
    'current_player': {
        'no': 0,
        'sid': None
    },
    'sids': []
}

connected_players = []

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)

async def index(request):
    with open('index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')

def init_xml():
    @dataclass
    class Player:
        no: int
        hand: list
    def init_bag():
        bag = []
        for _ in range(0, 2):
            for value in range(1, 13 + 1):
                for color in range(1, 4 + 1):
                    tile = f'{color},{value}'
                    bag.append(tile)
            bag.append(f'{0},{0}') #jokers
        random.shuffle(bag)
        return bag
    def draw_tiles(bag):
        draws = bag[:14]
        bag = bag[14:]
        return draws, bag
    def init_players(bag):
        players = []
        for i in range(len(connected_players)):
            tiles, bag = draw_tiles(bag)
            players.append(tiles)
        return players, bag
    def create_xml(bag, players):
        turn_root = ET.Element('turn')

        # bag
        bag_element = ET.SubElement(turn_root, 'bag')
        for tile in bag:
            tile_element = ET.SubElement(bag_element, 'tile')
            tile_element.text = tile

        # board
        board_element = ET.SubElement(turn_root, 'board')
        # players
        for player in players:
            player_element = ET.SubElement(turn_root, 'player')
            player_element.set('first_move', str(True))
            for tile in player:
                tile_element = ET.SubElement(player_element, 'tile')
                tile_element.text = tile

        tree = ET.ElementTree(turn_root)
        xml_string = ET.tostring(tree.getroot()).decode()
        return xml_string

    bag = init_bag()
    players, bag = init_players(bag)
    xml = create_xml(bag, players)
    return xml

@sio.event
async def connect(sid, environ):
    ip = environ['REMOTE_ADDR'].split(':')[-1]
    port = environ['REMOTE_PORT']

    print(f"connection established {ip}:{port}")

    if len(connected_players) == 0:
        state['current_player']['sid'] = sid

    if len(connected_players) >= args.players:
        await sio.disconnect(sid=sid)
    else:
        connected_players.append({
            'sid': sid,
            'nickname': '',
            'ip': ip
        })
        state['players'].append(f'player-{sid}')
        state['sids'].append(sid)

    await sio.emit('receive state', state)

@sio.on('setnickname')
async def set_nickname(sid, nickname):
    if state['state'] == game_states['waiting']:
        for i, player in enumerate(connected_players):
            if player['sid'] == sid:
                player['nickname'] = nickname
                state['players'][i] = nickname
        await sio.emit('receivestate', state)

@sio.on('sendstate')
async def send_state(sid, xml):
    if state['state'] == game_states['ongoing'] and state['current_player']['sid'] == sid:
        next_id = (state['current_player']['no'] + 1) % len(connected_players)
        state['current_player']['no'] = next_id
        next_player = connected_players[next_id]
        state['current_player']['sid'] = next_player['sid']

        state['xml'] = xml
        await sio.emit('receivestate', state)

@sio.on('startgame')
async def start_game(sid):
    if state['state'] == game_states['waiting']:
        state['xml'] = init_xml()
        state['state'] = game_states['ongoing']

        await sio.emit('receivestate', state)

@sio.on('whoami')
async def whoami(sid):
    await sio.emit('whoami', data=sid, to=sid)

@sio.event
async def disconnect(sid):
    player = [item for item in connected_players if item["sid"] == sid][0]

    print(f"client disconnected {player['ip']}")

    index_to_remove = connected_players.index(player)
    connected_players.remove(player)

    state['players'].pop(index_to_remove)
    state['sids'].pop(index_to_remove)

app.router.add_get('/', index)

web.run_app(app, port=50000)
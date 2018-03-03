import bottle
import os
import random
import config
import build_board
# import json


@bottle.route('/')
def static():
    return "the server is running"


@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.post('/start')
def start():
    data = bottle.request.json
    game_id = data.get('game_id')
    board_width = data.get('width')
    board_height = data.get('height')

    config.board_width = board_width
    config.board_height = board_height

    head_url = '%s://%s/static/head.png' % (
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc
    )

    # TODO: Do things with data

    return {
        'color': '#00FF00',
        'taunt': '{} ({}x{})'.format(game_id, board_width, board_height),
        'head_url': head_url
    }

@bottle.post('/move')
def move():
    data = bottle.request.json
    board_dims = get_board_dims()
    height = board_dims[0]
    width = board_dims[1]

    board = build_board.build_board(data, height, width)
    stringified_board = str(board)

    snake_positions = build_board.build_snake_positions(data)
    stringified_snake_positions = str(snake_positions)

    directions = ['up', 'down', 'left', 'right']
    direction = random.choice(directions)
    print direction
    return {
        'move': direction,
        'taunt': stringified_board
    }

def get_board_dims():
    board_height = config.board_height
    board_width = config.board_width
    return [board_height, board_width]

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
snake_ip = config.snake_ip

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', snake_ip),
        port=os.getenv('PORT', '8080'),
        debug = True)

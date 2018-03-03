import bottle
import os
import random



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
    height = data['height']
    width = data['width']
    directions = ['up', 'down', 'left', 'right']
    ourSnak = {}

    for snake in data['snakes']['data']:
        if snake['name'] == 'JSTMNA':
            ourSnak = snake

    parts = ourSnak['body']['data']
    xhead = parts[0]['x']
    yhead = parts[0]['y']

    close_food = find_close_food(data,xhead, yhead)
    dirr = find_food(close_food,xhead,yhead,directions)
    nextdirrxy = find_next(dirr,xhead,yhead)
    danger = danger_zone(data,nextdirrxy,height,width)
    print(danger)
    if danger:
        dirr = choose_next_dirr(dirr,directions,xhead,yhead,data,height,width)



    return {
        'move': dirr,
        'taunt': 'battlesnake-python!'
    }

def choose_next_dirr(dirr,directions,xhead,yhead,data,height,width):
    for move in directions:
        nextdirrxy = find_next(move,xhead,yhead)
        if not danger_zone(data,nextdirrxy,height,width):
            return move
        else:
            continue
    return dirr

def danger_zone(data,nextdirr,height,width):
    snakes = data['snakes']
    for snake in snakes['data']:
        body = snake['body']['data']
        for part in body:
            if part['x'] == nextdirr[0]:
                return True
            if part['y'] == nextdirr[1]:
                return True
    if nextdirr[0] == width or nextdirr[0]==-1:
        return True
    if nextdirr[1] == height or nextdirr[1]==-1:
        return True
    return False

def find_next(dirr,xhead,yhead):
    if dirr == 'up':
        return [xhead,yhead-1]
    if dirr == 'down':
        return [xhead,yhead+1]
    if dirr == 'right':
        return [xhead+1,yhead]
    if dirr == 'left':
        return [xhead-1,yhead]

def find_food(close_food,xhead,yhead,directions):
    closeFoodx = close_food[0]
    closeFoody = close_food[1]
    movx = closeFoodx-xhead
    movy = closeFoody-yhead
    if movx !=0:
        if movx>0:
            return directions[3]
        elif movx<0:
            return directions[2]
    if movy !=0:
        if movy>0:
            return directions[1]
        elif movy<0:
            return directions[0]
    return directions[1]



def find_close_food(data,xhead,yhead):
    food = data['food']
    closeFoodDist = 1000
    closeFoodx = 0
    closeFoody = 0
    for foodbits in food['data']:
        foodx = foodbits['x']
        foody = foodbits['y']
        dist = abs(xhead-foodx) + abs(yhead-foody)
        if dist < closeFoodDist:
            closeFoodDist = dist
            closeFoodx =foodbits['x']
            closeFoody = foodbits['y']
    return (closeFoodx,closeFoody)

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()


if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '172.20.10.2'),
        port=os.getenv('PORT', '8080'),
        debug = True)

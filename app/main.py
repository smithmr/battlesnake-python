import bottle
import os
import random
import operator
tail_postition ={}

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
        'color': '#0B83B6',
        'taunt': 'sluts',
        'head_url': head_url
    }


@bottle.post('/move')
def move():
    data = bottle.request.json
    height = data['height']
    width = data['width']
    directions = ['up', 'down', 'left', 'right']
    ourSnak = data['you']

    parts = ourSnak['body']['data']
    xhead = parts[0]['x']
    yhead = parts[0]['y']

    snake_length = ourSnak['length']
    xtail = parts[snake_length-1]['x']
    ytail = parts[snake_length-1]['y']
    tail = (xtail, ytail)
    weaker_snake = find_weaker_snake_head(data, snake_length)
    close_food = find_close_food(data,xhead, yhead)
    taunt = "what to do?"
    if (ourSnak['health'] < 25 or ourSnak['length']<10 ):
        dirr = find_food(close_food,xhead,yhead,directions)
        taunt = "eat fooooooood!"
    elif (weaker_snake[0]!=False):
        dirr = find_food(weaker_snake, xhead,yhead,directions)
        taunt ="KILL KILLL KILLLLLLL"
    else:
        dirr = find_food(tail, xhead,yhead,directions)
        taunt = "chase tail...."

    nextdirrxy = find_next(dirr,xhead,yhead)
    danger = danger_zone(data,nextdirrxy,height,width,tail)
    if danger:
        taunt ='danger'
        count_up = flood_fill(data,directions[0],xhead,yhead,height,width,tail)
        print(count_up)
        count_down = flood_fill(data,directions[1],xhead,yhead,height,width,tail)
        print(count_down)
        count_left = flood_fill(data,directions[2],xhead,yhead,height,width,tail)
        print(count_left)
        count_right = flood_fill(data,directions[3],xhead,yhead,height,width,tail)
        print(count_right)
        counts = {'up':count_up,'down':count_down,'left':count_left,'right':count_right}
        dirr = max(counts.iteritems(), key=operator.itemgetter(1))[0]
        print(dirr)
    return {
        'move': dirr,
        'taunt': taunt
    }

def flood_fill(data, dirr, xhead, yhead, height, width,tail):
    directions = ['up', 'down', 'left', 'right']
    next_dirr = find_next(dirr,xhead,yhead)
    count = 0
    while (danger_zone(data, next_dirr,height, width,tail)!=True):
        count = count+1
        dirr = choose_next_dirr(dirr, directions, next_dirr[0],next_dirr[1], data, height, width,tail)
        next_dirr = find_next(dirr,next_dirr[0], next_dirr[1])
        if count>10:
            break
    return count

def follow_tail(tail,xhead,yhead,directions):
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

def choose_next_dirr(dirr,directions,xhead,yhead,data,height,width,tail):
    for move in directions:
        nextdirrxy = find_next(move,xhead,yhead)
        if not danger_zone(data,nextdirrxy,height,width,tail):
            return move
        else:
            continue
    return dirr

def danger_zone(data,nextdirr,height,width, tail):
    snakes = data['snakes']
    for snake in snakes['data']:
        body = snake['body']['data']
        for part in body:
            if part['x'] == tail[0] and part['y'] == tail[1]:
                break
            if part['x'] == nextdirr[0] and part['y']==nextdirr[1]:
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

def find_weaker_snake_head(data, our_snek_len):
    our_snek = data['you']

    our_snek_id = our_snek['id']
    closeSnakex = False
    closeSnakey = False
    snakes = data['snakes']['data']
    for snake in snakes:
        head = snake['body']['data'][0]
        if snake['length'] < our_snek_len:
            closeSnakex = head['x']
            closeSnakey = head['y']
            return (closeSnakex,closeSnakey)

    return (closeSnakex,closeSnakey)

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
        host=os.getenv('IP', '192.168.1.111'),
        port=os.getenv('PORT', '8080'),
        debug = True)

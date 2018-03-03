
def build_board(data, board_height, board_width):
    board = {}
    snake_positions = build_snake_positions(data)
    food_positions = build_food_positions(data)
    positions = merge_two_dicts(food_positions, snake_positions)

    for row in range(0,board_height):
        for col in range(0,board_width):
            pos = (row,col)
            if pos in positions:
                board[pos] = positions[pos]
            else:
                board[pos] = 0

    return board

def build_snake_positions(data):
    snakes = data['snakes']['data']
    snake_positions = {}
    for snake in snakes:
        body_parts = snake['body']['data']
        for part in body_parts:
            snake_positions[(part['x'], part['y'])] = 1;

    return snake_positions

def build_food_positions(data):
    foods = data['food']['data']
    food_positions = {}
    for food in foods:
        food_positions[(food['x'], food['y'])] = 3;

    return food_positions

def merge_two_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z

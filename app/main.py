import bottle
import os

from heapq import heappush, heappop
import math

HEAD_URL = "CoffeeBean.jpg"
SNAKE_ID = "c057977b-3428-4a38-a453-e5f2cb644eaa"
SNAKE_COLOR = "#4d2800"
SNAKE_TAUNT = "MMMMM Coffee"

PREVIOUS = 0

class MapSize:
    x = 0
    y = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y

class Tile:
    x = 0
    y = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y


class Node:
    xPos = 0 # x position
    yPos = 0 # y position
    distance = 0 # total distance already travelled to reach the node
    priority = 0 # priority = distance + remaining distance estimate

    def __init__(self, xPos, yPos, distance, priority):
        self.xPos = xPos
        self.yPos = yPos
        self.distance = distance
        self.priority = priority
    def __lt__(self, other): # comparison method for priority queue
        return self.priority < other.priority
    def updatePriority(self, xDest, yDest):
        self.priority = self.distance + self.estimate(xDest, yDest) * 10 # A*
    # give higher priority to going straight instead of diagonally
    def nextMove(self, dirs, d): # d: direction to move
        if dirs == 8 and d % 2 != 0:
            self.distance += 14
        else:
            self.distance += 10
    # Estimation function for the remaining distance to the goal.
    def estimate(self, xDest, yDest):
        xd = xDest - self.xPos
        yd = yDest - self.yPos
        # Euclidian Distance
        d = math.sqrt(xd * xd + yd * yd)
        # Manhattan distance
        # d = abs(xd) + abs(yd)
        # Chebyshev distance
        # d = max(abs(xd), abs(yd))
        return(d)


# A-star algorithm.
# The path returned will be a string of digits of directions.
def pathFind(the_map, mapWidth, mapHeight, headX, headY, goalX, goalY):
    # Possible movement directions
    dirs = 4
    dir_map = []

    # ?
    dx = [1, 0, -1, 0]
    dy = [0, 1, 0, -1]

    # Closed (tried-out) nodes
    closed_nodes_map = []

    # Open (not-yet-tried) nodes
    open_nodes_map = []

    # Build an empty 2D to track open/closed nodes
    row = [0] * mapWidth
    for i in range(mapHeight):
        closed_nodes_map.append(list(row))
        open_nodes_map.append(list(row))
        dir_map.append(list(row))

    pq = [[], []] # priority queues of open (not-yet-tried) nodes
    pqi = 0 # priority queue index

    # create the start node and push into list of open nodes
    n0 = Node(headX, headY, 0, 0)
    n0.updatePriority(goalX, goalY)
    heappush(pq[pqi], n0)
    open_nodes_map[headY][headX] = n0.priority # mark it on the open nodes map

    # A* search
    while len(pq[pqi]) > 0:
        # get the current node w/ the highest priority
        # from the list of open nodes
        n1 = pq[pqi][0] # top node
        n0 = Node(n1.xPos, n1.yPos, n1.distance, n1.priority)
        x = n0.xPos
        y = n0.yPos
        heappop(pq[pqi]) # remove the node from the open list
        open_nodes_map[y][x] = 0
        closed_nodes_map[y][x] = 1 # mark it on the closed nodes map

        # quit searching when the goal is reached
        # if n0.estimate(xB, yB) == 0:
        if x == goalX and y == goalY:
            # generate the path from finish to start
            # by following the dirs
            path = ''
            while not (x == headX and y == headY):
                j = dir_map[y][x]
                c = str((j + dirs / 2) % dirs)
                path = c + path
                x += dx[j]
                y += dy[j]
            return path

        # generate moves (child nodes) in all possible dirs
        for i in range(dirs):
            xdx = x + dx[i]
            ydy = y + dy[i]
            if not (xdx < 0 or xdx > mapWidth-1 or ydy < 0 or ydy > mapHeight - 1
                    or the_map[ydy][xdx] == 1 or closed_nodes_map[ydy][xdx] == 1):
                # generate a child node
                m0 = Node(xdx, ydy, n0.distance, n0.priority)
                m0.nextMove(dirs, i)
                m0.updatePriority(goalX, goalY)
                # if it is not in the open list then add into that
                if open_nodes_map[ydy][xdx] == 0:
                    open_nodes_map[ydy][xdx] = m0.priority
                    heappush(pq[pqi], m0)
                    # mark its parent node direction
                    dir_map[ydy][xdx] = (i + dirs / 2) % dirs
                elif open_nodes_map[ydy][xdx] > m0.priority:
                    # update the priority
                    open_nodes_map[ydy][xdx] = m0.priority
                    # update the parent direction
                    dir_map[ydy][xdx] = (i + dirs / 2) % dirs
                    # replace the node
                    # by emptying one pq to the other one
                    # except the node to be replaced will be ignored
                    # and the new node will be pushed in instead
                    while not (pq[pqi][0].xPos == xdx and pq[pqi][0].yPos == ydy):
                        heappush(pq[1 - pqi], pq[pqi][0])
                        heappop(pq[pqi])
                    heappop(pq[pqi]) # remove the target node
                    # empty the larger size priority queue to the smaller one
                    if len(pq[pqi]) > len(pq[1 - pqi]):
                        pqi = 1 - pqi
                    while len(pq[pqi]) > 0:
                        heappush(pq[1-pqi], pq[pqi][0])
                        heappop(pq[pqi])
                    pqi = 1 - pqi
                    heappush(pq[pqi], m0) # add the better node instead
    return '' # if no route found

def buildMap(pData):
    data = pData

    n = data["width"] # horizontal size of the map
    m = data["height"] # vertical size of the map


    the_map = []
    row = [0] * n
    for i in range(m): # create empty map
        the_map.append(list(row))
    for x in range(n):
        the_map[x][0] = 1
        the_map[x][m-1] = 1
    for y in range(m):
        the_map[0][y] = 1
        the_map[n-1][y] = 1

    for snake in data.get("snakes"):
        for piece in snake.get("coords"):
            the_map[piece[0]][piece[1]] = 1

    if "walls" in data:
        for wall in data["walls"]:
            the_map[wall[0]][wall[1]] = 1

    return the_map, [n, m]

def findPath(pHead, pNode, the_map, map_size):
    # Basically just run aStar
    return pathFind(the_map, map_size[0], map_size[1], pHead.x, pHead.y, pNode.x, pNode.y)

def findOurSnake(snakes):
    global SNAKE_ID

    for snake in snakes:
        if snake.get("id") == SNAKE_ID:
            return snake

@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.get('/')
def index():
    global SNAKE_COLOR, HEAD_URL

    head_url = '%s://%s/static/%s' % (
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc,
        HEAD_URL
    )

    return {
        'color': SNAKE_COLOR,
        'head': head_url
    }


@bottle.post('/start')
def start():
    global SNAKE_TAUNT
    data = bottle.request.json

    return {
        'taunt': SNAKE_TAUNT
    }


@bottle.post('/move')
def move():

    data = bottle.request.json
    global PREVIOUS

    Move = (PREVIOUS + 1) % 4
    PREVIOUS = Move
    print PREVIOUS

    #if data.get("health") < 20:



    our_move = "default"
    if Move == 0:
     our_move = "east"
    elif Move == 1:
     our_move = "south"
    elif Move == 2:
     our_move = "west"
    elif Move == 3:
     our_move = "north"

    return {
        'move': our_move,
        'taunt': 'COFFEEEEEEE'
    }

#     data = bottle.request.json
#
#     map, map_size = buildMap(data)
#
#     map_width = data.get("width")
#     map_height = data.get("height")
#
#     snakes = data.get("snakes")
#
#     our_snake = findOurSnake(snakes)
#     our_snake_head = Tile(our_snake.get("coords")[0][0], our_snake.get("coords")[0][1])
#     other_snakes = snakes
#     other_snakes.remove(our_snake)
#
#     # Parse data for list of coin/food tiles
#     foodTiles = list()
#     coinTiles = list()
#
#     for food in data.get("food"):
#         foodTiles.append(Tile(food[0], food[1]))
#     if "gold" in data:
#         for coin in data["gold"]:
#             coinTiles.append(Tile(coin[0], coin[1]))
#
#     path = list()
#
#     # Choose a strategy
#     print "Choosing a strategy:"
#     if True:
#         print "Health"
#
#         path = findPath(our_snake_head, foodTiles[0], map, map_size)
#
#         # best_our_food_path = list()
#         # best_opponent_food_cost = 1000
#         #
#         # for food in foodTiles:
#         #     our_path_current_food = findPath(our_snake_head, food, map, map_size)
#         #
#         #     best_opponent_cost = 1000
#         #
#         #     for snake in other_snakes:
#         #         # find their cost to food
#         #         their_path = findPath(Tile(snake.get("coords")[0][0], snake.get("coords")[0][1]), food, map, map_size)
#         #         # If their cost - our cost < previous best, set that food as target
#         #         if len(their_path) - len(our_path_current_food) < best_opponent_food_cost:
#         #             best_opponent_food_cost = len(their_path)
#         #
#         #     if best_opponent_cost < best_opponent_food_cost:
#         #         best_our_food_path = our_path_current_food
#         #         best_opponent_food_cost = best_opponent_cost
#         #
#         # path = best_our_food_path
#
#     elif len(coinTiles) > 0:
#         print "Coins"
#
#         best_our_coin_path = list()
#         best_opponent_coin_cost = 1000
#
#         for coin in coinTiles:
#             our_path_current_coin = findPath(our_snake_head, coin, map, map_size)
#
#             best_opponent_cost = 1000
#
#             for snake in other_snakes:
#                 # find their cost to coin
#                 their_path = findPath(Tile(snake.get("coords")[0][0], snake.get("coords")[0][1]), coin, map, map_size)
#                 # If their cost - our cost < previous best, set that coin as target
#                 if len(their_path) - len(our_path_current_coin) < best_opponent_coin_cost:
#                     best_opponent_coin_cost = len(their_path)
#
#             if best_opponent_cost < best_opponent_coin_cost:
#                 best_our_coin_path = our_path_current_coin
#                 best_opponent_coin_cost = best_opponent_cost
#
#         path = best_our_coin_path
#     else:
#         print "Walls"
#         goal = Tile(2, 2)
#         head = our_snake.get("coords")[0]
#         head_tile = Tile(head[0], head[1])
#
#         if head == [2, 2]:
#             goal = Tile(map_width -1, 2)
#         elif head == [map_width -1, 2]:
#             goal = Tile(map_width -1, map_height -1)
#         elif head == [map_width-1, map_height -1]:
#             goal = Tile(2, map_height -1)
#         elif head == [2, map_height-1]:
#             goal = Tile(2, 2)
#
#
#         print "Goal: " + str(goal.x) + ", " + str(goal.y)
#
#         path = findPath(head_tile, goal, map, map_size)
#
#         # Find closest edge and go in that direction
#         # If against wall, turn to nearest corner
#         # if in corner keep following wall
#
#     head = our_snake.get("coords")[0]
#
#     # Figure out required move to get to goal
#     Move = path[-1]
#     neck = our_snake.get("coords")[1]
#     if(neck[0] > head[0] and Move == "0"):
#         Move = 1
#     if(neck[1] > head[1] and Move == "1"):
#         Move = 0
#     if(neck[1] < head[1] and Move == "3"):
#         Move = 0
#     if(neck[0] < head[0] and Move == "2"):
#         Move = 1
#
#     tempHead = list(head)
#     if Move == 1:
#         tempHead[1] = head[1] + 1
#     if Move == 0:
#         tempHead[0] = head[0] + 1
#     if Move == 2:
#         tempHead[0] = head[0] - 1
#     if Move == 3:
#         tempHead[1] = head[1] - 1
#
#     """if map[tempHead[0]][tempHead[1]] == 1:
#         Move += 1
#         Move % 4
# """
#     our_move = "default"
#     if Move == "1":
#         our_move = "south"
#     elif Move == "0":
#         our_move = "east"
#     elif Move == "2":
#         our_move = "west"
#     elif Move == "3":
#         our_move = "north"
#
#
#
#
#     return {
#         'move': our_move,
#         'taunt': 'battlesnake-python!'
#     }


@bottle.post('/end')
def end():
    data = bottle.request.json

    # TODO: Do things with data

    return {
        'taunt': 'battlesnake-python!'
    }


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))

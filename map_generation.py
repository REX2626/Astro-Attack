import random

size = (20, 20)

row = []
last_row = None

map = []

seed = int(input())
if seed == 0:
    seed = random.randint(1, 1000000)

count = 0

def check_for_ateroid(x, r, lr):
    if x > 0:
        if r[x - 1] == 1:
            return False
        else:
            if lr != None:
                if lr[x - 1] == 1 or lr[x] == 1:
                    return False
                elif x < size[0] - 1:
                    if lr[x + 1] == 1:
                        return False
                    else:
                        return True
                else:
                    return True
            else:
                return True
    elif lr != None:
        if lr[x - 1] == 1 or lr[x] == 1:
            return False
        elif x < size[0] - 1:
            if lr[x + 1] == 1:
                return False
            else:
                return True
        else:
            return True
    else:
        return True

for y in range(size[1]):
    for x in range(size[0]):
        random.seed(seed + x**2 + y)
        if random.random() < 0.2 and check_for_ateroid(x, row, last_row):
            row.append(1)
        else:
            row.append(0)

    map.append(row)
    last_row = row
    row = []

def retrieve_chunk_value(x, y):
    return map[y][x]

for _ in map:
    print(_)
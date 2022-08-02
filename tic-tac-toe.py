import sys

def ply_field(crosses, noughts):                #draw a currrent field
    print("  0 1 2")
    for i in range(3):  # go row by row checking whether coordinates are occupied
        print(f"{i}", end=" ")

        for j in range(3):
            if (i, j) in crosses:
                print(f"x", end=" ")
            elif (i, j) in noughts:
                print(f"o", end=" ")
            else:
                print(f"-", end=" ")

        print()

def win_check(fig):             #check if figure has won
    Xs = list(map(lambda t: t[0], fig))
    Ys = list(map(lambda t: t[1], fig))

    if any([Xs.count(0) == 3, Xs.count(1) == 3, Xs.count(2) == 3]):
        return True
    if any([Ys.count(0) == 3, Ys.count(1) == 3, Ys.count(2) == 3]):
        return True
    if ((0, 0) in fig) and ((1, 1) in fig) and ((2, 2) in fig):
        return True
    if ((0, 2) in fig) and ((1, 1) in fig) and ((2, 0) in fig):
        return True

    return False


def draw_field(crosses, noughts):                #decorate function to draw current field after each use
    def dec_body(func):
        ply_field(crosses, noughts)

        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            ply_field(crosses, noughts)
            return None

        return wrapper

    return dec_body

crosses = []
noughts = []

@draw_field(crosses, noughts)
def turn(x, y, fig):                #add coordinates to the right list
    fig.append((x, y))

def get_values(fig):                #get input and check if it's right
    while True:
        cds = input(f"Сделайте ход {fig} (укажите строку, затем столбец через пробел): ").split()

        if len(cds) < 2:
            print("Укажите две координаты!")
            continue

        x, y = cds

        if x not in "012" or y not in "012":
            print("Укажите координаты в поле для игры!")
            continue

        x, y = int(x), int(y)

        if (x, y) in noughts or (x, y) in crosses:
            print("Укажите свободную точку!")
            continue

        break

    return x, y

#Main body, where we make turns and check for wins
turn(*get_values("крестиками"), crosses)

for _ in range(4):
    turn(*get_values("ноликами"), noughts)
    if win_check(noughts):
        print("Нолики выиграли")
        sys.exit()

    turn(*get_values("крестиками"), crosses)
    if win_check(crosses):
        print("Крестики выиграли")
        sys.exit()

print("Ничья")
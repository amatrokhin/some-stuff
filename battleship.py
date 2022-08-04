import random as rnd
import sys
from colorama import init, Fore, Style
init()

class BoardOutException(Exception):
    pass

class OccupiedPlaceException(Exception):
    pass

class DirectionException(Exception):
    pass

class Dot:

    def __init__(self, x, y):
        self.x = x                              #because we want our player to use 1-6 numbers
        self.y = y

    def __eq__(self, other):                    #We want to compare dots and to be able to find them in lists
        return self.x == other.x and self.y == other.y

class Ship:

    def __init__(self, l, dot, direction):
        self.l = l
        self.dot = dot                          #we transfer a Dot class instance
        self.direction = direction              #vertical (v) or horizontal (h) direction
        self.hp = l


    def dots(self):                             #show ship's dots
        if self.direction == "h":
            return [Dot(self.dot.x, self.dot.y + i) for i in range(self.l)]
        elif self.direction == "v":
            return [Dot(self.dot.x + i, self.dot.y) for i in range(self.l)]
        else:
            raise DirectionException("Неизвестное направление! Введите букву 'v' или 'h'.")

class Board:

    field: list                                 #board matrix 6x6
    ships: int                                  #list of ships on board
    alive: int                                  #number of ships alive
    hid: bool                                   #hide board: True/False
    ship_list: list                             #list of ship instances
    total_hp: int                               #all ships hp combined

    def __init__(self, hid):
        self.hid = hid
        self.field = [['O'] * 6 for _ in range(6)]
        self.alive = 0
        self.ships = 0
        self.ship_list = []
        self.total_hp = 0

    def out(self, dot):                         #check if dot is out of bounds
        if any([dot.x < 0, dot.x > 5, dot.y < 0, dot.y > 5]):
            return True
        else:
            return False

    def get_dot(self, x, i, y, j):              #this is a helper not to write many ifs in add_ship method
        if any([x+i < 0, x+i > 5, y+j < 0, y+j > 5]):
            return False
        else:
            return self.field[x + i][y + j]

    def add_ship(self, ship):                   #adding a ship on the Board using Ship class, if allowed
        init_fig = '■'
        ship_fig = Fore.RED + init_fig + Style.RESET_ALL
        for dot in ship.dots():
            if self.out(dot):
                raise BoardOutException("Не выходите за пределы доски!")

            elif self.field[dot.x][dot.y] == ship_fig:
                raise OccupiedPlaceException("Здесь находится корабль, выберите другое место")

            elif any([self.get_dot(dot.x, 1, dot.y, 0) == ship_fig, self.get_dot(dot.x, -1, dot.y, 0) == ship_fig,
                      self.get_dot(dot.x, 0, dot.y, 1) == ship_fig, self.get_dot(dot.x, 0, dot.y, -1) == ship_fig,
                      self.get_dot(dot.x, 1, dot.y, 1) == ship_fig, self.get_dot(dot.x, 1, dot.y, -1) == ship_fig,
                      self.get_dot(dot.x, -1, dot.y, 1) == ship_fig, self.get_dot(dot.x, -1, dot.y, -1) == ship_fig]):
                raise OccupiedPlaceException("Рядом находится другой корабль, выберите другое место")

        for dot in ship.dots():                      #we first check all posotions and then place them at once
            self.field[dot.x][dot.y] = init_fig      #otherwise we will never place 3-cell and 2-cell ships

        #Now we fill 'ships waters' with red (his cells and nearby cells)
            self.contour(dot)

        self.ship_list.append(ship)             #Add ship to the desk list and increase it's total hp
        self.total_hp += ship.hp

    def contour(self, dot):                    #fill cells near dot with red
        for i in range(-1, 2):

            for j in range(-1, 2):

                if pos := self.get_dot(dot.x, i, dot.y, j):
                    if Fore.RED not in pos:
                        self.field[dot.x + i][dot.y + j] = Fore.RED + self.field[dot.x + i][dot.y + j] + Style.RESET_ALL

    def show(self):                             #show a current state of a board
        if self.hid:
            print("Эта доска противника и она скрыта")
        else:
            print(f"  | 1 | 2 | 3 | 4 | 5 | 6 |")
            for i in range(6):
                print(f"{i+1} | ", end="")

                for j in range(6):
                    print(f"{self.field[i][j]} | ", end="")

                print()

    def shot(self, dot):                        #make a shot in a valid dot return the symbol placed
        init_fig = 'X'
        shot_fig = Fore.RED + init_fig + Style.RESET_ALL
        if self.out(dot):
            raise BoardOutException("Не выходите за пределы доски!")

        elif ('X' in self.field[dot.x][dot.y]) or ('T' in self.field[dot.x][dot.y]):
            raise BoardOutException("Сюда вы уже стреляли, выберите другую точку")

        elif '■' in self.field[dot.x][dot.y]:
            self.field[dot.x][dot.y] = shot_fig

            for elem in self.ship_list:
                if dot in elem.dots():          #search for hitted ship
                    elem.hp -= 1                #decrease ship's hp
                    self.total_hp -= 1          #decrease total hp

                    if elem.hp:                 #check if ship is still alive
                        print("Ранил!")
                    else:
                        self.alive -= 1
                        print("Убил!")

            return 'X'

        else:
            self.field[dot.x][dot.y] = 'T'
            print("Мимо!")
            return 'T'

class SupBoard(Board):                          #this board is for tracking your shots

    def shot(self, dot, elem, help):            #place element 'elem' in dot
        self.field[dot.x][dot.y] = elem
        if help == "Y":
            if elem == 'X':                     #little helper if you want, I don't
                self.contour(dot)


class Player:

    def __init__(self, my_board, enemy_board, shot_board):
        self.my_board = my_board
        self.enemy_board = enemy_board
        self.shot_board = shot_board

    def ask(self, text):                        #ask where to shoot, will be used leter in AI and User classes
        pass

    def move(self, help):                             #make a move aka shoot where said
        try:
            x, y = self.ask("Введите координаты выстрела в формате '#cтрока #столбец': ")
            elem = self.enemy_board.shot(Dot(int(x) - 1, int(y) - 1))
            self.shot_board.shot(Dot(int(x) - 1, int(y) - 1), elem, help)
            return False
        except BoardOutException as err:
            print(err)
            return True
        except ValueError:
            print("Введите два числа от 1 до 6 через пробел!")
            return True

    def show_boards(self):                      #show my_board and shot_board
        if self.my_board.hid and self.shot_board.hid:
            print("Эта доска противника и она скрыта")
        else:
            print("  | 1 | 2 | 3 | 4 | 5 | 6 |                | 1 | 2 | 3 | 4 | 5 | 6 |")
            for i in range(6):
                print(f"{i + 1} | ", end="")    #draw main board

                for j in range(6):
                    print(f"{self.my_board.field[i][j]} | ", end="")

                print(f"             {i + 1} | ", end="")

                for j in range(6):              #draw supboard
                    print(f"{self.shot_board.field[i][j]} | ", end="")

                print()

class AI(Player):

    def ask(self, text):
        return rnd.randint(1, 6), rnd.randint(1, 6)     #because we want a uniform input from AI and User we use 1-6 numbers

class User(Player):

    def ask(self, text):
        return input(text).split()


class Game:                                     #create players and play game

    user_board = Board(False)
    user_shot_board = SupBoard(False)
    ai_board = Board(True)
    ai_shot_board = SupBoard(True)
    user = User(user_board, ai_board, user_shot_board)
    ai = AI(ai_board, user_board, ai_shot_board)

    def clear_board(self, board):               #reset board to initial state
        for i, row in enumerate(board.field):
            for j in range(len(row)):
                board.field[i][j] = 'O'
        board.ship_list = []
        board.ships = 0
        board.alive = 0
        board.total_hp = 0

    def random_board(self, board):              #create a random board for ai or user
        l = 3

        for i in range(7):
            if i == 1:
                l = 2
            if i == 3:
                l = 1

            for j in range(2000):
                try:
                    x, y = self.ai.ask('')      #empty string because in ai case there is no need in string
                    board.add_ship(Ship(l, Dot(x - 1, y - 1), rnd.choice(['v', 'h'])))

                except BoardOutException:
                    continue
                except OccupiedPlaceException:
                    continue

                else:
                    board.alive += 1
                    board.ships += 1
                    break

            if board.ships < i+1:               #if after step no ship added then stop creating it and clear it
                self.clear_board(board)
                break

        if board.ships < 7:                     #if everything went well finish else repeat board creation
            self.random_board(board)

    def manuall_board(self, board):             #user places ships on board manually, we explain how to do it
        print("Необходимо расставить по очередь 7 кораблей: "
              "1 3-палубный, 2 2-палубных и 4 1-палубных. В указанном порядке")
        print("Вам будет предложено выбрать положение носа корабля на карте и его направление")
        print("Вертикальное направление означает, что остальные точки корабля будут располагаться ниже носа")
        print("Горизонтальное направление означает, что остальные точки корабля будут располагаться правее носа")
        print("Ах,да! Корабли не должны находиться на соседних клетках... Ты ведь в курсе, да?")

        for i in range(7):  # add ships manually
            if i == 0:
                l = 3
            elif i == 1:
                l = 2
            elif i == 3:
                l = 1

            print("\n-------------------------------------------------------------------------------------")
            print("Ваша доска")
            board.show()

            while True:
                print(f"Выберите место для {l}-палубного корабля")

                try:
                    x, y = self.user.ask("Выберите точку, где будет располагаться его нос в формате "
                                         "'#строка #столбец': ")
                    # Don't forget that ask() returns a list!
                    if l == 1:
                        direction = 'v'         #since it doesn't matter for 1-cell ships
                    else:
                        direction = self.user.ask("Выберите направление - вертикальное(v) или горизонтальное (h): ")[0]
                    board.add_ship(Ship(l, Dot(int(x) - 1, int(y) - 1), direction))

                except BoardOutException as err:
                    print(err)
                    continue
                except OccupiedPlaceException as err:
                    print(err)
                    continue
                except DirectionException as err:
                    print(err)
                    continue
                except ValueError:
                    print("Введите два числа через пробел")
                    continue

                else:
                    board.alive += 1
                    board.ships += 1
                    break

        print("Все готово, теперь играем!")

    def greet(self):                            #greet and explain the rules
        print("Ну здарова Сталкер!")
        print("Я эту прогу сделал и в благородство играть не буду.")
        print("Сыграешь пару раундов и мы в расчете.")
        print("Незнаю, правда, зачем тебе этот морской бой сдался, но я в чужие дела не лезу,")
        print("хочешь поиграть, значит совсем заняться нечем.")
        print("-------------------------------------------------------------------------------------")
        print("Правила игры следующие: надо потопить корабли противника раньше, чем потопят твои ")
        print("Ходить надо так: вводишь номер строки и номер столбца через пробел. И только в таком порядке!")

    def loop(self, help):                             #moves and win checks
        user_board_hp = self.user_board.total_hp
        ai_board_hp = self.ai_board.total_hp
        while True:
            print("\n-------------------------------------------------------------------------------------")
            print("Ваша доска                               Карта ваших попаданий")
            self.user.show_boards()
            print("\nВаш ход")


            while self.user.move(help) or self.ai_board.total_hp < ai_board_hp:             #check if move is right and hp has decreased

                print(f"У противника осталось {self.ai_board.alive} кораблей")

                if self.ai_board.total_hp < ai_board_hp:
                    print("-------------------------------------------------------------------------------------")
                    print("Ваша доска                               Карта ваших попаданий")
                    self.user.show_boards()
                    print("\nВаш ход")

                ai_board_hp = self.ai_board.total_hp

                if ai_board_hp == 0:
                    self.results("Вы выиграли, поздравляю!")
                    sys.exit()


            print("Ход противника")

            while self.ai.move(help) or self.user_board.total_hp < user_board_hp:
                user_board_hp = self.user_board.total_hp

                if user_board_hp == 0:
                    self.results("Вы проиграли, соболезную(((")
                    sys.exit()

    def results(self, text):                          #shows all boards
        print("\n-------------------------------------------------------------------------------------")
        print(text)
        print("\nВаша доска                               Карта ваших попаданий")
        self.user.show_boards()
        print("\nДоска противника                         Карта попаданий противника")
        self.ai_board.hid = False
        self.ai_shot_board.hid = False
        self.ai.show_boards()

    def start(self):                            #greet, create ships on boards and start the play
        print("\n\nДраим палубы и заряжаем орудия, подождите")
        print("\n-------------------------------------------------------------------------------------")
        self.random_board(self.ai_board)
        self.greet()
                                                #ask if user wants to add ships by hand or allmighty random
        print("\nВы хотите самостоятельно расставить корабли(1), или создать случайную расстановку(2)?")
        while (answer := input("Введите 1 или 2: ")) != "1" and answer != "2":
            print("Непохоже на 1 или 2, попробуй еще раз")

        if answer == "1":
            self.manuall_board(self.user_board)
        else:
            self.random_board(self.user_board)

        while (answer := input("Вы хотите выделять красным область вокруг вашего выстрела "
                               "после попадания (Да/Нет)?: ").lower()) != "да" \
                                and answer != "нет":
            print("Наберите Да или Нет")

        if answer == "да":
            help = "Y"
        else:
            help = "N"

        self.loop(help)

game = Game()
game.start()
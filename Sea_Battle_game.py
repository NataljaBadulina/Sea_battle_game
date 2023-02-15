from random import randint
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __repr__(self):
        return f"({self.x}, {self.y})"


class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"


class BoardWrongShipException(BoardException):
    pass
class Ship:
    """
        Класс Ship - реализация поведения объекта корабль для игры "Морской бой":
        bow - Точка, где размещён нос корабля
        l - Длина:палубность (1 - 4)
        o - Направление корабля (0-вертикальное/1-горизонтальное)
        l - Количеством жизней (сколько точек корабля еще не подбито)

        свойство dots: массив с координатами точек корабля, который формируется конструктором
        метод shooten: проверка попадания в цель

        свойство:статус гибели корабля
        свойство (указывается при создании объекта):префикс тега (для своих кораблей будет, например, "my", для чужих "nmy"
        метод-конструктор:изменение массива со статусами точек, например [0,0,1,0]
        метод:shoot(координаты точки), возвращает 1 - если попали, 2 - убил, 0 - мимо

    """
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l
    
    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x 
            cur_y = self.bow.y
            
            if self.o == 0:
                cur_x += i
            
            elif self.o == 1:
                cur_y += i
            
            ship_dots.append(Dot(cur_x, cur_y))
        
        return ship_dots
    
    def shooten(self, shot):
        return shot in self.dots

class Board:
    """
         Класс Board - реализация игрового поля size x size для игры "Морской бой"
             metod add_ship - расставляет корабли на поле с проверкой выхода за пределы поля и занятость ячейки
             метод contour - обводит контур корабля - там кораблей быть не может
             метод __str__ - прориисовывыет поле с текущим состоянием ячеек
             метод out - возвращает True, если точка находится за пределами доски
             метод shot -  реализация выстрела по цели  - мимо, ранен,убит или вылов ошибки - уже стреляли или вылетели из поля
             метод begin - задает множество занятых точек пустым множеством

    """

    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid
        
        self.count = 0
        
        self.field = [ ["O"]*size for _ in range(size) ]
        
        self.busy = []  # множество точек занятых кораблем или убитым кораблем или выстрелом
        self.ships = [] # множество кораблей
    
    def add_ship(self, ship):
        
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)
        
        self.ships.append(ship)
        self.contour(ship)
            
    def contour(self, ship, verb = False):
        near = [
            (-1, -1), (-1, 0) , (-1, 1),
            (0, -1), (0, 0) , (0 , 1),
            (1, -1), (1, 0) , (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)
    
    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i+1} | " + " | ".join(row) + " |"
        
        if self.hid:
            res = res.replace("■", "O")
        return res
    
    def out(self, d):
        return not((0<= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()
        
        if d in self.busy:
            raise BoardUsedException()
        
        self.busy.append(d)
        
        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True
        
        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False
    
    def begin(self):
        self.busy = []

class Player:
    """
         Класс Player - реализация класса игрока, родительский класс для классов User и AI

             metod ask -"спрашивает" игрока, в какую клетку он делает выстрел.
             ask.User - этот метод будет спрашивать кординаты точки из консоли
             ask.AI - координаты точки выдаются рандомно (1-6)
             метод move - делает ход в игре: вызываем метод ask, делаем выстрел по вражеской доске (метод Board.shot ),
             отлавливаем исключения (корабль подбит), и повторяем ход, если паймали исключение.

    """
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy
    
    def ask(self):
        raise NotImplementedError('Пока остается пустым')
    
    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class AI(Player):
    def ask(self):
        d = Dot(randint(0,5), randint(0, 5))
        print(f"Ход компьютера: {d.x+1} {d.y+1}")
        return d

class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()
            
            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue
            
            x, y = cords
            
            if not(x.isdigit()) or not(y.isdigit()):
                print(" Введите числа! ")
                continue
            
            x, y = int(x), int(y)
            
            return Dot(x-1, y-1)

class Game:
    """
        метод random_board - метод генерирует случайную доски для пользователя и для AI (cкрыта)
        метод random_place - метод генерирует корабли длиной [3, 2, 2, 1, 1, 1, 1] и случайными координатами (0-6)
        метод greet - приветствие игрока
        метод loop - реализация игрового цикла: последовательно вызывается move для игроков с проверкой количества живых
        кораблей на досках для определения победы.
        метод start - запуск игры.
    """
    def __init__(self, size = 6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True
        
        self.ai = AI(co, pl)
        self.us = User(pl, co)
    
    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board
    
    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size = self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0,1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        print("------------------------")
        print("    Приветствуем вас    ")
        print("        в игре          ")
        print("       Морской бой      ")
        print("------------------------")
        print("   формат ввода: x y ")
        print("   x - номер строки  ")
        print("   y - номер столбца ")
    
    
    def loop(self):
        num = 0
        while True:
            print("-"*20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-"*20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-"*20)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-"*20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1
            
            if self.ai.board.count == 7:
                print("-"*20)
                print("Пользователь выиграл!")
                break
            
            if self.us.board.count == 7:
                print("-"*20)
                print("Компьютер выиграл!")
                break
            num += 1
            
    def start(self):
        self.greet()
        self.loop()
            
            
g = Game()
g.start()
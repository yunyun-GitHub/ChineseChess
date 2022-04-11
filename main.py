import random

import pygame


class Checkerboard:
    """棋盘"""

    XinJv = (("黑车", 0, 0), ("黑马", 1, 0), ("黑象", 2, 0), ("黑士", 3, 0), ("黑将", 4, 0), ("黑士", 5, 0), ("黑象", 6, 0),
             ("黑马", 7, 0), ("黑车", 8, 0), ("黑炮", 1, 2), ("黑炮", 7, 2), ("黑卒", 0, 3), ("黑卒", 2, 3), ("黑卒", 4, 3),
             ("黑卒", 6, 3), ("黑卒", 8, 3), ("红兵", 0, 6), ("红兵", 2, 6), ("红兵", 4, 6), ("红兵", 6, 6), ("红兵", 8, 6),
             ("红砲", 1, 7), ("红砲", 7, 7), ("红车", 0, 9), ("红马", 1, 9), ("红相", 2, 9), ("红仕", 3, 9), ("红帅", 4, 9),
             ("红仕", 5, 9), ("红相", 6, 9), ("红马", 7, 9), ("红车", 8, 9))

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((600, 605))  # 设置窗口大小，和棋盘图片大小一样
        pygame.display.set_caption("中国象棋")  # 设置标题
        pygame.display.set_icon(pygame.image.load("image/黑象.png"))  # 设置图标图片
        pygame.event.set_blocked(None)  # 禁止所有事件进入队列
        pygame.event.set_allowed((pygame.MOUSEBUTTONDOWN, pygame.QUIT))  # 只允许鼠标按下和关闭游戏窗口事件进入队列
        pygame.event.clear()  # 清空队列中已有的所有事件
        self.font = pygame.font.Font(pygame.font.match_font('SimHei'), 12)
        self.chess_size = (56, 56)  # 棋子图片大小
        self.checkerboard_image = pygame.image.load("image/棋盘.png")  # 加载棋盘图片
        self.checked_image = pygame.image.load("image/选中.png")  # 加载选中图片
        self.move_chess_image = pygame.image.load("image/落子.png")  # 加载落子图片
        self.dots_image = pygame.image.load("image/圆点.png")  # 加载圆点图片
        self.button_image = pygame.image.load("image/按钮.png")  # 按钮
        self.x_y = [[33, 93, 153, 214, 273, 333, 393, 453, 511], [6, 65, 125, 186, 246, 306, 365, 426, 485, 544]]
        self.checked_of_chess = None  # 默认没有棋子被选中
        self.chess_player = "红黑"  # 走棋玩家，默认红方先走
        self.player_pos = True  # 表示黑棋在上红棋在下
        self.end = False
        self.dots_coordinate = [580, 291]
        self.button_coordinate = [580, 271]
        self.move_chess_track = [None, None]  # 落子轨迹，为两个棋盘坐标，默认为空
        self.last_mouse_coordinate = (None, None)  # 上次鼠标点击的棋盘坐标，默认为空
        self.chess_manual = {}  # 保存棋子
        self.create_chess()  # 创建棋子

    def create_chess(self):
        """创建棋子"""
        for image_name in list({}.fromkeys(i[0] for i in Checkerboard.XinJv)):
            image = pygame.image.load("image/" + image_name + ".png")  # 加载棋子图片
            for chess in Checkerboard.XinJv:
                if image_name == chess[0]:  # 创建棋子
                    self.chess_manual[chess[-2:]] = Chessman(chess[0], image, chess[-2:], self.x_y)

    def start_game(self):
        while True:
            self.draw_chess()  # 在窗口中画上棋盘，棋子，各种效果等
            pygame.display.update()  # 刷新界面
            self.process_events()  # 处理事件

    def draw_chess(self):
        """在窗口中画上棋盘，棋子，各种效果等"""
        self.screen.blit(self.checkerboard_image, (0, 0))  # 画棋盘
        for chess in self.chess_manual.values():  # 根据chess_manual画棋子
            self.screen.blit(chess.image, chess.pixel_coordinate)
        if self.checked_of_chess:  # 如果有棋子被选中，就在该棋子处画上选中效果
            self.screen.blit(self.checked_image, self.checked_of_chess.pixel_coordinate)
        if self.move_chess_track != [None, None]:  # 画落子效果
            self.screen.blit(self.move_chess_image, self.move_chess_track[0])
            self.screen.blit(self.move_chess_image, self.move_chess_track[1])
        self.screen.blit(self.dots_image, self.dots_coordinate)  # 画圆点
        self.screen.blit(self.button_image, self.button_coordinate)
        self.screen.blit(self.font.render(self.chess_player[0] + "方走", True, (0, 0, 0)), (558, 293))  # 显示走棋棋手

    def process_events(self):
        """处理事件"""
        while True:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 只有鼠标左键按下才会更新
                    if self.dots_coordinate[0] < event.pos[0] < self.dots_coordinate[0] + 18 and \
                            self.dots_coordinate[1] < event.pos[1] < self.dots_coordinate[1] + 18:
                        self.flip_board()  # 翻转棋盘
                    elif self.button_coordinate[0] < event.pos[0] < self.button_coordinate[0] + 18 and \
                            self.button_coordinate[1] < event.pos[1] < self.button_coordinate[1] + 18:
                        Engine.demo()
                    elif self.end is False:
                        self.update_checkerboard_state(self.translate_coordinate(event.pos))  # 更新棋盘状态属性
                    break

    def update_checkerboard_state(self, now_mouse_coordinate):
        """接收鼠标点击的棋盘坐标，更新棋盘状态属性，判断是要走棋还是要干什么"""
        if now_mouse_coordinate != self.last_mouse_coordinate:  # 如果点击的坐标和前一次一样，则什么也不做
            chess = self.chess_manual.get(now_mouse_coordinate)
            # 如果没有选中棋子，则把点击的棋子标记为选中状态，或者点击了棋盘边缘，则选中为None
            if self.checked_of_chess is None or now_mouse_coordinate == (None, None):
                if (chess and chess.name[0] == self.chess_player[0]) or (chess is None):
                    self.checked_of_chess = chess  # 把点击的棋子标记为选中状态
                self.last_mouse_coordinate = now_mouse_coordinate  # 更新上次点击的棋盘坐标
            else:  # 否则说明要将选中的棋子走到点击的棋盘坐标
                self.move_chess(self.checked_of_chess, now_mouse_coordinate)  # 将选中的棋子走到点击的棋盘坐标
                self.last_mouse_coordinate = (None, None)  # 更新上次点击的棋盘坐标

    def move_chess(self, chess, coordinate):
        """接受一个被选中的棋子和要走的坐标进行走棋"""
        m = {}
        for i in self.chess_manual:
            m[Checkerboard.player_coordinate_convert("盘转" + self.chess_player[0], i, self.player_pos)] = self.chess_manual[i].name

        if Checkerboard.player_coordinate_convert("盘转" + self.chess_player[0], coordinate, self.player_pos) in Checkerboard.may_coordinate(
                Checkerboard.player_coordinate_convert("盘转" + self.chess_player[0], chess.coordinate, self.player_pos), m):
            self.move_chess_track[0] = chess.pixel_coordinate  # 更新落子轨迹
            self.chess_manual[coordinate] = chess
            self.chess_manual.pop(chess.coordinate)
            chess.coordinate = coordinate  # 将接收到的棋子走到指定坐标
            self.move_chess_track[1] = chess.pixel_coordinate  # 更新落子轨迹
            self.chess_player = self.chess_player[::-1]  # 更新走棋棋手
            general = []
            for chess in self.chess_manual.values():
                if chess.name in {"黑将", "红帅"}:
                    general.append(chess.name)
            if "黑将" not in general:
                self.end = True
                print("红方胜")
            if "红帅" not in general:
                self.end = True
                print("黑方胜")
        self.checked_of_chess = None  # 更新选中状态

    def translate_coordinate(self, pixel_coordinate):
        """将像素坐标翻译成棋盘坐标"""
        coordinate = [None, None]
        for i in self.x_y[0]:
            if i < pixel_coordinate[0] < i + self.chess_size[0]:
                coordinate[0] = self.x_y[0].index(i)
        for j in self.x_y[1]:
            if j < pixel_coordinate[1] < j + self.chess_size[1]:
                coordinate[1] = self.x_y[1].index(j)
        if None in coordinate:
            coordinate = [None, None]
        return tuple(coordinate)

    def flip_board(self):
        """翻转棋盘"""
        m = {}
        for chess in self.chess_manual.values():
            chess.coordinate = (8 - chess.coordinate[0], 9 - chess.coordinate[1])
            m[chess.coordinate] = chess
        self.chess_manual = m
        self.move_chess_track = [None, None]
        self.player_pos = not self.player_pos

    @staticmethod
    def player_coordinate_convert(convert, coordinate, player_pos):
        """棋盘坐标与棋手坐标相互转换"""
        if player_pos:
            if convert == "黑转盘":
                return coordinate[0] - 1, coordinate[1] - 1
            elif convert == "红转盘":
                return 9 - coordinate[0], 10 - coordinate[1]
            elif convert == "盘转黑":
                return coordinate[0] + 1, coordinate[1] + 1
            elif convert == "盘转红":
                return 9 - coordinate[0], 10 - coordinate[1]
            elif convert == "互转":
                return 10 - coordinate[0], 11 - coordinate[1]
        else:
            if convert == "黑转盘":
                return 9 - coordinate[0], 10 - coordinate[1]
            elif convert == "红转盘":
                return coordinate[0] - 1, coordinate[1] - 1
            elif convert == "盘转黑":
                return 9 - coordinate[0], 10 - coordinate[1]
            elif convert == "盘转红":
                return coordinate[0] + 1, coordinate[1] + 1
            elif convert == "互转":
                return 10 - coordinate[0], 11 - coordinate[1]

    @staticmethod
    def general_meet(coordinate_self, chess_manual, coordinate):
        chess_manual = chess_manual.copy()
        if chess_manual.get(coordinate) in {"黑将", "红帅"}:
            return False
        chess_manual[coordinate] = chess_manual[coordinate_self]
        chess_manual.pop(coordinate_self)
        x1 = y1 = x2 = y2 = None
        for i in chess_manual:
            if chess_manual[i] == "黑将":
                x1, y1 = i[0], i[1]
            elif chess_manual[i] == "红帅":
                x2, y2 = i[0], i[1]
        if x1 == x2:
            s = int(((y2 - y1) ** 2) ** 0.5)
            for c in range(1, s):
                x = (x2 - x1) * c / s + x1
                y = (y2 - y1) * c / s + y1
                if chess_manual.get((x, y)):
                    return False
            return True
        return False

    @staticmethod
    def may_coordinate(chess_coordinate, chess_manual):
        """接收一个棋子坐标和棋谱，计算能落子的坐标,棋谱必须和self.chess_manual的self.player_pos一样"""
        chess_name = chess_manual[chess_coordinate]
        coordinate_gather = set()
        i, j = chess_coordinate
        if chess_name[-1] in {"车"}:
            for x, y in [(9, j), (1, j), (i, 1), (i, 10)]:
                s = int(((x - i) ** 2 + (y - j) ** 2) ** 0.5)
                for c in range(1, s + 1):  # s/c=(x-i)/(x1-i)=(y-j)/(y1-j)
                    x1 = int((x - i) * c / s + i)
                    y1 = int((y - j) * c / s + j)
                    if chess_manual.get((x1, y1)) is None:
                        coordinate_gather.add((x1, y1))
                    else:
                        if chess_manual.get((x1, y1))[0] != chess_name[0]:
                            coordinate_gather.add((x1, y1))
                        break
        elif chess_name[-1] in {"马"}:
            candidacy = {(i - 1, j + 2): (i, j + 1), (i + 1, j + 2): (i, j + 1), (i - 1, j - 2): (i, j - 1),
                         (i + 1, j - 2): (i, j - 1), (i - 2, j + 1): (i - 1, j), (i - 2, j - 1): (i - 1, j),
                         (i + 2, j + 1): (i + 1, j), (i + 2, j - 1): (i + 1, j)}
            for coordinate in candidacy:
                lame_leg = candidacy[coordinate]
                if 1 <= coordinate[0] <= 9 and 1 <= coordinate[1] <= 10 and chess_manual.get(lame_leg) is None:
                    if chess_manual.get(coordinate) is None:
                        coordinate_gather.add(coordinate)
                    else:
                        if chess_manual.get(coordinate)[0] != chess_name[0]:
                            coordinate_gather.add(coordinate)
        elif chess_name[-1] in {"象", "相"}:
            candidacy = {(i + 2, j + 2): (i + 1, j + 1), (i - 2, j + 2): (i - 1, j + 1), (i - 2, j - 2): (i - 1, j - 1),
                         (i + 2, j - 2): (i + 1, j - 1)}
            for coordinate in candidacy:
                elephant_eye = candidacy[coordinate]
                if 1 <= coordinate[0] <= 9 and 1 <= coordinate[1] <= 5 and chess_manual.get(elephant_eye) is None:
                    if chess_manual.get(coordinate) is None:
                        coordinate_gather.add(coordinate)
                    else:
                        if chess_manual.get(coordinate)[0] != chess_name[0]:
                            coordinate_gather.add(coordinate)
        elif chess_name[-1] in {"士", "仕"}:
            candidacy = {(i + 1, j + 1), (i - 1, j + 1), (i - 1, j - 1), (i + 1, j - 1)}
            for coordinate in candidacy:
                if 1 <= coordinate[1] <= 3 and 4 <= coordinate[0] <= 6:
                    if chess_manual.get(coordinate) is None:
                        coordinate_gather.add(coordinate)
                    else:
                        if chess_manual.get(coordinate)[0] != chess_name[0]:
                            coordinate_gather.add(coordinate)
        elif chess_name[-1] in {"将", "帅"}:
            candidacy = {(i, j + 1), (i - 1, j), (i, j - 1), (i + 1, j)}
            for coordinate in candidacy:
                if 1 <= coordinate[1] <= 3 and 4 <= coordinate[0] <= 6:
                    if chess_manual.get(coordinate) is None:
                        coordinate_gather.add(coordinate)
                    else:
                        if chess_manual.get(coordinate)[0] != chess_name[0]:
                            coordinate_gather.add(coordinate)
        elif chess_name[-1] in {"炮", "砲"}:
            for x, y in [(9, j), (1, j), (i, 1), (i, 10)]:
                s = int(((x - i) ** 2 + (y - j) ** 2) ** 0.5)
                gun_mount = None
                for c in range(1, s + 1):  # s/c=(x-i)/(x1-i)=(y-j)/(y1-j)
                    x1 = int((x - i) * c / s + i)
                    y1 = int((y - j) * c / s + j)
                    if gun_mount is None:
                        if chess_manual.get((x1, y1)) is None:
                            coordinate_gather.add((x1, y1))
                        else:
                            gun_mount = True
                    else:
                        if chess_manual.get((x1, y1)):
                            if chess_manual.get((x1, y1))[0] != chess_name[0]:
                                coordinate_gather.add((x1, y1))
                            break
        elif chess_name[-1] in {"兵", "卒"}:
            candidacy = {(i, j + 1), (i - 1, j), (i + 1, j)}
            for coordinate in candidacy:
                if 1 <= coordinate[0] <= 9 and 1 <= coordinate[1] <= 10:
                    if coordinate[1] <= 5 and coordinate == (i, j + 1):
                        coordinate_gather.add(coordinate)
                    elif coordinate[1] > 5:
                        if chess_manual.get(coordinate) is None:
                            coordinate_gather.add(coordinate)
                        else:
                            if chess_manual.get(coordinate)[0] != chess_name[0]:
                                coordinate_gather.add(coordinate)
        for i in coordinate_gather.copy():
            if Checkerboard.general_meet(chess_coordinate, chess_manual, i):
                coordinate_gather.remove(i)
        return coordinate_gather

    @staticmethod
    def translate_move_chess(move_chess, chess_name):
        """接受棋手坐标形式的走法和棋子名字，返回四字棋谱语言"""
        x1, y1, x2, y2 = move_chess[0][0], move_chess[0][1], move_chess[1][0], move_chess[1][1]
        c = chess_name
        if chess_name in {"车", "炮", "砲", "将", "帅", "兵", "卒"}:
            if x1 == x2:
                if y2 > y1:
                    c = chess_name + str(x1) + "进" + str(y2 - y1)
                elif y2 < y1:
                    c = chess_name + str(x1) + "退" + str(y1 - y2)
            elif y1 == y2:
                c = chess_name + str(x1) + "平" + str(x2)
        elif chess_name in {"马", "象", "相", "士", "仕"}:
            if y2 > y1:
                c = chess_name + str(x1) + "进" + str(x2)
            elif y2 < y1:
                c = chess_name + str(x1) + "退" + str(x2)
        return c


class Chessman:
    """棋子"""

    def __init__(self, name, image, coordinate, x_y):
        self.name = name
        self.image = image
        self.coordinate = coordinate  # 棋子的棋盘坐标
        self.x_y = x_y  # 棋盘坐标和像素坐标对照表

    @property
    def pixel_coordinate(self):
        """棋子在棋盘的像素坐标"""
        return [self.x_y[0][self.coordinate[0]], self.x_y[1][self.coordinate[1]]]


class Engine:

    @staticmethod
    def calculate_coordinate(chess_manual_all):

        return random.choice(list(chess_manual_all.keys()))

    @staticmethod
    def one_hot(feature, player):
        if feature:
            if player == "红":
                r = {"红车": [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "红马": [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     "红砲": [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "红相": [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     "红仕": [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0], "红帅": [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                     "红兵": [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0], "黑车": [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                     "黑马": [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0], "黑炮": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
                     "黑象": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0], "黑士": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
                     "黑将": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0], "黑卒": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]}
                return r[feature]
            elif player == "黑":
                b = {"黑车": [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "黑马": [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     "黑炮": [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "黑象": [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     "黑士": [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0], "黑将": [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                     "黑卒": [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0], "红车": [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                     "红马": [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0], "红砲": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
                     "红相": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0], "红仕": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
                     "红帅": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0], "红兵": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]}
                return b[feature]
        else:
            return [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    @staticmethod
    def demo():
        initial_chess_manual = {}
        for chess in Checkerboard.XinJv:
            initial_chess_manual[Checkerboard.player_coordinate_convert("盘转黑", chess[-2:], True)] = chess[0]

        train_samples = Engine.simulation_chess(initial_chess_manual, "红黑")
        # for s in train_samples:
        #     print(s)
        print("================")

        return train_samples

    @staticmethod
    def simulation_chess(chess_manual, player):
        """模拟下完一整盘棋，以独热编码形式返回每步局面以及胜负"""
        num = 0
        chess_num = len(chess_manual)
        besieged = None
        simulation = []
        while True:
            m = {}
            for chess in chess_manual:
                m[(10 - chess[0], 11 - chess[1])] = chess_manual[chess]
            chess_manual = m
            chess_manual_all = {}  # 储存当前局面下的所有走法的局面
            for chess in chess_manual:
                if chess_manual[chess][0] == player[0]:
                    for coordinate in Checkerboard.may_coordinate(chess, chess_manual):
                        chess_manual_clone = chess_manual.copy()
                        chess_manual_clone[coordinate] = chess_manual_clone[chess]
                        chess_manual_clone.pop(chess)
                        sample = []  # 将每种可能的走法局面以独热编码形式保存
                        for j in range(1, 11):
                            for i in range(1, 10):
                                sample.append(Engine.one_hot(chess_manual_clone.get((i, j)), player[0]))
                        chess_manual_all[(chess, coordinate)] = sample
            if chess_manual_all:
                move_chess = Engine.calculate_coordinate(chess_manual_all)  # 选择走法
                chess_manual[move_chess[1]] = chess_manual[move_chess[0]]  # 走棋
                chess_manual.pop(move_chess[0])
                sample = chess_manual_all[move_chess]  # 这三行不能合并成一行simulation.append(chess_manual_all[move_chess].append(player[0]))
                sample.append(player[0])
                simulation.append(sample)  # 保存走法
                player = player[::-1]
                if len(chess_manual) == chess_num:
                    num += 1
                else:
                    num = 0
                    chess_num = len(chess_manual)
            else:
                besieged = player[0]  # 困毙

            if "黑将" not in chess_manual.values() or besieged == "黑":
                for sample in simulation:
                    if sample[-1] == "红":
                        sample[-1] = [0, 1, 0]
                    elif sample[-1] == "黑":
                        sample[-1] = [0, 0, 1]
                break
            if "红帅" not in chess_manual.values() or besieged == "红":
                for sample in simulation:
                    if sample[-1] == "黑":
                        sample[-1] = [0, 1, 0]
                    elif sample[-1] == "红":
                        sample[-1] = [0, 0, 1]
                break
            if num >= 60:
                for sample in simulation:
                    sample[-1] = [1, 0, 0]
                break
        return simulation


if __name__ == '__main__':
    checkerboard = Checkerboard()  # 创建棋盘
    checkerboard.start_game()  # 开始游戏

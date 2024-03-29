import os
import random
import pygame
import numpy as np
import tensorflow as tf
import threading
import time
import math
import sys


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
        self.button_image = pygame.image.load("image/按钮.png")  # 按钮
        self.x_y = [[33, 93, 153, 214, 273, 333, 393, 453, 511], [6, 65, 125, 186, 246, 306, 365, 426, 485, 544]]
        self.checked_of_chess = None  # 默认没有棋子被选中
        self.chess_player = "红黑"  # 走棋玩家，默认红方先走
        self.move_what = None
        self.player_pos = True  # 表示黑棋在上红棋在下
        self.end = False
        self.work = False
        self.r_value = 0
        self.b_value = 0
        self.button_coordinate0 = [580, 251]
        self.button_coordinate1 = [580, 271]
        self.button_coordinate2 = [580, 291]
        self.button_coordinate3 = [580, 311]
        self.move_chess_track = [None, None]  # 落子轨迹，为两个棋盘坐标，默认为空
        self.last_mouse_coordinate = (None, None)  # 上次鼠标点击的棋盘坐标，默认为空
        self.chess_manual = {}  # 保存棋子
        self.create_chess()  # 创建棋子
        self.engine = Engine()  # 创建引擎

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
        self.screen.blit(self.button_image, self.button_coordinate0)  # 画圆点
        self.screen.blit(self.button_image, self.button_coordinate1)
        self.screen.blit(self.button_image, self.button_coordinate2)
        self.screen.blit(self.button_image, self.button_coordinate3)
        self.screen.blit(self.font.render("B:" + str(self.b_value), True, (0, 0, 0)), (558, 253))
        self.screen.blit(self.font.render("R:" + str(self.r_value), True, (0, 0, 0)), (558, 313))
        self.screen.blit(self.font.render(self.move_what, True, (0, 0, 0)), (558, 273))  # 显示走棋
        self.screen.blit(self.font.render(self.chess_player[0] + "方走", True, (0, 0, 0)), (558, 293))  # 显示走棋棋手
        if self.work:
            self.screen.blit(self.font.render("思考中.", True, (0, 0, 0)), (558, 333))

    def process_events(self):
        """处理事件"""
        while True:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                pygame.quit()
                # exit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 只有鼠标左键按下才会更新
                    self.button_event(event)
                    break

    def button_event(self, event):
        if self.button_coordinate0[0] < event.pos[0] < self.button_coordinate0[0] + 18 and self.button_coordinate0[1] < event.pos[1] < self.button_coordinate0[1] + 18:
            if self.engine.start_train:
                self.engine.start_train = False
                self.work = False
                print("正在结束，请稍等。。。")
            elif len(threading.enumerate()) <= 1:
                self.engine.start_train = True
                self.work = True
                threading.Thread(target=self.engine.train_model).start()  # 启动线程，即让线程开始执行
        elif self.button_coordinate1[0] < event.pos[0] < self.button_coordinate1[0] + 18 and self.button_coordinate1[1] < event.pos[1] < self.button_coordinate1[1] + 18:
            if len(threading.enumerate()) <= 1:
                self.flip_board()  # 翻转棋盘
        elif self.button_coordinate2[0] < event.pos[0] < self.button_coordinate2[0] + 18 and self.button_coordinate2[1] < event.pos[1] < self.button_coordinate2[1] + 18 and \
                self.end is False:  # 电脑思考
            if len(threading.enumerate()) <= 1:
                self.work = True
                threading.Thread(target=self.computer_think).start()  # 电脑思考  启动线程，即让线程开始执行
        elif self.button_coordinate3[0] < event.pos[0] < self.button_coordinate3[0] + 18 and self.button_coordinate3[1] < event.pos[1] < self.button_coordinate3[1] + 18:
            # 开始新局,将各个属性恢复默认
            if len(threading.enumerate()) <= 1:
                self.chess_manual = {}  # 清空棋子
                self.create_chess()  # 创建棋子
                self.checked_of_chess = None  # 默认没有棋子被选中
                self.chess_player = "红黑"  # 走棋玩家，默认红方先走
                self.r_value = "0"
                self.b_value = "0"
                self.end = False
                self.move_what = None
                self.player_pos = True  # 表示黑棋在上红棋在下
                self.move_chess_track = [None, None]  # 落子轨迹，为两个棋盘坐标，默认为空
                self.last_mouse_coordinate = (None, None)  # 上次鼠标点击的棋盘坐标，默认为空
        elif self.end is False:
            if len(threading.enumerate()) <= 1:
                self.update_checkerboard_state(self.translate_coordinate(event.pos))  # 更新棋盘状态属性

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
                value = self.move_chess(self.checked_of_chess, now_mouse_coordinate)  # 将选中的棋子走到点击的棋盘坐标
                if value:
                    if self.chess_player == "黑红":
                        self.r_value = int(value)
                    else:
                        self.b_value = int(value)
                self.last_mouse_coordinate = (None, None)  # 更新上次点击的棋盘坐标

    def move_chess(self, chess, coordinate):
        """接受一个被选中的棋子和要走的坐标进行走棋"""
        m = {}
        for i in self.chess_manual:
            m[Checkerboard.player_coordinate_convert("盘转" + self.chess_player[0], i, self.player_pos)] = self.chess_manual[i].name
        value = False
        player_chess = Checkerboard.player_coordinate_convert("盘转" + self.chess_player[0], chess.coordinate, self.player_pos)
        player_coordinate = Checkerboard.player_coordinate_convert("盘转" + self.chess_player[0], coordinate, self.player_pos)
        if player_coordinate in Checkerboard.may_coordinate(player_chess, m):
            self.move_what = Checkerboard.translate_move_chess((player_chess, player_coordinate), chess.name[-1])
            self.move_chess_track[0] = chess.pixel_coordinate  # 更新落子轨迹
            self.chess_manual[coordinate] = chess
            self.chess_manual.pop(chess.coordinate)
            chess.coordinate = coordinate  # 将接收到的棋子走到指定坐标

            m[player_coordinate] = m[player_chess]
            m.pop(player_chess)
            value = np.max(self.engine.chess_model(tf.reshape(tf.cast(self.engine.one_hot_chess_manual(m, self.chess_player[0]), tf.int16), (1, 10, 9, 15))))

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
        return value

    def computer_think(self):
        m = {}
        for i in self.chess_manual:
            m[Checkerboard.player_coordinate_convert("盘转" + self.chess_player[0], i, self.player_pos)] = self.chess_manual[i].name

        nm = {}
        b = list(m.keys())
        random.shuffle(b)
        for i in b:
            nm[i] = m[i]

        move_chess, ucb1 = self.engine.connector(nm, self.chess_player)
        if self.chess_player == "红黑":
            self.r_value = int(ucb1)
        else:
            self.b_value = int(ucb1)
        chess = Checkerboard.player_coordinate_convert(self.chess_player[0] + "转盘", move_chess[0], self.player_pos)
        coordinate = Checkerboard.player_coordinate_convert(self.chess_player[0] + "转盘", move_chess[1], self.player_pos)
        self.move_chess(self.chess_manual[chess], coordinate)
        self.work = False
        self.draw_chess()  # 在窗口中画上棋盘，棋子，各种效果等
        pygame.display.update()  # 刷新界面

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
    def enemy_chess_manual(chess_manual):
        enemy_chess_manual = {}  # 将坐标转到对手坐标
        for chess in chess_manual:
            enemy_chess_manual[(10 - chess[0], 11 - chess[1])] = chess_manual[chess]
        return enemy_chess_manual

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
        """接收一个棋子坐标和棋谱，计算能落子的坐标"""
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


class Node:
    def __init__(self, chess_manual, players, move_chess=None, root_node=None):
        self.root_node = root_node
        self.child_nodes = []
        self.value = 0
        self.search_num = 0
        self.move_chess = move_chess
        self.chess_manual = chess_manual
        self.players = players

    @property
    def enemy_general(self):
        if self.players == '红黑':
            enemy_general = '黑将'
        else:
            enemy_general = '红帅'
        return enemy_general

    @property
    def general(self):
        if self.players == '红黑':
            general = '红帅'
        else:
            general = '黑将'
        return general

    @property
    def ucb1(self):
        if self.search_num == 0:
            ucb1 = float("inf")
        else:
            ucb1 = self.value / self.search_num + 2 * math.sqrt(math.log(self.root_node.search_num) / self.search_num)
        return ucb1


class Engine:
    """引擎"""

    def __init__(self):
        gpus = tf.config.experimental.list_physical_devices('GPU')  # 当使用GPU版本时，该语句列出所有GPU
        if gpus:  # set_memory_growth模式允许内存增长
            for gpu in gpus:  # 当有多块GPU时可以使用循环语句，把所有的GPU都设置成set_memory_growth模式
                tf.config.experimental.set_memory_growth(gpu, True)
        self.chess_model = self.create_model()  # 创建模型
        self.chess_loss_func = tf.keras.losses.MeanSquaredError()  # 损失函数
        self.chess_optimizer = tf.keras.optimizers.Adam()  # 优化器
        # 定义检查点
        self.checkpoint_dir = './DQN_checkpoints'
        self.checkpoint = tf.train.Checkpoint(chess_optimizer=self.chess_optimizer, chess_model=self.chess_model)
        if os.path.exists(self.checkpoint_dir):  # 如有需要（在训练前），恢复最新的检查点
            self.checkpoint.restore(tf.train.latest_checkpoint(self.checkpoint_dir))
        else:
            print('未检测到模型数据')
        self.start_train = False
        self.r = {"红车": [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "红马": [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  "红砲": [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "红相": [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  "红仕": [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0], "红帅": [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                  "红兵": [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0], "黑车": [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                  "黑马": [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0], "黑炮": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
                  "黑象": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0], "黑士": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
                  "黑将": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0], "黑卒": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                  None: [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}
        self.b = {"黑车": [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "黑马": [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  "黑炮": [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "黑象": [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  "黑士": [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0], "黑将": [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                  "黑卒": [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0], "红车": [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                  "红马": [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0], "红砲": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
                  "红相": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0], "红仕": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
                  "红帅": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0], "红兵": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                  None: [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}
        self.initial_chess_manual = {}
        for chess in Checkerboard.XinJv:
            self.initial_chess_manual[Checkerboard.player_coordinate_convert("盘转红", chess[-2:], True)] = chess[0]

    @staticmethod
    def create_model():
        """构建模型"""
        model = tf.keras.Sequential([
            # 特征提取层1
            tf.keras.layers.Conv2D(16, kernel_size=(3, 3), padding="same", activation=tf.nn.relu, input_shape=(10, 9, 15)),
            tf.keras.layers.Conv2D(16, kernel_size=(3, 3), padding="same", activation=tf.nn.relu),
            tf.keras.layers.Dropout(0.2),

            # 特征提取层2
            tf.keras.layers.Conv2D(32, kernel_size=(3, 3), padding="same", activation=tf.nn.relu),
            tf.keras.layers.Conv2D(32, kernel_size=(3, 3), padding="same", activation=tf.nn.relu),
            tf.keras.layers.Dropout(0.2),

            # 特征提取层3
            tf.keras.layers.Conv2D(64, kernel_size=(3, 3), padding="same", activation=tf.nn.relu),
            tf.keras.layers.Conv2D(64, kernel_size=(3, 3), padding="same", activation=tf.nn.relu),
            tf.keras.layers.Dropout(0.2),

            # 特征提取层4
            tf.keras.layers.Conv2D(64, kernel_size=(3, 3), padding="same", activation=tf.nn.relu),
            tf.keras.layers.Conv2D(64, kernel_size=(3, 3), padding="same", activation=tf.nn.relu),
            tf.keras.layers.Dropout(0.2),

            # 全连接层
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(128, activation="relu"),
            tf.keras.layers.Dense(128, activation="relu"),
            tf.keras.layers.Dense(1)
        ])
        return model

    def create_child_nodes(self, node):
        nodes_list = []
        train_manual = []
        for chess in node.chess_manual:
            if node.chess_manual[chess][0] == node.players[0]:
                for coordinate in Checkerboard.may_coordinate(chess, node.chess_manual):
                    chess_manual_child_node = node.chess_manual.copy()
                    chess_manual_child_node[coordinate] = chess_manual_child_node[chess]
                    chess_manual_child_node.pop(chess)
                    if node.enemy_general not in chess_manual_child_node.values():
                        node.child_nodes = []
                        node.child_nodes.append(Node(chess_manual_child_node, node.players, move_chess=(chess, coordinate), root_node=node.root_node))
                        return
                    enemy_chess_manual = Checkerboard.enemy_chess_manual(chess_manual_child_node)
                    move_chess_all, chess_manual_all = self.chess_manual_all(enemy_chess_manual, node.players[1])
                    train_manual.extend(chess_manual_all)
                    nodes_list.append([enemy_chess_manual, move_chess_all, (chess, coordinate)])
        s = 0
        pred = self.chess_model(np.array(train_manual))
        for child_node in nodes_list:
            s1 = s + len(child_node[1])
            move_chess = child_node[1][np.argmax(pred[s:s1])]  # 估计对对手最有利，对己方最不利的走法
            s = s1
            enemy_chess_manual = child_node[0]
            enemy_chess_manual[move_chess[1]] = enemy_chess_manual[move_chess[0]]  # 根据选择的走法走棋
            enemy_chess_manual.pop(move_chess[0])
            chess_manual_child_node = Checkerboard.enemy_chess_manual(enemy_chess_manual)
            if node.general in chess_manual_child_node.values():
                node.child_nodes.append(Node(chess_manual_child_node, node.players, move_chess=child_node[2], root_node=node.root_node))

    def mcts(self, node):
        if node.child_nodes:  # child_nodes有值为枝节点，为空则为叶子节点
            search_node = node.child_nodes[0]
            for child_node in node.child_nodes:
                if child_node.ucb1 > search_node.ucb1:
                    search_node = child_node
            search_value = self.mcts(search_node)
            node.value += search_value
            node.search_num += 1
        else:
            if node.search_num == 0:  # 如果该节点n为0，则ROLLOUT
                search_value = np.max(self.chess_model(np.array(self.chess_manual_all(node.chess_manual, node.players[0])[1])))
                node.value += search_value
                node.search_num += 1
            else:
                if node.general in node.chess_manual.values():
                    if node.enemy_general in node.chess_manual.values():
                        self.create_child_nodes(node)
                        search_value = self.mcts(node.child_nodes[0])
                    else:
                        search_value = 100
                else:
                    search_value = -100
                node.value += search_value
                node.search_num += 1
        return search_value

    def connector(self, chess_manual, players):
        """接口程序"""
        root_node = Node(chess_manual, players)  # 创建根节点
        root_node.root_node = root_node  # 根节点的'根节点'属性为自己
        s1 = time.time()
        self.create_child_nodes(root_node)
        print(time.time() - s1)
        len_root_node_child_nodes = len(root_node.child_nodes)
        n = 0
        while n < len_root_node_child_nodes:
            self.mcts(root_node)
            n += 1
            print('\r', n, end='')
        if len_root_node_child_nodes > 0:
            choose_node = root_node.child_nodes[0]
            for child_node in root_node.child_nodes:
                if child_node.ucb1 > choose_node.ucb1:
                    choose_node = child_node
            print('\n', time.time() - s1)
            return choose_node.move_chess, choose_node.ucb1
        else:
            move_chess_all, chess_manual_all = self.chess_manual_all(chess_manual, players[0])
            move_chess = move_chess_all[np.argmax(self.chess_model(np.array(chess_manual_all)))]
            return move_chess, -100

    def choose_action(self, move_chess_all, chess_manual_all, move_chess):
        """如果有杀棋直接杀，否则90%的情况下选择价值最大的，10%的情况下随机选择"""
        if move_chess:
            return move_chess

        predict = self.chess_model(np.array(chess_manual_all))
        d = abs(abs(np.max(predict)) - 100)
        if d > 100:
            d = 100
        epson = -0.009 * d + 1
        if np.random.uniform() < epson:
            move_chess = random.choice(move_chess_all)
        else:
            move_chess = move_chess_all[np.argmax(predict)]
        return move_chess

    def chess_manual_all(self, chess_manual, player):
        """接受一个局面和玩家，返回所有的走法和走后的局面(独热编码形式)"""
        chess_manual_all = []  # 储存当前局面下的所有走法的局面
        move_chess_all = []
        for chess in chess_manual:
            if chess_manual[chess][0] == player:
                for coordinate in Checkerboard.may_coordinate(chess, chess_manual):
                    chess_manual_clone = chess_manual.copy()
                    chess_manual_clone[coordinate] = chess_manual_clone[chess]
                    chess_manual_clone.pop(chess)
                    sample = self.one_hot_chess_manual(chess_manual_clone, player)  # 将每种可能的走法局面以独热编码形式保存
                    chess_manual_all.append(sample)
                    move_chess_all.append((chess, coordinate))

        return move_chess_all, chess_manual_all

    def one_hot_chess_manual(self, chess_manual, player):
        sample = []  # 将每种可能的走法局面以独热编码形式保存
        if player == "红":
            for j in range(1, 11):
                row = []
                for i in range(1, 10):
                    row.append(self.r[chess_manual.get((i, j))])
                sample.append(row)
        elif player == "黑":
            for j in range(1, 11):
                row = []
                for i in range(1, 10):
                    row.append(self.b[chess_manual.get((i, j))])
                sample.append(row)
        return sample

    def reward(self, chess_manual, players, num):
        if players == '红黑':
            general, enemy_general = '红帅', '黑将'
        else:
            general, enemy_general = '黑将', '红帅'

        chess_manual_all = []  # 储存当前局面下的所有走法的局面
        move_chess_all = []
        move_chess = False
        if enemy_general not in chess_manual.values():
            print(players)
            unterminated = False
            reward = 100
        elif num >= 50:
            print('和棋')
            unterminated = False
            reward = 0
        else:
            unterminated = True
            reward = 0
            chess_manual = Checkerboard.enemy_chess_manual(chess_manual)  # 将坐标转到对手坐标
            for chess in chess_manual:
                if chess_manual[chess][0] == players[1]:
                    for coordinate in Checkerboard.may_coordinate(chess, chess_manual):
                        chess_manual_clone = chess_manual.copy()
                        chess_manual_clone[coordinate] = chess_manual_clone[chess]
                        chess_manual_clone.pop(chess)
                        sample = self.one_hot_chess_manual(chess_manual_clone, players[1])  # 将每种可能的走法局面以独热编码形式保存
                        chess_manual_all.append(sample)
                        move_chess_all.append((chess, coordinate))
                        if general not in chess_manual_clone.values():
                            reward = -100
                            move_chess = (chess, coordinate)
            if not move_chess_all:
                unterminated = False
                reward = 100
        return reward, unterminated, chess_manual, move_chess_all, chess_manual_all, move_chess

    def simulation_chess(self, chess_manual_initial, player_initial):
        """模拟下完一整盘棋，以独热编码形式返回每步局面以及胜负"""
        players = player_initial
        chess_manual = chess_manual_initial.copy()
        unterminated = True
        trains = []
        labels = []
        num, chess_num = 0, len(chess_manual)
        move_chess_all, chess_manual_all = self.chess_manual_all(chess_manual, players[0])  # 计算所有的走法和局面
        move_chess = False
        while unterminated:
            move_chess = self.choose_action(move_chess_all, chess_manual_all, move_chess)  # 从所有的走法中选择一个走法
            chess_manual[move_chess[1]] = chess_manual[move_chess[0]]  # 根据选择的走法走棋
            chess_manual.pop(move_chess[0])
            train = self.one_hot_chess_manual(chess_manual, players[0])
            trains.append(train)

            if len(chess_manual) == chess_num:
                num += 1
            else:
                num, chess_num = 0, len(chess_manual)
            if trains.count(trains[-1]) >= 3:
                num = 50
            reward, unterminated, chess_manual, move_chess_all, chess_manual_all, move_chess = self.reward(chess_manual, players, num)

            if unterminated:
                if reward == -100:
                    potential_value = reward
                else:
                    estimate_move_chess = move_chess_all[np.argmax(self.chess_model(np.array(chess_manual_all)))]  # 估计对对手最有利，对己方最不利的走法

                    estimate_chess_manual = chess_manual.copy()
                    estimate_chess_manual[estimate_move_chess[1]] = estimate_chess_manual[estimate_move_chess[0]]  # 根据选择的走法走棋
                    estimate_chess_manual.pop(estimate_move_chess[0])
                    estimate_chess_manual = Checkerboard.enemy_chess_manual(estimate_chess_manual)  # 将坐标转到对手坐标

                    estimate_move_chess_all, estimate_chess_manual_all = self.chess_manual_all(estimate_chess_manual, players[0])  # 计算所有的走法和局面
                    if estimate_move_chess_all:
                        potential_value = reward + 0.9 * np.max(self.chess_model(np.array(estimate_chess_manual_all)))  # 估计对自己最有利，对对手最不利的走法
                    else:
                        potential_value = reward
            else:
                potential_value = reward
            label = potential_value
            labels.append(label)
            players = players[::-1]
        return trains, labels

    # 注意`tf.function`的使用，该注解使函数被“编译”为计算图模式
    @tf.function
    def train_model_step(self, samples, labels):
        """一个批次的训练"""
        with tf.GradientTape() as chess_tape:
            chess_pred = self.chess_model(samples, training=True)
            chess_loss = self.chess_loss_func(labels, chess_pred)

        gradients_of_chess = chess_tape.gradient(chess_loss, self.chess_model.trainable_variables)
        self.chess_optimizer.apply_gradients(zip(gradients_of_chess, self.chess_model.trainable_variables))

    def train_model(self):
        print("训练开始...")
        time_train = time.time()
        num = 0
        while self.start_train:
            time_start = time.time()
            trains, labels = self.simulation_chess(self.initial_chess_manual, "红黑")
            trains, labels = np.array(trains), tf.cast(labels, tf.float32)
            for i in range(5):
                self.train_model_step(trains, labels)  # 训练模型
            time_end = time.time()
            num += 1
            print('样本:', len(labels), 'time: ', int(time_end - time_start), 'train_time:', int(time_end - time_train), 'num', num)
        current_time = time.strftime('%Y-%m-%d_%H：%M：%S', time.localtime(time.time()))  # 获取当前时间
        checkpoint_prefix = os.path.join(self.checkpoint_dir, current_time)  # 拼接文件名
        self.checkpoint.save(file_prefix=checkpoint_prefix)  # 保存模型
        print("训练结束，模型已保存")


if __name__ == '__main__':
    checkerboard = Checkerboard()  # 创建棋盘
    checkerboard.start_game()  # 开始游戏

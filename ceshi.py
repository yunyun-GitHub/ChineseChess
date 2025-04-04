import copy
import pygame
import sys
import bisect


class Game:
    def __init__(self):
        self.board = [[-7, -6, -3, -2, -1, -2, -3, -6, -7],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, -5, 0, 0, 0, 0, 0, -5, 0],
                      [-4, 0, -4, 0, -4, 0, -4, 0, -4],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [4, 0, 4, 0, 4, 0, 4, 0, 4],
                      [0, 5, 0, 0, 0, 0, 0, 5, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [7, 6, 3, 2, 1, 2, 3, 6, 7]]
        self.num_piece = {7: '红车', 6: '红马', 5: '红砲', 4: '红兵', 3: '红相', 2: '红仕', 1: '红帅',
                          -7: '黑车', -6: '黑马', -5: '黑炮', -4: '黑卒', -3: '黑象', -2: '黑士', -1: '黑将'}
        self.cols = [33, 93, 153, 214, 273, 333, 393, 453, 511]  # x轴对应列
        self.rows = [6, 65, 125, 186, 246, 306, 365, 426, 485, 544]  # y轴对应行
        # 初始化 Pygame
        pygame.init()

        # 设置只监听退出事件和鼠标点击事件, 只在鼠标点击时刷新, 节省计算资源
        pygame.event.set_blocked(None)  # 先屏蔽所有事件
        pygame.event.set_allowed([pygame.QUIT, pygame.MOUSEBUTTONDOWN])  # 只允许特定类型的事件进入队列
        pygame.event.clear()  # 清空队列中已有的所有事件

        # 创建窗口
        self.screen = pygame.display.set_mode((600, 605))  # 设置窗口大小，和棋盘图片大小一样
        pygame.display.set_caption("中国象棋")  # 设置标题
        pygame.display.set_icon(pygame.image.load("image/黑象.png"))  # 设置图标图片

        self.font = pygame.font.Font(pygame.font.match_font('SimHei'), 12)  # 加载字体
        self.board_image = pygame.image.load("image/棋盘.png")  # 加载棋盘图片
        self.checked_image = pygame.image.load("image/选中.png")  # 加载选中图片
        self.tracked_image = pygame.image.load("image/落子.png")  # 加载落子图片
        self.button_image = pygame.image.load("image/按钮.png")  # 按钮

        for key, value in self.num_piece.items():  # 加载所有棋子图片, 保存在字典中, 覆盖self.num_piece的值
            self.num_piece[key] = pygame.image.load("image/" + value + ".png")

        self.pr = copy.deepcopy(self.board)
        self.pb = copy.deepcopy(self.board)
        self.checked = [-1, -1]  # 记录选中的坐标, 默认为-1, 表示为空
        self.tracked = [[-1, -1], [-1, -1]]  # 落子轨迹，为两个棋盘坐标，默认为空
        self.player = 1  # 1表示轮到红方走, -1表示轮到黑方走, 默认红方先走

        self.running = False  # 游戏运行状态
        self.draw()

    def update(self, event):
        """更新游戏状态"""
        coordinate = self.pos2coordinate(event.pos)
        if coordinate[0] < 0:  # 点击了棋盘边缘
            self.checked = [-1, -1]  # 重置选中状态
            return

        if self.checked[0] < 0:  # 说明之前没有选中棋子
            # 乘积大于0表示符号相同, 说明点击的位置有棋子, 并且属于当前玩家
            if self.board[coordinate[0]][coordinate[1]] * self.player > 0:
                self.checked = coordinate  # 记录选中坐标
            return

        # 说明之前已经选中了一个棋子，现在要移动
        ar, ab, board, a = self.board2player([self.checked, coordinate])

        if self.validate(a, board):  # 验证移动合法
            self.move(ar, ab)
            self.tracked = [self.checked, coordinate]
            self.player *= -1  # 轮到对方走棋
        self.checked = [-1, -1]  # 重置选中状态

    def move(self, ar, ab):
        """接受一个动作, 执行走棋"""
        (sr, sc), (er, ec) = ar  # 解构元组, 如果两个坐标相同, 相当于没走
        self.board[sr][sc], self.board[er][ec] = 0, self.board[sr][sc]
        self.pr[sr][sc], self.pr[er][ec] = 0, self.pr[sr][sc]

        (sr, sc), (er, ec) = ab  # 解构元组, 如果两个坐标相同, 相当于没走
        self.pb[sr][sc], self.pb[er][ec] = 0, self.pb[sr][sc]

    def board2player(self, action):
        (sr, sc), (er, ec) = action  # 解构元组, 如果两个坐标相同, 相当于没走
        ar = [(sr, sc), (er, ec)]
        sr, sc, er, ec = 9 - sr, 8 - sc, 9 - er, 8 - ec
        ab = [(sr, sc), (er, ec)]

        if self.player == 1:
            board = self.pr
            a = ar
        else:
            board = self.pb
            a = ab

        return ar, ab, board, a

    @staticmethod
    def validate(action, board):
        """验证移动合法"""
        (sr, sc), (er, ec) = action  # 解构元组
        value = board[sr][sc]

        mvs = []
        match value:
            case 7:
                for dr, dc, s in [(0, 1, 8 - sc), (-1, 0, sr), (0, -1, sc), (1, 0, 9 - sr)]:
                    for t in range(1, s + 1):
                        tr, tc = sr + dr * t, sc + dc * t
                        if board[tr][tc] == 0:
                            mvs.append([tr, tc])
                        else:
                            if board[tr][tc] < 0:
                                mvs.append([tr, tc])
                            break
            case 6:
                dts = [[sr, sc + 1, sr - 1, sc + 2], [sr, sc + 1, sr + 1, sc + 2], [sr, sc - 1, sr + 1, sc - 2],
                       [sr, sc - 1, sr - 1, sc - 2], [sr - 1, sc, sr - 2, sc + 1], [sr - 1, sc, sr - 2, sc - 1],
                       [sr + 1, sc, sr + 2, sc + 1], [sr + 1, sc, sr + 2, sc - 1]]
                for mr, mc, tr, tc in dts:
                    if 0 <= tr <= 9 and 0 <= tc <= 8 and board[tr][tc] <= 0 == board[mr][mc]:
                        mvs.append([tr, tc])
            case 5:
                for dr, dc, s in [(0, 1, 8 - sc), (-1, 0, sr), (0, -1, sc), (1, 0, 9 - sr)]:
                    screen = False
                    for t in range(1, s + 1):
                        tr, tc = sr + dr * t, sc + dc * t
                        if not screen:
                            if board[tr][tc] == 0:
                                mvs.append([tr, tc])
                            else:
                                screen = True
                        elif board[tr][tc] != 0:
                            if board[tr][tc] < 0:
                                mvs.append([tr, tc])
                            break
            case 4:
                dts = [[sr - 1, sc]] if 5 <= sr else [[sr, sc + 1], [sr - 1, sc], [sr, sc - 1]]
                for tr, tc in dts:
                    if tr >= 0 and 8 >= tc >= 0 >= board[tr][tc]:
                        mvs.append([tr, tc])
            case 3:
                dts = [[sr - 1, sc + 1, sr - 2, sc + 2], [sr - 1, sc - 1, sr - 2, sc - 2],
                       [sr + 1, sc - 1, sr + 2, sc - 2], [sr + 1, sc + 1, sr + 2, sc + 2]]
                for mr, mc, tr, tc in dts:
                    if 5 <= tr <= 9 and 0 <= tc <= 8 and board[tr][tc] <= 0 == board[mr][mc]:
                        mvs.append([tr, tc])
            case 2:
                dts = [[sr - 1, sc + 1], [sr - 1, sc - 1], [sr + 1, sc - 1], [sr + 1, sc + 1]]
                for tr, tc in dts:
                    if 7 <= tr <= 9 and 3 <= tc <= 5 and board[tr][tc] <= 0:
                        mvs.append([tr, tc])
            case 1:
                dts = [[sr, sc + 1], [sr - 1, sc], [sr, sc - 1], [sr + 1, sc]]
                for tr, tc in dts:
                    if 7 <= tr <= 9 and 3 <= tc <= 5 and board[tr][tc] <= 0:
                        mvs.append([tr, tc])

        print(mvs)
        if [er, ec] in mvs:
            return True

    def pos2coordinate(self, pos):
        """将屏幕像素坐标转换成棋盘坐标方便计算,
        棋盘坐标用线性代数矩阵方法表示, 从上到下为行, 从左到右为列
        """

        # 查找列索引（对应棋盘坐标的列）
        col_idx = bisect.bisect_right(self.cols, pos[0]) - 1
        valid_col = col_idx >= 0 and self.cols[col_idx] <= pos[0] < self.cols[col_idx] + 56

        # 查找行索引（对应棋盘坐标的行）
        row_idx = bisect.bisect_right(self.rows, pos[1]) - 1
        valid_row = row_idx >= 0 and self.rows[row_idx] <= pos[1] < self.rows[row_idx] + 56

        # [-1, -1]表示点击了棋盘外
        return [row_idx, col_idx] if valid_col and valid_row else [-1, -1]

    def coordinate2pos(self, coordinate):
        """将棋盘坐标转换成屏幕像素坐标主要用于绘图
        屏幕像素坐标从左上角开始, 从左到右为x轴, 从上到下为y轴
        """

        row, col = coordinate
        # x横坐标对应列, y纵坐标对应行, 这里有点不合习惯
        x = self.cols[col]
        y = self.rows[row]
        return [x, y]

    def draw(self):
        """绘制所有内容"""
        self.screen.blit(self.board_image, (0, 0))  # 画棋盘

        # 接受一个棋盘二维列表, 遍历所有的元素和索引
        for i, row in enumerate(self.board):
            for j, val in enumerate(row):
                if val != 0:
                    piece_image = self.num_piece[val]  # 获取已经加载的图片
                    self.screen.blit(piece_image, self.coordinate2pos([i, j]))  # 画棋子

        if self.checked[0] >= 0:  # 如果有棋子被选中, 就在该棋子处画上选中效果
            self.screen.blit(self.checked_image, self.coordinate2pos(self.checked))
        if self.tracked[0][0] >= 0:  # 画落子效果
            self.screen.blit(self.tracked_image, self.coordinate2pos(self.tracked[0]))
            self.screen.blit(self.tracked_image, self.coordinate2pos(self.tracked[1]))

        self.screen.blit(self.font.render("_红黑"[self.player] + "方走", True, (0, 0, 0)), (558, 293))  # 显示走棋棋手

        pygame.display.flip()  # 更新显示

    def _handle_event(self, event: pygame.event.Event):
        """处理单个游戏事件"""
        if event.type == pygame.QUIT:
            self._quit_game()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.update(event)
            self.draw()

    def _quit_game(self):
        """清理资源并退出游戏"""
        self.running = False
        pygame.quit()  # 卸载所有Pygame模块, 比如关闭窗口, 释放音频设备等资源
        sys.exit()  # 终止Python解释器的运行

    def run(self):
        """启动游戏主循环"""
        self.running = True

        while self.running:
            # 阻塞等待事件，节省系统资源
            event = pygame.event.wait()
            self._handle_event(event)


if __name__ == "__main__":
    Game().run()

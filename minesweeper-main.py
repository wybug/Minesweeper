import random
import tts
import pygame
import math

screen_width = 1280
screen_height = 720

pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('扫雷世界')

clock = pygame.time.Clock()
running = True

images_path = [
    "images/tile_1.gif",
    "images/tile_2.gif",
    "images/tile_3.gif",
    "images/tile_4.gif",
    "images/tile_5.gif",
    "images/tile_6.gif",
    "images/tile_7.gif",
    "images/tile_8.gif",
    "images/tile_clicked.gif",
    "images/tile_flag.gif",
    "images/tile_mine.gif",
    "images/tile_plain.gif",
    "images/tile_wrong.gif",
]

img_bg = pygame.image.load("images/background.jpg")

img_list = []

for path in images_path:
    img_temp = pygame.image.load(path)
    img_list.append(img_temp)


def get_bell(money):
    if money == 2:
        return 1
    return 0


def add(a, b):
    return a + b


def box(a, b):
    return a * a - b * b


print(f'get_bell 1 is :', get_bell(1))
print(f'get_bell 2 is :', get_bell(2))
print(f'1+1 is :', add(1, 1))
print(f'1+2 is :', add(1, 2))
print(f'1+3 is :', add(1, 3))
print(f'a=2, b=1 is :', box(2, 1))

# 初始化mixer模块
pygame.mixer.init()

# 加载音乐文件
# 《疯狂动物城》的主题曲, try everything
pygame.mixer.music.load('mp3/bg.mp3')

# 设置音乐参数
pygame.mixer.music.set_volume(0.7)  # 设置音量为70%
pygame.mixer.music.set_endevent(pygame.constants.USEREVENT + 1)  # 设置用户事件来在音乐结束时触发

# 播放音乐
pygame.mixer.music.play(loops=-1)  # 设置音乐循环播放无限次

tts.say('欢迎加入扫雷世界')


def isVictory(all_blocks):
    open_flag_counter = 0
    for temp in all_blocks:
        if temp.open_flag:
            open_flag_counter += 1
    if open_flag_counter == 9 * 9 - 10:
        return True


class Missile(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.images = []
        image = pygame.image.load('images/missile.png')
        for angle in range(0, 360):
            self.images.append(pygame.transform.rotate(image, angle))

        self.angle = 0
        self.image = self.images[0]  # self.angle % 360
        self.rect = self.image.get_rect()

    def update(self):
        x1, y1 = self.rect.center
        x2, y2 = pygame.mouse.get_pos()

        # 图像正常位置时90度
        angle_degrees = (math.atan2(y2 - y1, x2 - x1) * 180 / math.pi)

        # 顺时针转换
        if angle_degrees < 0:
            angle_degrees = math.fabs(angle_degrees)
        elif angle_degrees > 0:
            angle_degrees = 360 - angle_degrees

        self.rotate(angle_degrees - 90)
        if x1 != x2 or y1 != y2:
            # 计算角度和运动
            if x2 > x1:
                x1 += 1
            else:
                x1 -= 1
            if y2 > y1:
                y1 += 1
            else:
                y1 -= 1
            self.rect.center = (x1, y1)

    def rotate(self, angle):
        self.angle = int(angle)
        self.image = self.images[self.angle % 360]
        self.rect = self.image.get_rect()

class Block:
    x = 0
    y = 0
    position = []  # 9x9位置, 例如：0,1,1
    type = 0  # 1:mine 2:none
    mine_counter = 0  # 当该模块为none时，counter计数周边
    mine_flag = False  # 该块是否标识雷，用户设置该属性 查询
    open_flag = False  # 该块是否打开，游戏重置为False，用户仅仅能open一次
    down_flag = False

    # 周围方块对应索引，-1为不可用
    # 1  2  3
    # 4  X  5
    # 6  7  8
    def clear(self):
        self.type = 0
        self.mine_counter = 0
        self.mine_flag = False
        self.open_flag = False
        self.down_flag = False

    def mouse_down_event(self, pos, button):
        if self.open_flag:
            return
        pos_x, pos_y = pos
        if self.x <= pos_x < self.x + 16 and self.y <= pos_y < self.y + 16:
            self.down_flag = True
            print(f'click item')

    def mouse_up_event(self, pos, button):
        if self.open_flag:
            return
        pos_x, pos_y = pos
        if self.x <= pos_x < self.x + 16 and self.y <= pos_y < self.y + 16:
            if self.down_flag:
                print(f'clicked item')
                if button == 3:  # 鼠标右键
                    self.mine_flag = True
                elif button == 1 and self.mine_flag:  # 鼠标左键
                    self.mine_flag = False
                else:
                    self.open_flag = True
        self.down_flag = False


# 块 9x9, 81数组
blocks = []

screen_offset_x = (screen_width - 9 * 20) / 2
screen_offset_y = (screen_height - 9 * 20) / 2

block_offset_x = 0
block_offset_y = 0
block_position_x = 1
block_position_y = 1

for i in range(1, 82):
    temp = Block()
    temp.x = screen_offset_x + block_offset_x
    temp.y = screen_offset_y + block_offset_y
    print(f'{i} - {temp.x},{temp.y}')
    temp.position = [i, block_position_x, block_position_y]
    blocks.append(temp)
    block_offset_x += 20
    block_position_x += 1
    if i % 9 == 0:
        block_offset_x = 0
        block_offset_y += 20
        block_position_x = 1
        block_position_y += 1


def generate_unique_data(n, min_val=0, max_val=None):
    if max_val is None:
        max_val = n
    data = list(range(min_val, max_val))
    random.shuffle(data)
    return data[:n]


def reset_game(all_block):
    for temp in all_block:
        temp.clear()

    #  9x9 格子10个雷
    for n in generate_unique_data(10, max_val=81):
        # 设置雷
        all_block[n].type = 1

    # 设置雷后，计算每个块周围的计数器
    for temp in all_block:
        if temp.type != 1:
            ind, px, py = temp.position
            # 周围方块对应索引，-1为不可用
            # 1  2  3
            # 4  X  5
            # 6  7  8
            inds = [
                (px - 1, py - 1),
                (px, py - 1),
                (px + 1, py - 1),
                (px - 1, py),
                (px + 1, py),
                (px - 1, py + 1),
                (px, py + 1),
                (px + 1, py + 1),
            ]

            list_ind = []
            temp.mine_counter = 0

            for pos_x, pos_y in inds:
                # 越界则索引为-1
                if (pos_x - 1) < 0 or (pos_y - 1) < 0:
                    temp_ind = -1
                elif (pos_x - 1) > 8 or (pos_y - 1) > 8:
                    temp_ind = -1
                else:
                    temp_ind = (pos_y - 1) * 9 + (pos_x - 1)
                list_ind.append(temp_ind)
                if temp_ind < 0:
                    continue
                if temp_ind >= len(blocks):
                    continue
                if blocks[temp_ind].type == 1:
                    temp.mine_counter += 1

            str_arr = [str(num) for num in list_ind]
            print(f"{ind} : {px},{py} ---", ' '.join(str_arr))


reset_game(blocks)


class Button:
    def __init__(self, screen, x, y, width, height, text, button_color=(0, 255, 0), text_color=(255, 255, 255)):
        self.screen = screen
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.button_color = button_color
        self.text_color = text_color
        self.rect = (self.x, self.y, self.width, self.height)

    def draw(self):
        # 绘制按钮
        pygame.draw.rect(self.screen, self.button_color, self.rect)
        # 绘制按钮上的文本
        font = pygame.font.Font('font/AlibabaPuHuiTi-3-35-Thin.ttf', 20)
        if font is None:
            font = pygame.font.SysFont(None, 22)
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect()
        text_rect.center = ((self.x + (self.width / 2)), (self.y + (self.height / 2)))
        self.screen.blit(text_surf, text_rect)

    def isOver(self, pos):
        # 检查鼠标是否在按钮上
        pos_x, pos_y = pos
        x, y, w, h = self.rect
        if x < pos_x < x + w and y < pos_y < y + h:
            return True
        return False

    def handleClicked(self):
        pass

    def handleEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.isOver(pygame.mouse.get_pos()):
            print('Button clicked!')  # 或者执行其他操作
            self.handleClicked()


class GameState:
    all_blocks = []
    """
    游戏状态机
    """
    startFlag = False
    pauseFlag = False
    timeTicks = 0
    timeTotalTicks = 0
    font = None
    text_color = None

    def __init__(self, screen, all_blocks, x, y, width, height, text_color=(255, 255, 255)):
        self.screen = screen
        self.all_blocks = all_blocks
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font = pygame.font.Font('font/AlibabaPuHuiTi-3-35-Thin.ttf', 16)
        if self.font is None:
            self.font = pygame.font.SysFont(None, 16)
        self.text_color = text_color
        self.rect = (self.x, self.y, self.width, self.height)
        self.startFlag = False

    def reset(self):
        self.startFlag = False
        self.pauseFlag = False
        self.timeTicks = 0
        self.timeTotalTicks = 0

    def start(self):
        if self.pauseFlag:
            self.pauseFlag = False
            self.timeTicks = pygame.time.get_ticks()
            return
        self.startFlag = True
        self.timeTicks = pygame.time.get_ticks()

    def pause(self):
        self.pauseFlag = True
        self.timeTotalTicks += (pygame.time.get_ticks() - self.timeTicks)

    def stop(self):
        self.startFlag = False

    def isStop(self):
        if self.startFlag:
            return False
        return True

    def getState(self):
        second = 0
        if self.pauseFlag:
            second = math.floor(self.timeTotalTicks / 1000)
        elif self.startFlag:
            second = math.floor((self.timeTotalTicks + pygame.time.get_ticks() - self.timeTicks) / 1000)
        mine_flag_counter = 0
        for item in self.all_blocks:
            if item.mine_flag:
                mine_flag_counter += 1
        return second, mine_flag_counter

    def draw(self):
        # 绘制按钮
        pygame.draw.rect(self.screen, (0, 100, 100), self.rect)

        second, counter = self.getState()
        text = f"Mine Flag: {counter}/10, Time: {second} S"
        # 绘制按钮上的文本
        text_surf = self.font.render(text, True, self.text_color)
        text_rect = text_surf.get_rect()
        text_rect.center = ((self.x + (self.width / 2)), (self.y + (self.height / 2)))
        self.screen.blit(text_surf, text_rect)


# 定义游戏
game_state = GameState(screen, blocks, (screen_width - 250) / 2, 50, 250, 30)


# 鼠标点击事件的处理函数
def handle_mouse_down_click(pos, button):
    print(f'#down 鼠标点击在位置: {pos}')
    for temp in blocks:
        temp.mouse_down_event(pos, button)


def open_around_block(select_block, all_blocks):
    if select_block.open_flag:
        return
    # 已经打开
    if select_block.mine_counter > 0:
        select_block.open_flag = True
        return

    ind, px, py = select_block.position

    print(f'处理空白块：{ind},{px},{py}')
    # 周围方块对应索引，-1为不可用
    # 1  2  3
    # 4  X  5
    # 6  7  8
    inds = [
        (px - 1, py - 1),
        (px, py - 1),
        (px + 1, py - 1),
        (px - 1, py),
        (px + 1, py),
        (px - 1, py + 1),
        (px, py + 1),
        (px + 1, py + 1),
    ]

    list_ind = []

    for pos_x, pos_y in inds:
        temp_ind = -1
        # 越界则索引为-1
        if (pos_x - 1) < 0 or (pos_y - 1) < 0:
            temp_ind = -1
        elif (pos_x - 1) > 8 or (pos_y - 1) > 8:
            temp_ind = -1
        else:
            temp_ind = (pos_y - 1) * 9 + (pos_x - 1)
        list_ind.append(temp_ind)

    if select_block.mine_counter == 0:
        select_block.open_flag = True
        # 仅仅处理空白块
        for n in list_ind:
            if n < 0:
                continue
            if n >= len(all_blocks):
                continue
            open_around_block(all_blocks[n], all_blocks)


def handle_mouse_up_click(pos, button):
    print(f'#up 鼠标点击在位置: {pos}')
    gameOver = False
    for temp in blocks:
        temp_open_flag = temp.open_flag
        temp.mouse_up_event(pos, button)
        if temp_open_flag != temp.open_flag:
            if temp.type == 1:
                tts.say("游戏结束，大侠请重新来过")
                # 播放爆炸声，带缓存。tts use default channel = 0
                tts.play_mp3_file(f'mp3/detonation.mp3', channel=1)
                gameOver = True
            # 空白处理
            elif temp.type != 1 and temp.mine_counter == 0:
                temp.open_flag = False
                open_around_block(temp, blocks)
            # 游戏结束检测
            if not gameOver and isVictory(blocks):
                tts.say("游戏胜利，请继续挑战")
                gameOver = True
            if game_state.isStop():
                game_state.start()
    if gameOver:
        for temp in blocks:
            temp.open_flag = True
        game_state.pause()


class ResetButton(Button):
    def handleClicked(self):
        game_state.reset()
        reset_game(blocks)


class VoiceButton(Button):
    voiceSwitch = True

    def handleClicked(self):
        if self.voiceSwitch:
            self.voiceSwitch = False
            pygame.mixer.music.pause()
            self.text = 'Voice: On'
        else:
            self.voiceSwitch = True
            pygame.mixer.music.play(loops=-1)
            self.text = 'Voice: Off'


# 创建一个按钮实例
buttonReset = ResetButton(screen, (screen_width - 100) / 2 - 60, 100, 100, 30, "重置", button_color=(255, 100, 0))
buttonVoice = VoiceButton(screen, (screen_width - 100) / 2 + 60, 100, 100, 30, "Voice:Off", button_color=(255, 100, 0))

missile_group = pygame.sprite.Group()
missile_group.add(Missile())

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:  # 检查是否点击了鼠标按钮
            # 获取鼠标点击的位置
            mouse_pos = pygame.mouse.get_pos()
            handle_mouse_down_click(mouse_pos, event.button)
            if buttonReset.isOver(event.pos):
                buttonReset.handleEvent(event)
            if buttonVoice.isOver(event.pos):
                buttonVoice.handleEvent(event)
        elif event.type == pygame.MOUSEBUTTONUP:  # 检查是否点击了鼠标按钮
            # 获取鼠标点击的位置
            mouse_pos = pygame.mouse.get_pos()
            handle_mouse_up_click(mouse_pos, event.button)

    image_rect = img_bg.get_rect()
    screen.blit(img_bg, image_rect)

    for temp in blocks:
        image_rect = img_list[11].get_rect()
        image_rect.left = temp.x
        image_rect.top = temp.y
        image_rect.right = image_rect.left + image_rect.width
        image_rect.bottom = image_rect.top + image_rect.height
        screen.blit(img_list[11], image_rect)

        # 显示雷
        if temp.open_flag and temp.type == 1:
            image_rect = img_list[10].get_rect()
            image_rect.left = temp.x
            image_rect.top = temp.y
            image_rect.right = image_rect.left + image_rect.width
            image_rect.bottom = image_rect.top + image_rect.height
            screen.blit(img_list[10], image_rect)
        # 底色或对应数字
        if temp.open_flag and temp.type != 1 and temp.mine_counter == 0:
            image_rect = img_list[8].get_rect()
            image_rect.left = temp.x
            image_rect.top = temp.y
            image_rect.right = image_rect.left + image_rect.width
            image_rect.bottom = image_rect.top + image_rect.height
            screen.blit(img_list[8], image_rect)
        if temp.open_flag and temp.type != 1 and temp.mine_counter > 0:
            image_rect = img_list[temp.mine_counter - 1].get_rect()
            image_rect.left = temp.x
            image_rect.top = temp.y
            image_rect.right = image_rect.left + image_rect.width
            image_rect.bottom = image_rect.top + image_rect.height
            screen.blit(img_list[temp.mine_counter - 1], image_rect)

        if temp.mine_flag and temp.type != 1 and temp.open_flag:  # 不是雷，但标记错了
            image_rect = img_list[12].get_rect()
            image_rect.left = temp.x
            image_rect.top = temp.y
            image_rect.right = image_rect.left + image_rect.width
            image_rect.bottom = image_rect.top + image_rect.height
            screen.blit(img_list[12], image_rect)
        elif temp.mine_flag:
            image_rect = img_list[9].get_rect()
            image_rect.left = temp.x
            image_rect.top = temp.y
            image_rect.right = image_rect.left + image_rect.width
            image_rect.bottom = image_rect.top + image_rect.height
            screen.blit(img_list[9], image_rect)
        # 显示click
        elif temp.down_flag:
            image_rect = img_list[8].get_rect()
            image_rect.left = temp.x
            image_rect.top = temp.y
            image_rect.right = image_rect.left + image_rect.width
            image_rect.bottom = image_rect.top + image_rect.height
            screen.blit(img_list[8], image_rect)

    # 重置按钮
    buttonReset.draw()
    buttonVoice.draw()
    game_state.draw()
    missile_group.update()
    missile_group.draw(screen)

    # 绘图
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

# 结束Pygame
pygame.mixer.music.stop()  # 停止音乐播放
pygame.mixer.quit()
pygame.quit()

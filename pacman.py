import pygame as pyg
import sys
from enum import Enum
import random
import time
import os
import heapq
'''
HÀM TRỢ GIÚP RẤT QUAN TRỌNG CHO PHÉP BẠN CHƠI ÂM THANH CHO TRÒ CHƠI PACMAN BẰNG CÁCH ĐỌC CÁC TẬP TIN ÂM THANH TỪ CÙNG THƯ MỤC VỚI TRÒ CHƠI
'''

pyg.init()

#contain basic game setup information and graphics
class Game_Setup:
    
    def __init__(self):
        # Thiết lập màn hình
        #tỷ lệ giữa bảng sprite và màn hình thực tế
        self.SCALE = 3
        # Kích thước màn hình
        #số ô trong hướng x và y (8x8 pixel trong hình ảnh gốc tạo thành một ô)
        self.X_CELLS = 28
        self.Y_CELLS = 31

        self.SCREEN_WIDTH = self.X_CELLS*8*self.SCALE
        self.SCREEN_HEIGHT = self.Y_CELLS*8*self.SCALE+120

        #tọa độ của lồng ma quái giữa vì đây là nơi tất cả các ma quái bắt đầu ở dạng ô
        self.BLINKY_CAGE_CORDS = (13,11)
        self.CAGE_CORDS = (13,13)

        #vị trí bắt đầu của pacman
        self.PACMAN_START = (13, 23)

        self.DISPLAYING = False

        # Tải bảng sprite
        self.SPRITE_SHEET_PATH = self.open_file_in_same_directory('Arcade - Pac-Man - General Sprites.png')
        #đường dẫn font arcade
        self.ARCADE_FONT_PATH = self.open_file_in_same_directory('PressStart2P-vaV7.ttf')

        self.ARCADE_FONT = pyg.font.Font(self.ARCADE_FONT_PATH, 20)
        self.ARCADE_FONT_LARGE = pyg.font.Font(self.ARCADE_FONT_PATH, 32)
        self.heart_sprite = None  # Để tránh lỗi khi khởi tạo, ta sẽ nạp sprite sau
        self.heart_sprite = None  # Để tránh lỗi khi khởi tạo, ta sẽ nạp sprite trong Graphics


        # Tạo màn hình
        self.SCREEN = pyg.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

    @staticmethod
    def open_file_in_same_directory(file_name):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, file_name)

        return file_path

'''

XÁC ĐỊNH THỜI GIAN BƯỚC ĐI

'''

#hàm trợ giúp cho âm thanh hiệu ứng
class Stopwatch:
    def __init__(self):
        self.start_time = None
        self.elapsed_time = 0.0
        self.pause_time = 0.0
    
    def is_running(self):
        return self.start_time is not None
    
    def start(self):
        self.start_time = time.time()

    def stop(self):
        if self.start_time is None:
            raise Exception("Stopwatch not started.")

        self.elapsed_time += time.time() - self.start_time
        self.start_time = None
        self.pause_time = 0.0

    def get_elapsed_time(self):
        if self.start_time is not None:
            return time.time() - self.start_time - self.pause_time
        else:
            return None
    
    def pause(self):
        self.pause_time += time.time() - self.start_time
        self.start_time = 0.0

    def unpause(self):
        self.start_time = time.time() - self.pause_time
        self.pause_time = 0.0
    

class SoundEffects:
    eating_channel = pyg.mixer.Channel(0)
    background_channel = pyg.mixer.Channel(1)
    startup_channel = pyg.mixer.Channel(2)
    death_channel = pyg.mixer.Channel(3)
    cherry_channel = pyg.mixer.Channel(4)
    ghost_eating_channel = pyg.mixer.Channel(5)
    
    

    eating_effect = pyg.mixer.Sound(Game_Setup.open_file_in_same_directory("pacman_waka.wav"))
    background_effect = pyg.mixer.Sound(Game_Setup.open_file_in_same_directory("pacman_background.wav"))
    startup_effect = pyg.mixer.Sound(Game_Setup.open_file_in_same_directory("pacman_startup.wav"))
    death_effect = pyg.mixer.Sound(Game_Setup.open_file_in_same_directory("pacman_death.wav"))
    cherry_effect = pyg.mixer.Sound(Game_Setup.open_file_in_same_directory("pacman_eatfruit.wav"))
    frightened_effect = pyg.mixer.Sound(Game_Setup.open_file_in_same_directory("pacman_backgroundfrightened.wav"))
    ghost_eating_effect = pyg.mixer.Sound(Game_Setup.open_file_in_same_directory("pacman_eatghost.wav"))
    win_effect = pyg.mixer.Sound(Game_Setup.open_file_in_same_directory("pacman_win.wav"))




class Graphics:
    def __init__(self, setup):
        self.setup = setup
        sprite_sheet_path = setup.SPRITE_SHEET_PATH
        self.sprite_sheet = pyg.image.load(sprite_sheet_path).convert()
        #biến tất cả màu đen thành trong suốt để tránh hộp kỳ lạ xung quanh các sprite
        self.sprite_sheet.set_colorkey((0,0,0))
 # Lấy hình trái tim hoặc Pac-Man nhỏ để hiển thị số mạng
        self.heart_sprite = self.get_sprite(488, 0, 16, 16)  # Lấy sprite từ sprite sheet
        self.heart_sprite = self.scale_sprite(self.heart_sprite)  # Scale cho dễ nhìn

    def get_sprite(self, x, y, width, height):
        sprite = pyg.Surface((width, height), pyg.SRCALPHA)
        sprite.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        return sprite

    def scale_sprite(self, sprite):
        width = sprite.get_width() * self.setup.SCALE
        height = sprite.get_height() * self.setup.SCALE
        return pyg.transform.scale(sprite, (int(width), int(height)))

    def scale_sprites(self, sprites: dict):
        for key in sprites:
             #nếu sprite là một danh sách các sprite thì tỷ lệ từng sprite trong danh sách
            if type(sprites[key]) == list:
                for i in range(len(sprites[key])):
                    sprites[key][i] = self.scale_sprite(sprites[key][i])
                    
             #nếu sprite là một sprite đơn thì tỷ lệ nó
            else:
                sprites[key] = self.scale_sprite(sprites[key])

        return sprites
    
    #tận dụng thực tế rằng các sprite ma quái nằm trong một lưới và tải tất cả các sprite ma quái cùng một lúc
    def load_ghost_sprites(self):
        #khởi tạo dict
        ghost_sprites = {
            'blinky': None,
            'pinky': None,
            'inky': None,
            'clyde': None,
            'frightened': None,
        }

         #thêm các sprite ma quái chính
        for ghost_row in range(4):
            sprites = dict()
            sprite_list = []
            for ghost_col in range(8):
                #lấy sprite cho mỗi ma quái
                sprite = self.get_sprite(456 + ghost_col*16, 64 + ghost_row*16, 16, 16)
                #tỷ lệ sprite
                sprite = self.scale_sprite(sprite)
                #thêm sprite vào danh sách
                sprite_list.append(sprite)


                #gán hướng đúng
                if ghost_col == 1:
                    sprites['right'] = sprite_list
                    #reset list
                    sprite_list = []
                elif ghost_col == 3:
                    sprites['left'] = sprite_list
                    #reset list
                    sprite_list = []

                elif ghost_col == 5:
                    sprites['up'] = sprite_list
                    #reset list
                    sprite_list = []

                elif ghost_col == 7:
                    sprites['down'] = sprite_list
                    #reset list
                    sprite_list = []


            #gán sprite cho ma quái đúng
            if ghost_row == 0:
                ghost_sprites['blinky'] = sprites
            elif ghost_row == 1:
                ghost_sprites['pinky'] = sprites
            elif ghost_row == 2:
                ghost_sprites['inky'] = sprites
            elif ghost_row == 3:
                ghost_sprites['clyde'] = sprites

        #tải các sprite ma quái bị sợ hãi
        scared_sprites = []
        for i in range(4):
            sprite = self.get_sprite(584 + i*16, 64, 16, 16)
            sprite = self.scale_sprite(sprite)
            scared_sprites.append(sprite)
        ghost_sprites['frightened'] = scared_sprites

        #thêm các sprite ma quái chết cho mỗi ma quái, đây là đôi mắt nổi
        for i in range(4):
            sprite = self.get_sprite(584 + i*16, 80, 16, 16)
            sprite = self.scale_sprite(sprite)
            for ghost in ghost_sprites:
                if ghost != 'frightened':
                    for direction in ghost_sprites[ghost]:
                        ghost_sprites[ghost][direction].append(sprite)



        return ghost_sprites

    def load_pacman_sprites(self):
        pacman_sprites = {
            'right': [self.get_sprite(456, 0, 16, 16),self.get_sprite(472, 0, 16, 16)],
            'left': [self.get_sprite(456, 16, 16, 16),self.get_sprite(472, 16, 16, 16)],
            'up': [self.get_sprite(456, 32, 16, 16),self.get_sprite(472, 32, 16, 16)],
            'down': [self.get_sprite(456, 48, 16, 16),self.get_sprite(472, 48, 16, 16)],
            'start': [self.get_sprite(488, 0, 16, 16)],
            'death': []
        }
        #11 giai đoạn của hoạt ảnh cái chết, tận dụng thực tế rằng các sprite nằm trong một lưới
        for i in range(11):
            pacman_sprites['death'].append(self.get_sprite(504 + i*16, 0, 16, 16))
        return pacman_sprites

    def load_sprites(self):
        #lưu hoạt ảnh sprite pacman, chỉ số 0 là miệng mở và chỉ số 1 là miệng đóng
        pacman_sprites = self.load_pacman_sprites()
        ghost_sprites = self.load_ghost_sprites()

        background_sprites = {
            'background': self.get_sprite(228, 0, 225, 250),
            'pellet': self.get_sprite(8, 8, 8, 8),
            'power_pellet': self.get_sprite(8, 24, 8, 8),
            'cherry': self.get_sprite(490, 50, 15, 15),
        }

        # Scale to be more visible in display
        self.scale_sprites(pacman_sprites)
        self.scale_sprites(background_sprites)
        #ghost sprites already scaled in load function

        return pacman_sprites, ghost_sprites, background_sprites



'''
PACMAN CLASSES ALL GO BELOW HERE
'''

class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    STOP = 5

#types of elements that can be fgound in the maze
class elements(Enum):
    WALL = '#'
    EMPTY = ' '
    PELLET = 'p'
    POWER_PELLET = 'o'
    PACMAN = 'C'
    GHOST = 'G'
    CHERRY = 'c'

#Moveable objects consist of pacman and the ghosts and are any sprite that can move
class Moveable:
    def __init__(self, position, sprites, setup):
        #tuple of the position of the center of the object in terms of pixels of the unscaled sprite
        #tuple of the position of pacman in terms of cells in the maze
        self.position = position
        #integer between 0-8 representing the subposition of pacman in the cell in terms of pixels from the center of tile he is
        self.subposition = (0,5)
        self.direction = Direction.STOP
        #array of sprites with thier different orientations
        self.sprites = sprites
        #alternate between movement animations
        self.open = False
        #keep track of displaying if frightened
        self.flash = False
        self.setup = setup

    #determine current displacemendt covered in one screen by pacman according to his curret speed
    def displacement(self): 
        speed = 1
        time = 1
        return int(speed*time)

    #check if object can change direction and if so change direction, returns true if can turn and false if cannot
    def change_direction(self, direction, maze):
        #check if object is next to wall and if so do not allow him to change direction
        x, y = self.position
        sub_x, sub_y = self.subposition

        #special cases for tunnel
        if x == maze.tunnel_left[0] and y == maze.tunnel_left[1]:
            if  direction == Direction.LEFT or direction == Direction.RIGHT:
                self.direction = direction
                return True
            else:
                return False
        elif x == maze.tunnel_right[0] and y == maze.tunnel_right[1]:
            if  direction == Direction.LEFT or direction == Direction.RIGHT:
                self.direction = direction
                return True
            else:
                return False

        #check if pacman can turn in, if not then buffer that move
        if direction == Direction.UP and sub_x==0 and maze.maze_elems[y-1][x] != elements.WALL:
            self.direction = direction
        elif direction == Direction.DOWN and sub_x==0 and maze.maze_elems[y+1][x] != elements.WALL:
            self.direction = direction
        elif direction == Direction.LEFT and sub_y==0 and maze.maze_elems[y][x-1] != elements.WALL:
            self.direction = direction
        elif direction == Direction.RIGHT and sub_y==0 and maze.maze_elems[y][x+1] != elements.WALL:
            self.direction = direction
        else:
            return False
        return True

    #move the sprite during a frame based on its current direction
    def move(self, maze):
        x, y = self.position
        sub_x, sub_y = self.subposition
        #change orientation of sprite based on where he is trying to move
        direction = self.direction

        #check if the next position is a wall and if not move to that position
        if direction == Direction.UP:
            #at edge of cell move to next cell
            if sub_y == 0 and sub_x == 0 and maze.maze_elems[y - 1][x] != elements.WALL:
                self.position = (x, y - 1)
                #reset sub_y to 15 to move to the bottom of the cell
                self.subposition = (sub_x, 8)
                #change the mouth state for animation
                self.open = not self.open
                #alternate flashing in frightened mode
                self.flash = not self.flash
            else:
                #cannot make sub positio below 0
                self.subposition = (sub_x,max(sub_y - self.displacement(),0))

        elif direction ==  Direction.DOWN and maze.maze_elems[y + 1][x] != elements.WALL:
            #at edge of cell move to next cell
            if sub_y == 8 and sub_x == 0:
                self.position = (x, y + 1)
                #reset sub_y to 0 to move to the top of the cell
                self.subposition = (sub_x, 0)
                #change the mouth state for animation
                self.open = not self.open
                #alternate flashing in frightened mode
                self.flash = not self.flash
            elif sub_x == 0:
                self.subposition = (sub_x, min(sub_y + self.displacement(),8))

        elif direction == Direction.LEFT:
            #special case for tunnel
            if x == maze.tunnel_left[0] and y == maze.tunnel_left[1]:
                if sub_x == 0 and sub_y==0:
                    self.position = maze.tunnel_right
                    self.subposition = (8, sub_y)
                else:
                    self.subposition = (max(sub_x - self.displacement(), 0), sub_y)

            #at edge of cell move to next cell
            elif sub_x == 0 and sub_y==0 and maze.maze_elems[y][x - 1] != elements.WALL:
                self.position = (x - 1, y)
                #reset sub_x to 15 to move to the right of the cell
                self.subposition = (8, sub_y)
                #change the mouth state for animation
                self.open = not self.open
                #alternate flashing in frightened mode
                self.flash = not self.flash
            elif sub_y == 0:
                self.subposition = (max(sub_x - self.displacement(), 0), sub_y)

        elif direction == Direction.RIGHT:
            #special case for tunnel
            if x == maze.tunnel_right[0] and y == maze.tunnel_right[1]:
                if sub_x == 8 and sub_y==0:
                    self.position = maze.tunnel_left
                    self.subposition = (0, sub_y)
                else:
                    self.subposition = (min(sub_x + self.displacement(),8), sub_y)

            #at edge of cell move to next cell
            elif sub_x == 8 and sub_y==0 and maze.maze_elems[y][x + 1] != elements.WALL:
                self.position = (x + 1, y)
                #reset sub_x to 0 to move to the left of the cell
                self.subposition = (0, sub_y)
                #change the mouth state for animation
                self.open = not self.open
                #alternate flashing in frightened mode
                self.flash = not self.flash
            elif sub_y == 0 and maze.maze_elems[y][x + 1] != elements.WALL:
                self.subposition = (min(sub_x + self.displacement(),8), sub_y)

    '''
    hellped function to check if the buffered direction is opposite a direction you
    are travelling and if so remove the buffered direction, this is done
    to avoid weird corner glitches as if you are taking a cornner with a floor below you 
    and you have a down move buffered the second you try to go up you will now be able to execute
    the buffered down move meaning you will go up then immediatlly reset your position

    ALso helps in ghosts to avoid them turning around and tracing back their steps
    '''
    def check_opposite_drection(self, new_direction):
        if self.direction == Direction.UP and new_direction == Direction.DOWN:
            new_direction = Direction.STOP
        elif self.direction == Direction.DOWN and new_direction == Direction.UP:
            new_direction = Direction.STOP
        elif self.direction == Direction.LEFT and new_direction == Direction.RIGHT:
            new_direction = Direction.STOP
        elif self.direction == Direction.RIGHT and new_direction == Direction.LEFT:
            new_direction = Direction.STOP
        #return true if the buffered move is opposite the current direction, and false otherwise
        else:
            return False
        return True

    def display(self, screen):
        x,y = self.position
        sub_x, sub_y = self.subposition

        sprite = None
        #choose sprite based on whether mouth is open or closed and the direction pacman is facing
        if self.direction == Direction.UP:
            if self.open:
                sprite = self.sprites['up'][0]
            else:
                sprite = self.sprites['up'][1]
        elif self.direction == Direction.DOWN:
            if self.open:
                sprite = self.sprites['down'][0]
            else:
                sprite = self.sprites['down'][1]
        elif self.direction == Direction.LEFT:
            if self.open:
                sprite = self.sprites['left'][0]
            else:
                sprite = self.sprites['left'][1]

        #start the game facing right in the stop direction
        elif self.direction == Direction.RIGHT or self.direction == Direction.STOP:
            if self.open:
                sprite = self.sprites['right'][0]
            else:
                sprite = self.sprites['right'][1]

        #since position is at the center point of pacman we need to adjust the position to the top left corner of the spritea
        screen.blit(sprite, ((x*8+sub_x-4)*self.setup.SCALE, (y*8+sub_y-4)*self.setup.SCALE))

    #check if object runs into another movable object, returns true if there is a collision and false otherwise
    def collision(self, other : 'Ghost'):
        #if ghost is already eaten by pacman do not collide with him
        if self.position == other.position and not other.is_eaten:
            return True
        else:
            return False

class Pacman(Moveable):
    def __init__(self, sprites, player, setup):
        self.setup = setup
        starting_position = setup.PACMAN_START
        #construct a moveable object with the starting position
        super().__init__(starting_position, sprites, setup)
        super().__init__(setup.PACMAN_START, sprites, setup)
        self.is_invincible = False  # Ban đầu không tàng hình
        self.invincibility_timer = 0  # Bộ đếm thời gian tàng hình
        #change sub position for display
        self.subposition = (5,0)
        #player who controls pacman
        self.player = player

        #dictionry containing all the different sprites for the different directions
        self.sprites = sprites

        '''
        input buffering, if the player tries to change direction and pacman is not able to change direction at that time
        save the direction the player wants to go in and change direction when pacman is able to
        '''
        self.buffered = Direction.STOP

        #keep track of whether pacman is supercharged py power pellet or not
        self.is_supercharged = False

        #alternate wether mouth is open or closed for animation
        self.open = True

        #timer for determining when to play eating sound effect
        self.eating_timer = Stopwatch()
        self.eat_time = 0.15


    #reset pacman to starting position
    def reset(self):
        self.position = self.setup.PACMAN_START
        self.direction = Direction.STOP
        self.subposition = (0,0)
        self.buffered = Direction.STOP
        self.is_supercharged = False

    #override inherrented change directiojn to include buffering inputs
    #check to make sure pacman can change to the intended direction and change if able, return true if can turn return false if cannot
    def change_direction(self, direction, maze):
        #check if pacman is next to wall and if so do not allow him to change direction
        x, y = self.position
        sub_x, sub_y = self.subposition

        #prevent buffered moves in the opposite direction from executing, see more information at actual function definition
        if super().check_opposite_drection(self.buffered):
            self.buffered = Direction.STOP
            return False

        #spec`ial case for tunnel
        if x == maze.tunnel_left[0] and y == maze.tunnel_left[1]:
            if  direction == Direction.LEFT or direction == Direction.RIGHT:
                self.direction = direction
                return True
            else:
                self.buffered = direction
                return False
        elif x == maze.tunnel_right[0] and y == maze.tunnel_right[1]:
            if  direction == Direction.LEFT or direction == Direction.RIGHT:
                self.direction = direction
                return True
            else:
                self.buffered = direction
                return False

        #check if pacman can turn in, if not then buffer that move
        if direction == Direction.UP and sub_x==0 and maze.maze_elems[y-1][x] != elements.WALL:
            self.direction = direction
        elif direction == Direction.DOWN and sub_x==0 and maze.maze_elems[y+1][x] != elements.WALL:
            self.direction = direction
        elif direction == Direction.LEFT and sub_y==0 and maze.maze_elems[y][x-1] != elements.WALL:
            self.direction = direction
        elif direction == Direction.RIGHT and sub_y==0 and maze.maze_elems[y][x+1] != elements.WALL:
            self.direction = direction
        #can't turn
        else:
            #set buffered direction
            self.buffered = direction
            return False
        #did turn
        return True


    #slighlty override parent move function to also implement eating pellets
    def move(self, maze):
        super().move(maze)
        #eat pellet if there is one at that position
        self.eat(maze.maze_elems)

    def eat(self, maze):
        x, y = self.position
        #eat the pellet if there is one at the position by incrementing score and removing the pellet
        if maze[y][x] == elements.PELLET:
            maze[y][x] = elements.EMPTY
            self.player.score += 10
            # Play pellet eating sound effect only if not alread playing
            if self.eating_timer.start_time == None or self.eating_timer.get_elapsed_time() == 0:
                #Turn off eating sound REMOVE LATER TO PLAY REGULARLY
                # SoundEffects.eating_channel.play(SoundEffects.eating_effect)
                self.eating_timer.start()
            elif self.eating_timer.get_elapsed_time() >= self.eat_time:
                self.eating_timer.stop()

        #eat the power pellet if there is one at the position by incrementing score and removing the pellet and making pacman supercharged
        if maze[y][x] == elements.POWER_PELLET:
            maze[y][x] = elements.EMPTY
            self.player.score += 50
            self.is_supercharged = True

        #eat the cherry for an additional 100 points
        if maze[y][x] == elements.CHERRY:
            #play cherry noise
            #REMOVE CHERRY NOISE ADD LATER
            #SoundEffects.cherry_channel.play(SoundEffects.cherry_effect)
            maze[y][x] = elements.EMPTY
            self.player.score += 100


    def display(self, screen):
        if not self.is_invincible or (int(time.time() * 2) % 2 == 0):  # Nhấp nháy khi tàng hình
            super().display(screen)

        #display text
        font = pyg.font.Font(None, 36)
        text = self.setup.ARCADE_FONT.render(f'Score: {self.player.score}', True, (255, 255, 255))
        screen.blit(text, (10, self.setup.SCREEN_HEIGHT - 90))
        # Hiển thị trái tim tương ứng với số mạng
        for i in range(self.player.lives):
            screen.blit(self.setup.heart_sprite, (10 + i * 30, self.setup.SCREEN_HEIGHT - 30))

        text = self.setup.ARCADE_FONT.render(f'SC?: {self.is_supercharged}', True, (255, 255, 255))
        screen.blit(text, (250, self.setup.SCREEN_HEIGHT - 30))

        # text = ARCADE_FONT.render(f'Direction: {self.direction}', True, (255, 255, 255))
        # screen.blit(text, (10, SCREEN_HEIGHT - 30))
        # text = ARCADE_FONT.render(f'Buffered: {self.buffered}', True, (255, 255, 255))
        # screen.blit(text, (350, SCREEN_HEIGHT - 30))


class Ghost(Moveable):
    def __init__(self, color, sprites, frightened_sprites, setup):
        self.setup = setup
        #every ghost except blinky starts in cage
        self.position = self.setup.CAGE_CORDS
        super().__init__(self.position, sprites, setup)
        self.frightened_sprites = frightened_sprites
        self.sub_position = (0,0)
        self.color = color
        self.sprites = sprites
        self.direction = Direction.STOP

        #every ghost has a target tile they want to reach and, this determiens the direction they will move in
        self.target_tile = (0,0)
        #every ghost has a scatter tile they want to reach when they are in scatter mode
        self.scatter_tile = (0,0)

        self.mode = 'chase'

        self.left_cage = False

        #additional fields for when the ghost is eaten by pacman in frightened mode
        self.is_eaten = False


    
    #reset the ghost to the cage after pacman death
    def reset(self):
        self.position = self.setup.CAGE_CORDS
        self.direction = Direction.STOP
        self.subposition = (0,0)
        self.mode = 'chase'
        self.left_cage = False

    #move the ghost out of the cage, to start chasign the player
    def leave_cage(self, maze):
        #first naviagate to the center of the cage
        if self.position != self.setup.CAGE_CORDS:
            self.target_tile = self.setup.CAGE_CORDS
            self.choose_direction(maze)
            self.move(maze)
        
        #if the ghost is in the middle of the cage forciblly move him out of the cage
        elif self.position == self.setup.CAGE_CORDS:
            self.position = (self.position[0], self.position[1] - 2)
            self.subposition = (0,0)
            self.direction = Direction.UP
            self.left_cage = True

    #every ghost has a different chase algorithm that will be overriden by the subclass
    #determines the target tile for the ghost to move to
    def chase(self, pacman, graph):
        pass

    def scatter(self):
        self.target_tile = self.scatter_tile
    
    #will determine the direction the ghost will move in to catch pacman
    def choose_direction(self, maze):
        #determine possible directions (neighbors of the current position)
        possible_tiles = maze.graph[self.position]
        #dtermine the possible directions the ghost can move in based on the tiles available to him
        possible_directions = {
            Direction.UP: None,
            Direction.DOWN: None,
            Direction.LEFT: None,
            Direction.RIGHT: None
        }

        #figure out what directions the ghost must move in to get to that tile
        #special tunnel cases
        if self.position == maze.tunnel_left:
            possible_directions[Direction.LEFT] = maze.tunnel_right
        elif self.position == maze.tunnel_right:
            possible_directions[Direction.RIGHT] = maze.tunnel_left

        for tile in possible_tiles:            
            if tile[0] == self.position[0] and tile[1] < self.position[1]:
                possible_directions[Direction.UP] = tile
            elif tile[0] == self.position[0] and tile[1] > self.position[1]:
                possible_directions[Direction.DOWN] = tile
            elif tile[1] == self.position[1] and tile[0] < self.position[0]:
                possible_directions[Direction.LEFT] = tile
            elif tile[1] == self.position[1] and tile[0] > self.position[0]:
                possible_directions[Direction.RIGHT] = tile

        #determine the distance to the target tile for each possible direction
        directions = {
            Direction.UP: None,
            Direction.DOWN: None,
            Direction.LEFT: None,
            Direction.RIGHT: None
        }

        for direction in directions:
            #can't choose to reverse direction or turn somewhere you cannot go
            if possible_directions[direction] is None or super().check_opposite_drection(direction):
                directions[direction] = float('inf')
            else:
                #distance from possible tile to target tile
                directions[direction] = self.distance(possible_directions[direction], self.target_tile)
            #choose lowest cost direction to travel
        #print(directions)
        optimal_direction = min(directions, key=directions.get)
        #if have reached edge of tile to turn that way do so, if not then wait 
        self.change_direction(optimal_direction, maze)
        

    #determine the euclidean distance between two points
    def distance(self, start, end):
        return ((start[0] - end[0])**2 + (start[1] - end[1])**2)**0.5
    
    #override display functionallity to include frightened mode
    def display(self, screen, flash):
        #regular display if not frightened
        if self.mode != 'frightened':
            super().display(screen)
        
        #ghost is eaten by pacman, display eyes
        elif self.is_eaten:
            x,y = self.position
            sub_x, sub_y = self.subposition
            
            sprite = None
            #choose sprite based on whether mouth is open or closed and the direction pacman is facing
            if self.direction == Direction.UP:
                sprite = self.sprites['up'][2]
            elif self.direction == Direction.DOWN:
                sprite = self.sprites['down'][2]
            elif self.direction == Direction.LEFT:
                sprite = self.sprites['left'][2]
            #start the game facing right in the stop direction
            elif self.direction == Direction.RIGHT or self.direction == Direction.STOP:
                sprite = self.sprites['right'][2]
            #since position is at the center point of pacman we need to adjust the position to the top left corner of the spritea
            screen.blit(sprite, ((x*8+sub_x-4)*self.setup.SCALE, (y*8+sub_y-4)*self.setup.SCALE))
        
        #display frightened mode
        elif self.mode == 'frightened':
            x,y = self.position
            sub_x, sub_y = self.subposition
            sprite = None

            #during regular frightened mode the ghost will alternate between the two blue sprites
            #when the ghost starts flashing the sprite will alternate between the four sprites, 2 flashing sprites and the 2 blue sprites
            if not flash or not self.flash:
                if open:
                    sprite = self.frightened_sprites[0]
                else:
                    sprite = self.frightened_sprites[1]


            elif self.flash and flash:
                if open:
                    sprite = self.frightened_sprites[2]
                else:
                    sprite = self.frightened_sprites[3]

            #since position is at the center point of pacman we need to adjust the position to the top left corner of the spritea
            screen.blit(sprite, ((x*8+sub_x-4)*self.setup.SCALE, (y*8+sub_y-4)*self.setup.SCALE))

    #during firghtened mode the ghost will move in the opposite direction
    def reverse_direction(self):
        if self.direction == Direction.UP:
            self.direction = Direction.DOWN
        elif self.direction == Direction.DOWN:
            self.direction = Direction.UP
        elif self.direction == Direction.LEFT:
            self.direction = Direction.RIGHT
        elif self.direction == Direction.RIGHT:
            self.direction = Direction.LEFT

    #enter firghted mode and reverse direction
    def make_frightened(self):
        self.mode = 'frightened'
        self.reverse_direction()

    #randomly choose a direction at interesection to move in when firghtened, if not at intersection keep moving straight
    def frightened(self, maze):
        #determine possible directions (neighbors of the current position)
        possible_tiles = maze.graph[self.position]
        #dtermine the possible directions the ghost can move in based on the tiles available to him
        possible_directions = {
            Direction.UP: None,
            Direction.DOWN: None,
            Direction.LEFT: None,
            Direction.RIGHT: None
        }
        #figure out what directions the ghost must move in to get to that tile

        #special tunnel cases
        if self.position == maze.tunnel_left:
            possible_directions[Direction.LEFT] = maze.tunnel_right
        elif self.position == maze.tunnel_right:
            possible_directions[Direction.RIGHT] = maze.tunnel_left

        for tile in possible_tiles:            
            if tile[0] == self.position[0] and tile[1] < self.position[1]:
                possible_directions[Direction.UP] = tile
            elif tile[0] == self.position[0] and tile[1] > self.position[1]:
                possible_directions[Direction.DOWN] = tile
            elif tile[1] == self.position[1] and tile[0] < self.position[0]:
                possible_directions[Direction.LEFT] = tile
            elif tile[1] == self.position[1] and tile[0] > self.position[0]:
                possible_directions[Direction.RIGHT] = tile

        #choose random direction
        directions = [direction for direction in possible_directions if possible_directions[direction] is not None and not super().check_opposite_drection(direction)]
        #if have reached edge of tile to turn that way do so, if not then wait 
        self.change_direction(random.choice(directions), maze)



    def update(self, pacman, maze, *args):
        if self.mode == 'chase':
            self.chase(pacman, maze, *args)
            self.choose_direction(maze)
            self.move(maze)
        elif self.mode == 'scatter':
            self.scatter()
            self.choose_direction(maze)
            self.move(maze)
        elif self.mode == 'frightened':
            if self.is_eaten and self.position != self.setup.BLINKY_CAGE_CORDS:
                self.target_tile = self.setup.BLINKY_CAGE_CORDS
                self.choose_direction(maze)
                self.move(maze)
            elif self.is_eaten and self.position == self.setup.BLINKY_CAGE_CORDS:
                self.is_eaten = False
                self.mode = 'chase'
            else:
                self.frightened(maze)
                self.move(maze)


# Blinky - Thuật toán DFS (Depth-First Search)
class Blinky(Ghost):
    def __init__(self, sprite, frightened_sprites,setup):
        super().__init__('red', sprite, frightened_sprites,setup)
        self.speed = 0.5  # Blinky nhanh nhất
        self.position = setup.BLINKY_CAGE_CORDS
        self.left_cage = True
        self.scatter_tile = 25, -3
        self.visited = set()
        self.stack = []

    def reset(self):
        super().reset()
        self.visited = set()
        self.stack = []

    def chase(self, pacman, maze):
        # DFS implementation
        start = self.position
        target = pacman.position
        
        if not self.stack or self.stack[-1] != target:
            self.stack = []
            self.visited = set()
            self.dfs(maze.graph, start, target, [start])
        
        if self.stack:
            next_pos = self.stack.pop()
            dx = next_pos[0] - start[0]
            dy = next_pos[1] - start[1]
            
            if dx == 1: self.target_tile = (start[0]+1, start[1])
            elif dx == -1: self.target_tile = (start[0]-1, start[1])
            elif dy == 1: self.target_tile = (start[0], start[1]+1)
            elif dy == -1: self.target_tile = (start[0], start[1]-1)

    def dfs(self, graph, node, target, path):
        if node == target:
            self.stack = path[1:]  # Exclude current position
            return True
            
        self.visited.add(node)
        
        for neighbor in graph[node]:
            if neighbor not in self.visited:
                if self.dfs(graph, neighbor, target, path + [neighbor]):
                    return True
        return False
#Pinky - Thuật toán BFS (Breadth-First Search)    
class Pinky(Ghost):
    def __init__(self, sprite, frightened_sprites, setup):
        super().__init__('pink', sprite, frightened_sprites, setup)
        self.speed = 0.5
        self.scatter_tile = (2,-3)
        self.queue = []
        self.parent = {}
        self.path = []

    def reset(self):
        super().reset()
        self.queue = []
        self.parent = {}
        self.path = []

    def chase(self, pacman, maze):
        # BFS implementation
        start = self.position
        target = pacman.position
        
        if not self.path:
            self.bfs(maze.graph, start, target)
        
        if self.path:
            next_pos = self.path.pop(0)
            self.target_tile = next_pos

    def bfs(self, graph, start, target):
        visited = set()
        queue = []
        queue.append(start)
        visited.add(start)
        self.parent = {start: None}
        
        found = False
        while queue:
            node = queue.pop(0)
            
            if node == target:
                found = True
                break
                
            for neighbor in graph[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    self.parent[neighbor] = node
                    queue.append(neighbor)
        
        if found:
            self.path = []
            node = target
            while node != start:
                self.path.insert(0, node)
                node = self.parent[node]
            if len(self.path) > 1:
                self.path = self.path[:1]  # Only take next step
#Inky - Thuật toán A* (A-Star)
class Inky(Ghost):
    def __init__(self, sprite, frightened_sprites, setup):
        super().__init__('cyan', sprite, frightened_sprites, setup)
        self.speed = 0.5
        self.scatter_tile = (27, 33)
        self.open_set = set()
        self.came_from = {}
        self.g_score = {}
        self.f_score = {}

    def reset(self):
        super().reset()
        self.open_set = set()
        self.came_from = {}
        self.g_score = {}
        self.f_score = {}

    def chase(self, pacman, maze, blinky):
        # A* implementation
        start = self.position
        # Calculate target using Blinky's position
        initial_target = (pacman.position[0] + 2*(pacman.position[0] - blinky.position[0]), 
                         pacman.position[1] + 2*(pacman.position[1] - blinky.position[1]))
        target = initial_target
        
        path = self.a_star(maze.graph, start, target)
        if path and len(path) > 1:
            self.target_tile = path[1]

    def heuristic(self, a, b):
        # Manhattan distance
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def a_star(self, graph, start, goal):
        self.open_set = {start}
        self.came_from = {}
        
        self.g_score = {start: 0}
        self.f_score = {start: self.heuristic(start, goal)}
        
        while self.open_set:
            current = min(self.open_set, key=lambda pos: self.f_score.get(pos, float('inf')))
            
            if current == goal:
                path = []
                while current in self.came_from:
                    path.append(current)
                    current = self.came_from[current]
                path.reverse()
                return path
                
            self.open_set.remove(current)
            
            for neighbor in graph[current]:
                tentative_g_score = self.g_score.get(current, float('inf')) + 1
                
                if tentative_g_score < self.g_score.get(neighbor, float('inf')):
                    self.came_from[neighbor] = current
                    self.g_score[neighbor] = tentative_g_score
                    self.f_score[neighbor] = self.g_score[neighbor] + self.heuristic(neighbor, goal)
                    if neighbor not in self.open_set:
                        self.open_set.add(neighbor)
        
        return []  # No path found
#Clyde - Thuật toán UCS (Uniform Cost Search)
class Clyde(Ghost):
    def __init__(self,sprite, frightened_sprites, setup):
        super().__init__('orange', sprite, frightened_sprites, setup)
        self.speed = 0.4  # Clyde chậm nhất
        self.scatter_tile = (0,33)
        self.priority_queue = []
        self.came_from = {}
        self.cost_so_far = {}

    def reset(self):
        super().reset()
        self.priority_queue = []
        self.came_from = {}
        self.cost_so_far = {}

    def chase(self, pacman, maze):
        # UCS implementation
        start = self.position
        target = pacman.position
        
        # Original Clyde behavior: switch to scatter if close to Pacman
        if self.distance(self.position, pacman.position) < 8:
            self.scatter()
            return
            
        path = self.ucs(maze.graph, start, target)
        if path and len(path) > 1:
            self.target_tile = path[1]

    def ucs(self, graph, start, goal):
        self.priority_queue = []
        heapq.heappush(self.priority_queue, (0, start))
        self.came_from = {start: None}
        self.cost_so_far = {start: 0}
        
        while self.priority_queue:
            current_cost, current = heapq.heappop(self.priority_queue)
            
            if current == goal:
                break
                
            for neighbor in graph[current]:
                new_cost = self.cost_so_far[current] + 1  # All edges have cost 1
                
                if neighbor not in self.cost_so_far or new_cost < self.cost_so_far[neighbor]:
                    self.cost_so_far[neighbor] = new_cost
                    heapq.heappush(self.priority_queue, (new_cost, neighbor))
                    self.came_from[neighbor] = current
        
        # Reconstruct path
        path = []
        current = goal
        while current != start:
            path.append(current)
            current = self.came_from.get(current)
            if current is None:  # No path found
                return []
        path.append(start)
        path.reverse()
        return path

    


class Background:
    def __init__(self, sprite):
        self.sprite = sprite



#represents the maze and its walls
class Maze:
    def __init__(self, sprites, setup):
        self.setup = setup
        #load all the sprites for the maze background such as the pellet, power pellet and the background itself
        self.sprites = sprites
        '''
        maze boudary itself is represented by 2d binary array where 1 represents a wall and a 0 represents a movable space type of element
        manually initializing the initial maze
        '''
        self.maze_boundaries = [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1], #0
            [1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1], #1
            [1,0,1,1,1,1,0,1,1,1,1,1,0,1,1,0,1,1,1,1,1,0,1,1,1,1,0,1], #2
            [1,0,1,1,1,1,0,1,1,1,1,1,0,1,1,0,1,1,1,1,1,0,1,1,1,1,0,1], #3
            [1,0,1,1,1,1,0,1,1,1,1,1,0,1,1,0,1,1,1,1,1,0,1,1,1,1,0,1], #4
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1], #5
            [1,0,1,1,1,1,0,1,1,0,1,1,1,1,1,1,1,1,0,1,1,0,1,1,1,1,0,1], #6
            [1,0,1,1,1,1,0,1,1,0,1,1,1,1,1,1,1,1,0,1,1,0,1,1,1,1,0,1], #7
            [1,0,0,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,0,1], #8
            [1,1,1,1,1,1,0,1,1,1,1,1,0,1,1,0,1,1,1,1,1,0,1,1,1,1,1,1], #9
            [1,1,1,1,1,1,0,1,1,1,1,1,0,1,1,0,1,1,1,1,1,0,1,1,1,1,1,1], #10
            [1,1,1,1,1,1,0,1,1,0,0,0,0,0,0,0,0,0,0,1,1,0,1,1,1,1,1,1], #11
            [1,1,1,1,1,1,0,1,1,0,1,1,1,1,1,1,1,1,0,1,1,0,1,1,1,1,1,1], #12
            [1,1,1,1,1,1,0,1,1,0,1,0,0,0,0,0,0,1,0,1,1,0,1,1,1,1,1,1], #13
            [0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0], #14
            [1,1,1,1,1,1,0,1,1,0,1,0,0,0,0,0,0,1,0,1,1,0,1,1,1,1,1,1], #15
            [1,1,1,1,1,1,0,1,1,0,1,1,1,1,1,1,1,1,0,1,1,0,1,1,1,1,1,1], #16
            [1,1,1,1,1,1,0,1,1,0,0,0,0,0,0,0,0,0,0,1,1,0,1,1,1,1,1,1], #17
            [1,1,1,1,1,1,0,1,1,0,1,1,1,1,1,1,1,1,0,1,1,0,1,1,1,1,1,1], #18
            [1,1,1,1,1,1,0,1,1,0,1,1,1,1,1,1,1,1,0,1,1,0,1,1,1,1,1,1], #19
            [1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1], #20
            [1,0,1,1,1,1,0,1,1,1,1,1,0,1,1,0,1,1,1,1,1,0,1,1,1,1,0,1], #21
            [1,0,1,1,1,1,0,1,1,1,1,1,0,1,1,0,1,1,1,1,1,0,1,1,1,1,0,1], #22
            [1,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,1], #23
            [1,1,1,0,1,1,0,1,1,0,1,1,1,1,1,1,1,1,0,1,1,0,1,1,0,1,1,1], #24
            [1,1,1,0,1,1,0,1,1,0,1,1,1,1,1,1,1,1,0,1,1,0,1,1,0,1,1,1], #25
            [1,0,0,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,0,1], #26
            [1,0,1,1,1,1,1,1,1,1,1,1,0,1,1,0,1,1,1,1,1,1,1,1,1,1,0,1], #27
            [1,0,1,1,1,1,1,1,1,1,1,1,0,1,1,0,1,1,1,1,1,1,1,1,1,1,0,1], #28
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1], #29
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1], #30
        ]

        #keep track of where pellets are on the maze
        self.maze_elems = [[elements.EMPTY for x in range(self.setup.X_CELLS)] for y in range(self.setup.Y_CELLS)]
        #start with the pellets in their initial positions
        self.fill_maze()

        #define tunnel points where pacman can pass through
        self.tunnel_points = [(0,14), (27,14)]
        self.tunnel_left = self.tunnel_points[0]
        self.tunnel_right = self.tunnel_points[1]
        
        #graphical representation of the maze for the ghosts path finding
        self.graph = self.construct_graph()

    #completely reset the maze without reloading the sprites
    def reset(self):
        self.maze_elems = [[elements.EMPTY for x in range(self.setup.X_CELLS)] for y in range(self.setup.Y_CELLS)]
        self.fill_maze()

    #color all collision objects in the maze
    def debug_display_maze(self, screen):
        for y in range(len(self.maze_boundaries)):
            for x in range(len(self.maze_boundaries[y])):
                if self.maze_boundaries[y][x] == 1:
                    pyg.draw.rect(screen, (random.randint(0,255), random.randint(0,255), random.randint(0,255)), (x*8*self.setup.SCALE, y*8*self.setup.SCALE, 8*self.setup.SCALE, 8*self.setup.SCALE))
        pyg.display.flip()

    #fill maze with the correct ellements
    def fill_maze(self):
        for y in range(self.setup.Y_CELLS):
            for x in range(self.setup.X_CELLS):
                #place wall objects at boundaries 
                if self.maze_boundaries[y][x] == 1:
                    self.maze_elems[y][x] = elements.WALL

                #place power pellets in their 4 spawning positions
                elif (y == 3 or y == 23) and (x == 1 or x == 26):
                    self.maze_elems[y][x] = elements.POWER_PELLET

                #place col of pellets that goes through middle of maze
                elif x == 6 or x == 21:
                    self.maze_elems[y][x] = elements.PELLET
                
                #pellets are placed in every empty slot except for the ghost cage and the tunnel and the middle
                elif y < 9 or y > 19:
                    self.maze_elems[y][x] = elements.PELLET
                else:
                    self.maze_elems[y][x] = elements.EMPTY
    
    def pellets_eaten(self):
        remaining = 0
        for y in range(self.setup.Y_CELLS):
            for x in range(self.setup.X_CELLS):
                if self.maze_elems[y][x] == elements.PELLET:
                    remaining += 1
        #starts with 240 pellets 240-remaining is the number of pellets he has eaten
        return 240 - remaining

    #place a cherry on the board
    def place_cherry(self):
        placed = False
        #find a random location to place the 
        while not placed:
            random_x = random.randint(0, self.setup.X_CELLS - 1)
            random_y = random.randint(0, self.setup.Y_CELLS - 1)
            #cherry must be placed on an open space, can't be placed inside the cage
            if (not (random_y > 12 and random_y < 16)) and self.maze_elems[random_y][random_x] == elements.EMPTY:
                self.maze_elems[random_y][random_x] = elements.CHERRY
                placed = True
        
    def construct_graph(self):
        graph = {}
        for y in range(self.setup.Y_CELLS):
            for x in range(self.setup.X_CELLS):
                if self.maze_boundaries[y][x] == 0:  # Only consider empty spaces
                    neighbors = []
                    #consider the tunnel as a connection between the two points
                    #special tunnel cases
                    if (x, y) == self.tunnel_left:
                        neighbors.append(self.tunnel_right)
                        neighbors.append((x+1,y))
                    elif (x, y) == self.tunnel_right:
                        neighbors.append(self.tunnel_left)
                        neighbors.append((x-1,y))
                    else:
                        if y > 0 and self.maze_boundaries[y - 1][x] == 0:
                            neighbors.append((x, y - 1))
                        if y < self.setup.Y_CELLS - 1 and self.maze_boundaries[y + 1][x] == 0:
                            neighbors.append((x, y + 1))
                        if x > 0 and self.maze_boundaries[y][x - 1] == 0:
                            neighbors.append((x - 1, y))
                        if x < self.setup.X_CELLS - 1 and self.maze_boundaries[y][x + 1] == 0:
                            neighbors.append((x + 1, y))
                    

                    graph[(x, y)] = neighbors
        return graph


    #display the maze on the screen
    def display(self, screen):
       
        #reset the screen
        screen.fill((0, 0, 0))
        #display the background
        screen.blit(self.sprites['background'], (0, 0))
        #add the pixels and power pellets ontop of background
        for y in range(self.setup.Y_CELLS):
            for x in range(self.setup.X_CELLS):
                if self.maze_elems[y][x] == elements.PELLET:
                    screen.blit(self.sprites['pellet'], (x*8*self.setup.SCALE, y*8*self.setup.SCALE))
                elif self.maze_elems[y][x] == elements.POWER_PELLET:
                    screen.blit(self.sprites['power_pellet'], (x*8*self.setup.SCALE, y*8*self.setup.SCALE))
                elif self.maze_elems[y][x] == elements.CHERRY:
                    screen.blit(self.sprites['cherry'], (x*8*self.setup.SCALE, y*8*self.setup.SCALE))


class Game:
    def draw_game_over_screen(self):
        print("Game Over screen should be displayed!")  # Debug
        # Load the background image
        background_image = pyg.image.load("assets/start_images/over.jpg")
        background_image = pyg.transform.scale(background_image, (self.setup.SCREEN_WIDTH, self.setup.SCREEN_HEIGHT))

        # Fill the screen with the background image
        self.screen.blit(background_image, (0, 0))

        # Render the text
        game_over_text = self.setup.ARCADE_FONT_LARGE.render("Game Over", True, (255, 0, 0))
        reset_text = self.setup.ARCADE_FONT.render("Reset", True, (255, 255, 255))
        quit_text = self.setup.ARCADE_FONT.render("Quit", True, (255, 255, 255))

        # Calculate positions for the text and buttons
        game_over_text_x = (self.setup.SCREEN_WIDTH - game_over_text.get_width()) // 2
        game_over_text_y = self.setup.SCREEN_HEIGHT // 4
        button_width = 200
        button_height = 60
        spacing = 20

        reset_rect_x = (self.setup.SCREEN_WIDTH - button_width) // 2
        reset_rect_y = self.setup.SCREEN_HEIGHT // 2

        quit_rect_x = reset_rect_x
        quit_rect_y = reset_rect_y + button_height + spacing

        # Draw the Game Over text
        self.screen.blit(game_over_text, (game_over_text_x, game_over_text_y))

        # Create button rectangles
        reset_rect = pyg.Rect(reset_rect_x, reset_rect_y, button_width, button_height)
        quit_rect = pyg.Rect(quit_rect_x, quit_rect_y, button_width, button_height)

        # Draw the buttons
        pyg.draw.rect(self.screen, (0, 255, 0), reset_rect)  # Reset button in green
        pyg.draw.rect(self.screen, (255, 0, 0), quit_rect)  # Quit button in red

        # Draw the button text
        self.screen.blit(reset_text, (reset_rect_x + (button_width - reset_text.get_width()) // 2,
                                      reset_rect_y + (button_height - reset_text.get_height()) // 2))
        self.screen.blit(quit_text, (quit_rect_x + (button_width - quit_text.get_width()) // 2,
                                     quit_rect_y + (button_height - quit_text.get_height()) // 2))

        pyg.display.flip()

        while True:
            for event in pyg.event.get():
                print(f"Event detected: {event}")  # Debug để kiểm tra các sự kiện

                if event.type == pyg.QUIT:
                    pyg.quit()
                    sys.exit()
                elif event.type == pyg.MOUSEBUTTONDOWN:
                    print(f"Mouse click at: {event.pos}")  # Debug vị trí nhấp chuột
                    if reset_rect.collidepoint(event.pos):
                        print("Reset button clicked!")  # Debug khi nhấp nút Reset
                        self.reset_game()
                        return
                    elif quit_rect.collidepoint(event.pos):
                        print("Quit button clicked!")  # Debug khi nhấp nút Quit
                        pyg.quit()
                        sys.exit()

    def draw_lives(self):
        for i in range(self.player.lives):
            self.screen.blit(self.setup.heart_sprite, (10 + i * 30, self.setup.SCREEN_HEIGHT - 30))

    def __init__(self, setup, clock, is_displaying):
        self.setup = setup
        self.screen = setup.SCREEN
        #initialize the graphics wiht the sprite sheet containing all images of pacman and ghosts
        graphics = Graphics(self.setup)

        #initialize player and game variables
        self.player = Player('Schools Dollar')
 # Lưu hình trái tim vào Game_Setup để dùng trong draw_lives()
        self.setup.heart_sprite = graphics.heart_sprite
        #set up the sprites
        pacman_sprites, ghost_sprites, background_sprites = graphics.load_sprites()
        self.pacman = Pacman(pacman_sprites, self.player, self.setup)
        self.ghosts = {
            'blinky': Blinky(ghost_sprites['blinky'], ghost_sprites['frightened'],self.setup),
            'pinky': Pinky(ghost_sprites['pinky'], ghost_sprites['frightened'],self.setup),
            'inky': Inky(ghost_sprites['inky'],ghost_sprites['frightened'],self.setup),
            'clyde': Clyde(ghost_sprites['clyde'],ghost_sprites['frightened'],self.setup)
        }
        self.maze = Maze(background_sprites, self.setup)

        self.is_displaying = is_displaying

        self.clock = clock

        #used to keep track of when start animation is playing and when to start the game
        self.start_frame = 0
        self.starting_up = True
        #frame on which the starting animation ends
        self.end_frames = 10

        self.death_frame = 0
        self.death_end_frames = 10

        self.is_dead = False

        #keep track of the game timer
        self.game_timer = Stopwatch()
        self.frightened_timer = Stopwatch()
        #how mnay seconds the ghosts will be frightened for
        self.frightened_time = 10

        #keep track of what mode the ghosts are in
        self.mode = 'scatter'

        #keep track of wether a cherry has been placed or not
        self.cherry_placed = False

        #keep track of when game ends
        self.game_over_bool = False

    #play starting animation and begin game loop
    def start(self):
        #play startup sound starting on first frame
        if(self.start_frame == 0):
            #reset ghost location 
            for ghost in self.ghosts.values():
                ghost.reset()
            #reset pacman location
            self.pacman.reset()

            #only play sound on first round, not on other resets
            if self.player.lives == 3 and self.is_displaying:
                sound = pyg.mixer.Sound(SoundEffects.startup_effect)   
                sound.play()

        if self.is_displaying:
            #play starting animation (which is just pacman waiting for a few seconds)
            self.maze.display(self.screen)
            #since position is at the center point of pacman we need to adjust the position to the top left corner of the spritea
            sprite = self.pacman.sprites['start'][0]
            x,y = self.pacman.position
            sub_x, sub_y = self.pacman.subposition
            self.screen.blit(sprite, ((x*8+sub_x-4)*self.setup.SCALE, (y*8+sub_y-4)*self.setup.SCALE))        
            for ghost in self.ghosts.values():
                ghost.display(self.screen, flash = False)
                
            #render ready text on middle of screen
            text = self.setup.ARCADE_FONT_LARGE.render('READY?', True, (255, 255, 255))
            self.screen.blit(text, (self.setup.SCREEN_WIDTH/2.75, self.setup.SCREEN_HEIGHT/2.1))

        #increment frame counter
        self.start_frame += 1

        #last frame of startup
        if(self.start_frame == self.end_frames - 1):
            #start the background music right as startup ends
            if self.is_displaying:
                SoundEffects.background_channel.play(SoundEffects.background_effect, loops = -1)
            #start game timer
            self.game_timer.start()
            self.starting_up = False
    
    #play the death animation and reset the game
    def reset_round(self):
    # Debug kiểm tra giá trị self.death_end_frames
        print(f"DEBUG: self.death_end_frames = {self.death_end_frames}")

    # Phát âm thanh chết
        if self.death_frame == 0:
            self.game_timer.stop()
            if self.is_displaying:
                SoundEffects.background_channel.stop()
                SoundEffects.eating_channel.stop()
                SoundEffects.startup_channel.stop()
                SoundEffects.death_channel.play(SoundEffects.death_effect)

    # Tránh chia cho 0
        death_animation_steps = max(1, self.death_end_frames // 11)  
        death_sprite_index = min(self.death_frame // death_animation_steps, 10)  
        death_sprite = self.pacman.sprites['death'][death_sprite_index]
    
        self.death_frame += 1

        self.maze.display(self.screen)
        x, y = self.pacman.position
        sub_x, sub_y = self.pacman.subposition
        self.screen.blit(death_sprite, ((x*8+sub_x-4)*self.setup.SCALE, (y*8+sub_y-4)*self.setup.SCALE))        

    # Kiểm tra nếu animation chết đã hoàn thành
        if self.death_frame == self.death_end_frames - 1:
            self.is_dead = False
            self.death_frame = 0
            self.start_frame = 0

        # 🛑 Trừ mạng Pac-Man
            self.player.lives -= 1  

        # 🛑 Kiểm tra số mạng còn lại
            if self.player.lives > 0:
                self.starting_up = True  # Nếu còn mạng, bắt đầu ván mới
                self.pacman.reset()
                for ghost in self.ghosts.values():
                    ghost.reset()
            else:
                self.game_over_bool = True  # Nếu hết mạng, kích hoạt trạng thái Game Over
                self.draw_game_over_screen()  # Hiển thị màn hình Game Over



    def update(self):
        # Nếu game đã kết thúc, hiển thị màn hình Game Over và dừng update
        if self.game_over_bool:
            self.draw_game_over_screen()
            return
    # Kiểm tra nếu Pac-Man đang tàng hình và đã qua 3 giây kể từ khi hồi sinh
        if self.pacman.is_invincible and time.time() - self.pacman.invincibility_timer >= 3:
            self.pacman.is_invincible = False  # Hết tàng hình

    # Kiểm tra nếu Pac-Man chết và animation chưa kết thúc
        if self.is_dead and self.death_frame < self.death_end_frames:
            self.reset_round()
            return

    # Nếu hết mạng, hiển thị màn hình Game Over
        elif self.player.lives <= 0:
            print("Pac-Man đã hết mạng, chuyển sang màn hình Game Over")  # Debug
            self.game_over_bool = True
            self.draw_game_over_screen()  # Gọi ngay để vẽ màn hình Game Over
            return


        elif self.check_win():
            self.win()

    # Phát animation bắt đầu game
        elif self.start_frame < self.end_frames:
            self.start()
            return

    # Vòng lặp game chính
        if not self.mode == 'frightened':
            self.choose_mode()

        self.place_cherry()

    # Xử lý sự kiện phím
        for event in pyg.event.get():
            if event.type == pyg.QUIT:
                pyg.quit()
                sys.exit()
            if event.type == pyg.KEYDOWN:
                if event.key == pyg.K_w:
                    self.pacman.change_direction(direction=Direction.UP, maze=self.maze)
                elif event.key == pyg.K_s:
                    self.pacman.change_direction(direction=Direction.DOWN, maze=self.maze)
                elif event.key == pyg.K_a:
                    self.pacman.change_direction(direction=Direction.LEFT, maze=self.maze)
                elif event.key == pyg.K_d:
                    self.pacman.change_direction(direction=Direction.RIGHT, maze=self.maze)

    # Cập nhật di chuyển Pac-Man và Ghosts
        self.pacman.change_direction(self.pacman.buffered, self.maze)
        self.pacman.move(self.maze)
        self.check_frightened()
        self.move_ghosts()

    # Kiểm tra va chạm
        self.handle_collisions()

    # Chỉ vẽ màn hình nếu game chưa kết thúc
        if not self.game_over_bool:
            self.draw_screen()


    #check if all pellets, powerp, and cherry's have been eaten, if so return true and end game with win
    def check_win(self):
        for y in range(self.setup.Y_CELLS):
            for x in range(self.setup.X_CELLS):
                if self.maze.maze_elems[y][x] == elements.PELLET or self.maze.maze_elems[y][x] == elements.POWER_PELLET or self.maze.maze_elems[y][x] == elements.CHERRY:
                    return False
        return True

    #check if pacman has eaten a power pellet, and enter firghtened mode if he has
    def check_frightened(self):
        #check if pacman has eaten a power pellet, start timer if so, also extends the timer if pacman eats another power pellet
        if self.pacman.is_supercharged:
            #pause normal game timer
            self.game_timer.pause()
            self.mode = 'frightened'
            self.change_mode()
            #start the timer for frightened mode
            self.frightened_timer.start()
            self.pacman.is_supercharged = False
            #start playing the scary music
            if self.is_displaying:
                SoundEffects.background_channel.stop()
                SoundEffects.background_channel.play(SoundEffects.frightened_effect, loops = -1)

        #supercharged mode lasts 10 seconds
        elif self.mode == 'frightened' and self.frightened_timer.get_elapsed_time() > self.frightened_time:
            self.choose_mode()
            self.frightened_timer.stop()
            #start playing normal background music
            if self.is_displaying:
                SoundEffects.background_channel.stop()
                SoundEffects.background_channel.play(SoundEffects.background_effect, loops = -1)       
            #unpause game timer
            self.game_timer.unpause()    
    
    #every frame there is a chance to place a very small chance to place cherry on the board
    def place_cherry(self):
        #on average it should take 10 seconds to place a cherry
        if random.randint(0,600) == 42 and not self.cherry_placed:
            #place cherry in random location
            self.maze.place_cherry()
            self.cherry_placed = True

    def handle_collisions(self):
        for ghost in self.ghosts.values():  # Sửa lỗi thụt dòng
            # Nếu Pac-Man không tàng hình và ma quái không trong chế độ sợ hãi
            if ghost.mode != 'frightened' and not self.pacman.is_invincible and self.pacman.collision(ghost):
                if self.player.lives > 1:  
                    self.player.lives -= 1  # Giảm 1 mạng
                    self.respawn_pacman()
                else:
                    self.is_dead = True  # Nếu hết mạng, kết thúc game

    # Cập nhật giao diện hiển thị số mạng (trái tim)
                self.draw_lives()


        # Nếu Pac-Man ăn ma trong chế độ "frightened"
            elif ghost.mode == 'frightened' and self.pacman.collision(ghost):
                ghost.is_eaten = True
                self.player.update_score(200)  # Thưởng điểm khi ăn ma


    def respawn_pacman(self):
        self.pacman.position = self.setup.PACMAN_START  # Đưa Pac-Man về vị trí ban đầu
        self.pacman.direction = Direction.STOP  # Dừng lại để chờ hồi sinh
        self.pacman.subposition = (5, 0)  # Sửa lỗi 'elf' → 'self'

    # Kích hoạt tàng hình trong 3 giây sau khi hồi sinh
        self.pacman.is_invincible = True  
        self.pacman.invincibility_timer = time.time()  # Ghi lại thời điểm bắt đầu tàng hình

    



    #determine the mode of the ghosts based on the game timer
    def choose_mode(self):
        #0-7 seconds scatter
        if self.game_timer.get_elapsed_time() < 7:
            self.mode = 'scatter'
            self.change_mode()
        #7-27 seconds chase
        elif self.game_timer.get_elapsed_time() < 27:
            self.mode = 'chase'
            self.change_mode()

        #27-34 seconds scatter
        elif self.game_timer.get_elapsed_time() < 34:
            self.mode = 'scatter'
            self.change_mode()

        #34-54 seconds chase
        elif self.game_timer.get_elapsed_time() < 54:
            self.mode = 'chase'
            self.change_mode()
        #54-59 seconds scatter
        elif self.game_timer.get_elapsed_time() < 59:
            self.mode = 'scatter'
            self.change_mode()
        #59-79 seconds chase
        elif self.game_timer.get_elapsed_time() < 79:
            self.mode = 'chase'
            self.change_mode()
        #79-84 seconds scatter
        elif self.game_timer.get_elapsed_time() < 84:
            self.mode = 'scatter'
            self.change_mode()
        #Chase indefinitely
        else:
            self.mode = 'chase'
            self.change_mode()
        
    #change the mode of all ghosts on the sc
    def change_mode(self):
        for ghost in self.ghosts.values():
            ghost.mode = self.mode

    #update the position of the ghosts and also keep track of releasing them from the cage
    def move_ghosts(self):
        self.ghosts['blinky'].update(self.pacman, self.maze)
        self.ghosts['pinky'].update(self.pacman, self.maze)
        self.ghosts['inky'].update(self.pacman, self.maze, self.ghosts['blinky'])
        self.ghosts['clyde'].update(self.pacman, self.maze)

        #slowly release ghosts one by one from cage
        if self.game_timer.get_elapsed_time() > 7 and not self.ghosts['pinky'].left_cage:
            self.ghosts['pinky'].leave_cage(self.maze)
        else:
            self.ghosts['pinky'].update(self.pacman, self.maze)

        if self.game_timer.get_elapsed_time() > 10 and not self.ghosts['inky'].left_cage:
            self.ghosts['inky'].leave_cage(self.maze)
        else:
            self.ghosts['inky'].update(self.pacman, self.maze, self.ghosts['blinky'])

        if self.game_timer.get_elapsed_time() > 13 and not self.ghosts['clyde'].left_cage:
            self.ghosts['clyde'].leave_cage(self.maze)
        else:        
            self.ghosts['clyde'].update(self.pacman, self.maze)
        

    #occurs whenever pacman dies, reset the round if he has lives and reset the game if he does not
    def lose_life(self):
        self.player.lives -= 1
        self.reset_round()

    def game_over(self):
        self.game_over_bool = True
        self.screen.fill((0, 0, 0))  # Xóa màn hình
        text = self.setup.ARCADE_FONT_LARGE.render('GAME OVER', True, (255, 0, 0))
        self.screen.blit(text, (self.setup.SCREEN_WIDTH / 3, self.setup.SCREEN_HEIGHT / 3))

    # Vẽ nút Reset và Quit
        reset_button = pyg.Rect(self.setup.SCREEN_WIDTH / 3, self.setup.SCREEN_HEIGHT / 2, 150, 50)
        quit_button = pyg.Rect(self.setup.SCREEN_WIDTH / 3, self.setup.SCREEN_HEIGHT / 2 + 70, 150, 50)

        pyg.draw.rect(self.screen, (0, 255, 0), reset_button)  # Màu xanh cho Reset
        pyg.draw.rect(self.screen, (255, 0, 0), quit_button)  # Màu đỏ cho Quit

        reset_text = self.setup.ARCADE_FONT.render('Reset', True, (0, 0, 0))
        quit_text = self.setup.ARCADE_FONT.render('Quit', True, (0, 0, 0))

        self.screen.blit(reset_text, (self.setup.SCREEN_WIDTH / 3 + 45, self.setup.SCREEN_HEIGHT / 2 + 15))
        self.screen.blit(quit_text, (self.setup.SCREEN_WIDTH / 3 + 50, self.setup.SCREEN_HEIGHT / 2 + 85))

        pyg.display.flip()

    # Xử lý sự kiện khi bấm nút
        while True:
            for event in pyg.event.get():
                if event.type == pyg.QUIT:
                    pyg.quit()
                    sys.exit()
                if event.type == pyg.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if reset_button.collidepoint(x, y):
                        self.reset_game()
                        return  # Thoát khỏi vòng lặp, tiếp tục game
                    elif quit_button.collidepoint(x, y):
                        pyg.quit()
                        sys.exit()

    def reset_game(self):
        self.player.lives = 3
        self.player.score = 0
        self.maze.reset()
        self.pacman.reset()
        for ghost in self.ghosts.values():
            ghost.reset()

        self.starting_up = True
        self.game_over_bool = False
        self.start_frame = 0
        self.game_timer.start()

    
    #display win screen and final points
    def win(self):
        if self.is_displaying:
            #fill screen with black and display text sayinng you lose
            self.screen.fill((255,255,255))
            text = self.setup.ARCADE_FONT_LARGE.render('YOU WIN', True, (0, 0, 0))
            self.screen.blit(text, (self.setup.SCREEN_WIDTH/3,self.setup.SCREEN_HEIGHT/2))
            #display final score
            text = self.setup.ARCADE_FONT.render(f'Final Score: {self.player.score}', True, (0, 0, 0))
            self.screen.blit(text, (self.setup.SCREEN_WIDTH/3,self.setup.SCREEN_HEIGHT/1.5))

        #right as win start the win music
        if not self.game_over_bool and self.is_displaying:
            #cut all noise
            SoundEffects.background_channel.stop()
            #play win noise
            SoundEffects.background_channel.play(SoundEffects.win_effect, loops=-1)
        self.game_over_bool = True
        self.won = True



    def draw_screen(self):
        self.maze.display(self.screen)
        self.pacman.display(self.screen)
        if self.mode == "frightened":
            #display regular blue when firghtened
            if self.frightened_timer.get_elapsed_time() < self.frightened_time - 5:
                for ghost in self.ghosts.values():
                    ghost.display(self.screen, flash = False)
            #flash for the last 5 seconds of frightened mode
            else:
                for ghost in self.ghosts.values():
                    ghost.display(self.screen, flash = True)
        else:
            for ghost in self.ghosts.values():
                ghost.display(self.screen, flash = False)


        #show cherry in bottom right if hasn't been placed
        if not self.cherry_placed:
            self.screen.blit(self.maze.sprites['cherry'], (self.setup.SCREEN_WIDTH - 2*8*self.setup.SCALE, self.setup.SCREEN_HEIGHT - 2*8*self.setup.SCALE))
        #debug
        font = pyg.font.Font(None, 36)
        text = self.setup.ARCADE_FONT.render(f'FPS: {self.clock.get_fps()}', True, (255, 255, 255))
        self.screen.blit(text, (450,10))
        #text = ARCADE_FONT.render(f'Mode: {self.mode}', True, (255, 255, 255))
        #self.screen.blit(text, (250, SCREEN_HEIGHT - 30))

class Genetic_Game(Game):

    def __init__(self, setup, clock, gene, is_displaying):
        super().__init__(setup, clock, is_displaying)
        self.gene = gene.upper()
        self.genetic_moves = iter(self.gene)
                #map of moves to directions
        self.direction_map = {
            'L': Direction.LEFT,
            'R': Direction.RIGHT,
            'U': Direction.UP,
            'D': Direction.DOWN
        }

        '''
        replacement for the ingame timers is to keep track of ticks
        if we assume we want this game to display on a 60fps screen when it is not being trained then 
        there should be 60 ticks per second meaning each tick is 1/60 of a second or approximately 16.6666666667 milliseconds
        '''
        self.ticks = {
            'game': 0,
            'frightened': 0
        }

        #used to pause flow of game when in interupting mode like frightened or death
        self.game_ticks_paused = False
        #keep track of when in frightened mode
        self.frightened_ticks_paused = True

        #keep track of wether the game has been won or lost
        self.won = False

        #determines how many moves each gene maps to
        self.gene_multiplier = 1
        self.gene_current_number = 0

    #helper functions to convert between ticks and second, conversion is each tick is 1/60 of a second
    def ticks_to_seconds(self, ticks):
        return ticks/60
    def seconds_to_ticks(self, seconds):
        return seconds*60
    
    #restart the game completely without having to reload objects
    def complete_restart(self, new_gene):
        self.gene = new_gene.upper()
        self.genetic_moves = iter(self.gene)

        self.ticks = {
            'game': 0,
            'frightened': 0
        }

        #used to pause flow of game when in interupting mode like frightened or death
        self.game_ticks_paused = False
        #keep track of when in frightened mode
        self.frightened_ticks_paused = True

        #keep track of wether the game has been won or lost
        self.won = False

        #determines how many moves each gene maps to
        self.gene_multiplier = 1
        self.gene_current_number = 0

        self.player = Player('Schools Dollar')

        self.start_frame = 0
        self.starting_up = True
        #frame on which the starting animation ends
        self.end_frames = 10

        self.death_frame = 0
        self.death_end_frames = 10

        self.is_dead = False

                #how mnay seconds the ghosts will be frightened for
        self.frightened_time = 10

        #keep track of what mode the ghosts are in
        self.mode = 'scatter'

        #keep track of wether a cherry has been placed or not
        self.cherry_placed = False

        #keep track of when game ends
        self.game_over_bool = False
        self.maze.reset()
        self.pacman.reset()
# Không reset Ghost để chúng vẫn còn trên bản đồ
        self.pacman.player = self.player




    #Execute the gene by reading through the chromome and returning the next move in the sequence
    def choose_gene_move(self):

        next_move = next(self.genetic_moves, 'N')
        if next_move == 'N':
            return self.last_move
        self.last_move = next_move
        return self.direction_map[next_move]

    def start(self):
        #reset ghost location 
        for ghost in self.ghosts.values():
            ghost.reset()
        #reset pacman location
        self.pacman.reset()
        #start game timer
        self.game_timer.start()
        self.starting_up = False

    def update(self):
    # Nếu game đã kết thúc, hiển thị màn hình Game Over và dừng update
        if self.game_over_bool:
            self.draw_game_over_screen()
            return

    # Kiểm tra nếu Pac-Man chết và animation chưa kết thúc
        if self.is_dead and self.death_frame < self.death_end_frames:
            self.reset_round()
            return

    # Nếu hết mạng, đặt game_over_bool thành True
        elif self.player.lives <= 0:
            print("Pac-Man đã hết mạng, chuyển sang màn hình Game Over")  # Debug
            self.game_over_bool = True
            self.draw_game_over_screen()  # Hiển thị màn hình Game Over
            return


        elif self.check_win():
            self.win()

    # Phát animation bắt đầu game
        elif self.start_frame < self.end_frames:
            self.start()
            return

    # Vòng lặp game chính
        if not self.mode == 'frightened':
            self.choose_mode()

        self.place_cherry()

    # Xử lý sự kiện phím
        for event in pyg.event.get():
            if event.type == pyg.QUIT:
                pyg.quit()
                sys.exit()
            if event.type == pyg.KEYDOWN:
                if event.key == pyg.K_w:
                    self.pacman.change_direction(direction=Direction.UP, maze=self.maze)
                elif event.key == pyg.K_s:
                    self.pacman.change_direction(direction=Direction.DOWN, maze=self.maze)
                elif event.key == pyg.K_a:
                    self.pacman.change_direction(direction=Direction.LEFT, maze=self.maze)
                elif event.key == pyg.K_d:
                    self.pacman.change_direction(direction=Direction.RIGHT, maze=self.maze)

    # Cập nhật di chuyển Pac-Man và Ghosts
        self.pacman.change_direction(self.pacman.buffered, self.maze)
        self.pacman.move(self.maze)
        self.check_frightened()
        self.move_ghosts()

    # Kiểm tra va chạm
        self.handle_collisions()

    # Chỉ vẽ màn hình nếu game chưa kết thúc
        if not self.game_over_bool:
            self.draw_screen()

    
    #overide the basic choose mode logic to function based on ticks instead of an actual timer
    def choose_mode(self):
        #0-7 seconds scatter
        if self.ticks['game'] < self.seconds_to_ticks(7):
            self.mode = 'scatter'
            self.change_mode()
        #7-27 seconds chase
        elif self.ticks['game'] < self.seconds_to_ticks(27):
            self.mode = 'chase'
            self.change_mode()

        #27-34 seconds scatter
        elif self.ticks['game'] < self.seconds_to_ticks(34):
            self.mode = 'scatter'
            self.change_mode()

        #34-54 seconds chase
        elif self.ticks['game'] < self.seconds_to_ticks(54):
            self.mode = 'chase'
            self.change_mode()
        #54-59 seconds scatter
        elif self.ticks['game'] < self.seconds_to_ticks(59):
            self.mode = 'scatter'
            self.change_mode()
        #59-79 seconds chase
        elif self.ticks['game'] < self.seconds_to_ticks(79):
            self.mode = 'chase'
            self.change_mode()
        #79-84 seconds scatter
        elif self.ticks['game'] < self.seconds_to_ticks(84):
            self.mode = 'scatter'
            self.change_mode()
        #Chase indefinitely
        else:
            self.mode = 'chase'
            self.change_mode()

    #overide the basic check frightened logic to function based on ticks instead of an actual timer
    #update the position of the ghosts and also keep track of releasing them from the cage
    def move_ghosts(self):
        self.ghosts['blinky'].update(self.pacman, self.maze)
        self.ghosts['pinky'].update(self.pacman, self.maze)
        self.ghosts['inky'].update(self.pacman, self.maze, self.ghosts['blinky'])
        self.ghosts['clyde'].update(self.pacman, self.maze)

        #slowly release ghosts one by one from cage
        if self.ticks['game'] > self.seconds_to_ticks(7) and not self.ghosts['pinky'].left_cage:
            self.ghosts['pinky'].leave_cage(self.maze)
        else:
            self.ghosts['pinky'].update(self.pacman, self.maze)

        if self.ticks['game'] > self.seconds_to_ticks(10) and not self.ghosts['inky'].left_cage:
            self.ghosts['inky'].leave_cage(self.maze)
        else:
            self.ghosts['inky'].update(self.pacman, self.maze, self.ghosts['blinky'])

        if self.ticks['game'] > self.seconds_to_ticks(13) and not self.ghosts['clyde'].left_cage:
            self.ghosts['clyde'].leave_cage(self.maze)
        else:        
            self.ghosts['clyde'].update(self.pacman, self.maze)
    
    #overide the basic check frightened logic to function based on ticks instead of an actual timer
    #check if pacman has eaten a power pellet, and enter firghtened mode if he has
    def check_frightened(self):
        #check if pacman has eaten a power pellet, start timer if so, also extends the timer if pacman eats another power pellet
        if self.pacman.is_supercharged:
            #pause normal game timer
            self.game_ticks_paused = True
            self.mode = 'frightened'
            self.change_mode()
            #start the timer for frightened mode
            self.frightened_ticks_paused = False

            self.pacman.is_supercharged = False
            #start playing the scary music
            if self.is_displaying:
                SoundEffects.background_channel.stop()
                SoundEffects.background_channel.play(SoundEffects.frightened_effect, loops = -1)

        #supercharged mode lasts 10 seconds
        elif self.mode == 'frightened' and self.ticks['frightened'] > self.seconds_to_ticks(self.frightened_time):
            self.choose_mode()

            #reset frightened mode
            self.ticks['frightened'] = 0
            self.frightened_ticks_paused = True

            #start playing normal background music
            if self.is_displaying:
                SoundEffects.background_channel.stop()
                SoundEffects.background_channel.play(SoundEffects.background_effect, loops = -1)       
            #unpause game timer
            self.game_ticks_paused = False
    
    #overide the basic screen drawing logic to function based on ticks instead of an actual timer
    def draw_screen(self):
        self.maze.display(self.screen)
        self.pacman.display(self.screen)
        if self.mode == "frightened":
            #display regular blue when firghtened
            if self.ticks['frightened'] < self.seconds_to_ticks(self.frightened_time - 5):
                for ghost in self.ghosts.values():
                    ghost.display(self.screen, flash = False)
            #flash for the last 5 seconds of frightened mode
            else:
                for ghost in self.ghosts.values():
                    ghost.display(self.screen, flash = True)
        else:
            for ghost in self.ghosts.values():
                ghost.display(self.screen, flash = False)


        #show cherry in bottom right if hasn't been placed
        if not self.cherry_placed:
            self.screen.blit(self.maze.sprites['cherry'], (self.setup.SCREEN_WIDTH - 2*8*self.setup.SCALE, self.setup.SCREEN_HEIGHT - 2*8*self.setup.SCALE))
        #debug
        font = pyg.font.Font(None, 36)
        text = self.setup.ARCADE_FONT.render(f'FPS: {self.clock.get_fps()}', True, (255, 255, 255))
        self.screen.blit(text, (450,10))
        #text = ARCADE_FONT.render(f'Mode: {self.mode}', True, (255, 255, 255))
        #self.screen.blit(text, (250, SCREEN_HEIGHT - 30))


class Player:
    def __init__(self, name):
        self.name = name
        self.score = 0
        self.lives = 3

    def update_score(self, points):
        self.score+=points

    def lose_life(self):
        self.lives -= 1



def main():
    # Initialize pygame

    # Create the game
    clock = pyg.time.Clock()
    setup = Game_Setup()
    game = Game(setup, clock, True)

    # Main game loop
    while True:

        # Update the game
        game.update()

        #update the display
        pyg.display.flip()

        #limit frame rate 
        clock.tick(60)

#class to run a full game of pacman, used in other files
class Pacman_Game():
    def test_game(self, frame_rate):
        # Create the game
        clock = pyg.time.Clock()
        setup = Game_Setup()
        game = Game(setup, clock, True)

        # Main game loop
        while True:

            # Update the game
            game.update()

            #update the display
            pyg.display.flip()

            #limit frame rate 
            clock.tick(frame_rate)
    
    def execute_moves(self, move_string):
        #map of moves to directions
        direction_map = {
            'L': Direction.LEFT,
            'R': Direction.RIGHT,
            'U': Direction.UP,
            'D': Direction.DOWN
        }

        #index of current move in string
        moves = move_string.upper()
        print(moves)
        move_iter = iter(moves)
        setup = Game_Setup()
        # Create the game
        game = Game(setup, pyg.time.Clock(), False)
        while True:
            try:
                move = next(move_iter)
            except StopIteration:
                break

    def genetic_test(self, gene):
        # Create the game
        clock = pyg.time.Clock()
        setup = Game_Setup()

        best_score = 0
        is_displaying = False
        for i in range(100):
            game = Genetic_Game(setup, clock, gene, is_displaying)
            # Main game loop
            while game.game_over_bool != True:

                # Update the game
                game.update()

                #update the display
                if is_displaying:
                    pyg.display.flip()
                    clock.tick(60)

            if game.player.score > best_score:
                best_score = game.player.score

        return game.player.score

        

if __name__ == "__main__":

    main()
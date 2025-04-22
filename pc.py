import pygame as pyg
import sys
from enum import Enum
import random
import time
import os

'''
HÀM TRỢ GIÚP RẤT QUAN TRỌNG CHO PHÉP BẠN CHƠI ÂM THANH CHO TRÒ CHƠI PACMAN BẰNG CÁCH ĐỌC CÁC TẬP TIN ÂM THANH TỪ CÙNG THƯ MỤC VỚI TRÒ CHƠI
'''

pyg.init()

#chứa thông tin thiết lập trò chơi cơ bản và đồ họa
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
            raise Exception("Đồng hồ bấm giờ chưa được bắt đầu.")

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
                    #đặt lại danh sách
                    sprite_list = []
                elif ghost_col == 3:
                    sprites['left'] = sprite_list
                    #đặt lại danh sách
                    sprite_list = []

                elif ghost_col == 5:
                    sprites['up'] = sprite_list
                    #đặt lại danh sách
                    sprite_list = []

                elif ghost_col == 7:
                    sprites['down'] = sprite_list
                    #đặt lại danh sách
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

        # Tỷ lệ để dễ nhìn hơn trong hiển thị
        self.scale_sprites(pacman_sprites)
        self.scale_sprites(background_sprites)
        #các sprite ma quái đã được tỷ lệ trong hàm tải

        return pacman_sprites, ghost_sprites, background_sprites

'''
CÁC LỚP PACMAN TẤT CẢ ĐI DƯỚI ĐÂY
'''

class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    STOP = 5

#các loại phần tử có thể tìm thấy trong mê cung
class elements(Enum):
    WALL = '#'
    EMPTY = ' '
    PELLET = 'p'
    POWER_PELLET = 'o'
    PACMAN = 'C'
    GHOST = 'G'
    CHERRY = 'c'

#Các đối tượng có thể di chuyển bao gồm pacman và các ma quái và là bất kỳ sprite nào có thể di chuyển
class Moveable:
    def __init__(self, position, sprites, setup):
        #tuple vị trí của tâm đối tượng theo pixel của sprite chưa được tỷ lệ
        #tuple vị trí của pacman theo ô trong mê cung
        self.position = position
        #số nguyên giữa 0-8 đại diện cho vị trí phụ của pacman trong ô theo pixel từ tâm ô mà anh ta đang
        self.subposition = (0,5)
        self.direction = Direction.STOP
        #mảng các sprite với các hướng khác nhau của chúng
        self.sprites = sprites
        #thay đổi giữa các hoạt ảnh di chuyển
        self.open = False
        #giữ theo dõi việc hiển thị nếu bị sợ hãi
        self.flash = False
        self.setup = setup

    #xác định sự dịch chuyển hiện tại được bao phủ trong một màn hình bởi pacman theo tốc độ hiện tại của anh ta
    def displacement(self): 
        speed = 1
        time = 1
        return int(speed*time)

    #kiểm tra xem đối tượng có thể thay đổi hướng hay không và nếu có thì thay đổi hướng, trả về true nếu có thể quay và false nếu không thể
    def change_direction(self, direction, maze):
        #kiểm tra xem đối tượng có bên cạnh tường và nếu vậy thì không cho phép anh ta thay đổi hướng
        x, y = self.position
        sub_x, sub_y = self.subposition
        
        #trường hợp đặc biệt cho đường hầm
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

        #kiểm tra xem pacman có thể quay vào, nếu không thì lưu trữ chuyển động đó
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
    
    #di chuyển sprite trong một khung hình dựa trên hướng hiện tại của nó
    def move(self, maze):
        x, y = self.position
        sub_x, sub_y = self.subposition
        #thay đổi hướng của sprite dựa trên nơi anh ta đang cố gắng di chuyển
        direction = self.direction

        #kiểm tra xem vị trí tiếp theo có phải là tường hay không và nếu không thì di chuyển đến vị trí đó
        if direction == Direction.UP:
            #tại cạnh của ô di chuyển đến ô tiếp theo
            if sub_y == 0 and sub_x == 0 and maze.maze_elems[y - 1][x] != elements.WALL:
                self.position = (x, y - 1)
                #đặt lại sub_y thành 15 để di chuyển đến đáy của ô
                self.subposition = (sub_x, 8)
                #thay đổi trạng thái miệng để hoạt ảnh
                self.open = not self.open
                #thay đổi nhấp nháy trong chế độ sợ hãi
                self.flash = not self.flash
            else:
                #không thể làm cho vị trí phụ nhỏ hơn 0
                self.subposition = (sub_x,max(sub_y - self.displacement(),0))

        elif direction ==  Direction.DOWN and maze.maze_elems[y + 1][x] != elements.WALL:
            #tại cạnh của ô di chuyển đến ô tiếp theo
            if sub_y == 8 and sub_x == 0:
                self.position = (x, y + 1)
                #đặt lại sub_y thành 0 để di chuyển đến đỉnh của ô
                self.subposition = (sub_x, 0)
                #thay đổi trạng thái miệng để hoạt ảnh
                self.open = not self.open
                #thay đổi nhấp nháy trong chế độ sợ hãi
                self.flash = not self.flash
            elif sub_x == 0:
                self.subposition = (sub_x, min(sub_y + self.displacement(),8))

        elif direction == Direction.LEFT:
            #trường hợp đặc biệt cho đường hầm
            if x == maze.tunnel_left[0] and y == maze.tunnel_left[1]:
                if sub_x == 0 and sub_y==0:
                    self.position = maze.tunnel_right
                    self.subposition = (8, sub_y)
                else:
                    self.subposition = (max(sub_x - self.displacement(), 0), sub_y)

            #tại cạnh của ô di chuyển đến ô tiếp theo
            elif sub_x == 0 and sub_y==0 and maze.maze_elems[y][x - 1] != elements.WALL:
                self.position = (x - 1, y)
                #đặt lại sub_x thành 15 để di chuyển đến bên phải của ô
                self.subposition = (8, sub_y)
                #thay đổi trạng thái miệng để hoạt ảnh
                self.open = not self.open
                #thay đổi nhấp nháy trong chế độ sợ hãi
                self.flash = not self.flash
            elif sub_y == 0:
                self.subposition = (max(sub_x - self.displacement(), 0), sub_y)

        elif direction == Direction.RIGHT:
            #trường hợp đặc biệt cho đường hầm
            if x == maze.tunnel_right[0] and y == maze.tunnel_right[1]:
                if sub_x == 8 and sub_y==0:
                    self.position = maze.tunnel_left
                    self.subposition = (0, sub_y)
                else:
                    self.subposition = (min(sub_x + self.displacement(),8), sub_y)
            
            #tại cạnh của ô di chuyển đến ô tiếp theo
            elif sub_x == 8 and sub_y==0 and maze.maze_elems[y][x + 1] != elements.WALL:
                self.position = (x + 1, y)
                #đặt lại sub_x thành 0 để di chuyển đến bên trái của ô
                self.subposition = (0, sub_y)
                #thay đổi trạng thái miệng để hoạt ảnh
                self.open = not self.open
                #thay đổi nhấp nháy trong chế độ sợ hãi
                self.flash = not self.flash
            elif sub_y == 0 and maze.maze_elems[y][x + 1] != elements.WALL:
                self.subposition = (min(sub_x + self.displacement(),8), sub_y)

    '''
    hàm trợ giúp để kiểm tra xem hướng được lưu trữ có đối diện với hướng bạn đang di chuyển hay không
    và nếu vậy thì xóa hướng được lưu trữ, điều này được thực hiện
    để tránh các lỗi góc kỳ lạ vì nếu bạn đang đi qua một góc với một sàn bên dưới bạn 
    và bạn có một chuyển động xuống được lưu trữ thì ngay khi bạn cố gắng đi lên bạn sẽ có thể thực hiện chuyển động xuống được lưu trữ
    có nghĩa là bạn sẽ đi lên rồi ngay lập tức đặt lại vị trí của mình

    Cũng giúp trong các ma quái để tránh chúng quay lại và theo dấu bước chân của chúng
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
        #trả về true nếu chuyển động được lưu trữ đối diện với hướng hiện tại, và false nếu không
        else:
            return False
        return True
    
    def display(self, screen):
        x,y = self.position
        sub_x, sub_y = self.subposition
        
        sprite = None
        #chọn sprite dựa trên việc miệng mở hay đóng và hướng mà pacman đang đối diện
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
                
        #bắt đầu trò chơi đối diện bên phải trong hướng dừng
        elif self.direction == Direction.RIGHT or self.direction == Direction.STOP:
            if self.open:
                sprite = self.sprites['right'][0]
            else:
                sprite = self.sprites['right'][1]

        #vì vị trí nằm ở điểm trung tâm của pacman nên chúng ta cần điều chỉnh vị trí đến góc trên bên trái của sprite
        screen.blit(sprite, ((x*8+sub_x-4)*self.setup.SCALE, (y*8+sub_y-4)*self.setup.SCALE))

    #kiểm tra xem đối tượng có va chạm với một đối tượng có thể di chuyển khác hay không, trả về true nếu có va chạm và false nếu không
    def collision(self, other : 'Ghost'):
        #nếu ma quái đã bị pacman ăn thì không va chạm với nó
        if self.position == other.position and not other.is_eaten:
            return True
        else: 
            return False
    
class Pacman(Moveable):
    def __init__(self, sprites, player, setup):
        self.setup = setup
        starting_position = setup.PACMAN_START
        #xây dựng một đối tượng có thể di chuyển với vị trí bắt đầu
        super().__init__(starting_position, sprites, setup)

        #thay đổi vị trí phụ để hiển thị 
        self.subposition = (5,0)
        #người chơi điều khiển pacman
        self.player = player

        #từ điển chứa tất cả các sprite khác nhau cho các hướng khác nhau
        self.sprites = sprites

        '''
        lưu trữ đầu vào, nếu người chơi cố gắng thay đổi hướng và pacman không thể thay đổi hướng vào thời điểm đó
        lưu hướng mà người chơi muốn đi và thay đổi hướng khi pacman có thể
        '''
        self.buffered = Direction.STOP

        #giữ theo dõi xem pacman có siêu cấp hay không
        self.is_supercharged = False

        #thay đổi liệu miệng mở hay đóng cho hoạt ảnh
        self.open = True

        #đồng hồ cho việc xác định khi nào phát hiệu ứng âm thanh ăn
        self.eating_timer = Stopwatch()
        self.eat_time = 0.15


    #đặt lại pacman về vị trí bắt đầu
    def reset(self):
        self.position = self.setup.PACMAN_START
        self.direction = Direction.STOP
        self.subposition = (0,0)
        self.buffered = Direction.STOP
        self.is_supercharged = False

    #ghi đè phương thức thay đổi hướng để bao gồm việc lưu trữ đầu vào
    #kiểm tra để đảm bảo pacman có thể thay đổi sang hướng dự định và thay đổi nếu có thể, trả về true nếu có thể quay và false nếu không thể
    def change_direction(self, direction, maze):
        #kiểm tra xem pacman có bên cạnh tường và nếu vậy thì không cho phép anh ta thay đổi hướng
        x, y = self.position
        sub_x, sub_y = self.subposition

        #ngăn chặn các chuyển động được lưu trữ ở hướng đối diện thực hiện, xem thêm thông tin tại định nghĩa hàm thực tế
        if super().check_opposite_drection(self.buffered):
            self.buffered = Direction.STOP
            return False
        
        #trường hợp đặc biệt cho đường hầm
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

        #kiểm tra xem pacman có thể quay vào, nếu không thì lưu trữ chuyển động đó
        if direction == Direction.UP and sub_x==0 and maze.maze_elems[y-1][x] != elements.WALL:
            self.direction = direction
        elif direction == Direction.DOWN and sub_x==0 and maze.maze_elems[y+1][x] != elements.WALL:
            self.direction = direction
        elif direction == Direction.LEFT and sub_y==0 and maze.maze_elems[y][x-1] != elements.WALL:
            self.direction = direction
        elif direction == Direction.RIGHT and sub_y==0 and maze.maze_elems[y][x+1] != elements.WALL:
            self.direction = direction
        #không thể quay
        else:
            #đặt hướng được lưu trữ 
            self.buffered = direction
            return False
        #đã quay 
        return True    
    
                
    #hơi ghi đè hàm di chuyển của cha để cũng thực hiện việc ăn các viên bi
    def move(self, maze):
        super().move(maze)
        #ăn viên bi nếu có ở vị trí đó
        self.eat(maze.maze_elems)

    def eat(self, maze):
        x, y = self.position
        #ăn viên bi nếu có ở vị trí đó bằng cách tăng điểm số và loại bỏ viên bi
        if maze[y][x] == elements.PELLET:
            maze[y][x] = elements.EMPTY
            self.player.score += 10
            # Phát hiệu ứng âm thanh ăn chỉ khi không đang phát
            if self.eating_timer.start_time == None or self.eating_timer.get_elapsed_time() == 0:
                #Tắt âm thanh ăn LOẠI BỎ SAU ĐỂ CHƠI THƯỜNG XUYÊN
                # SoundEffects.eating_channel.play(SoundEffects.eating_effect)
                self.eating_timer.start()
            elif self.eating_timer.get_elapsed_time() >= self.eat_time:
                self.eating_timer.stop()

        #ăn viên bi siêu nếu có ở vị trí đó bằng cách tăng điểm số và loại bỏ viên bi và làm cho pacman siêu cấp
        if maze[y][x] == elements.POWER_PELLET:
            maze[y][x] = elements.EMPTY
            self.player.score += 50
            self.is_supercharged = True
        
        #ăn quả anh đào để thêm 100 điểm
        if maze[y][x] == elements.CHERRY:
            #phát âm thanh anh đào
            #LOẠI BỎ ÂM THANH ANH ĐÀO THÊM SAU
            #SoundEffects.cherry_channel.play(SoundEffects.cherry_effect)
            maze[y][x] = elements.EMPTY
            self.player.score += 100
        

    def display(self, screen):
        super().display(screen)
        #hiển thị văn bản
        font = pyg.font.Font(None, 36)
        text = self.setup.ARCADE_FONT.render(f'Score: {self.player.score}', True, (255, 255, 255))
        screen.blit(text, (10, self.setup.SCREEN_HEIGHT - 90))
        text = self.setup.ARCADE_FONT.render(f'Lives: {self.player.lives}', True, (255, 255, 255))
        screen.blit(text, (10, self.setup.SCREEN_HEIGHT - 30))
        text = self.setup.ARCADE_FONT.render(f'SC?: {self.is_supercharged}', True, (255, 255, 255))
        screen.blit(text, (250, self.setup.SCREEN_HEIGHT - 30))
        # text = ARCADE_FONT.render(f'Direction: {self.direction}', True, (255, 255, 255))
        # screen.blit(text, (10, SCREEN_HEIGHT - 30))
        # text = ARCADE_FONT.render(f'Buffered: {self.buffered}', True, (255, 255, 255))
        # screen.blit(text, (350, SCREEN_HEIGHT - 30))



class Ghost(Moveable):
    def __init__(self, color, sprites, frightened_sprites, setup):
        self.setup = setup
        #mỗi ma quái ngoại trừ blinky bắt đầu trong lồng
        self.position = self.setup.CAGE_CORDS
        super().__init__(self.position, sprites, setup)
        self.frightened_sprites = frightened_sprites
        self.sub_position = (0,0)
        self.color = color
        self.sprites = sprites
        self.direction = Direction.STOP

        #mỗi ma quái có một ô mục tiêu mà chúng muốn đạt được và, điều này xác định hướng mà chúng sẽ di chuyển
        self.target_tile = (0,0)
        #mỗi ma quái có một ô tán xạ mà chúng muốn đạt được khi chúng ở chế độ tán xạ
        self.scatter_tile = (0,0)

        self.mode = 'chase'

        self.left_cage = False

        #các trường bổ sung cho khi ma quái bị pacman ăn trong chế độ sợ hãi
        self.is_eaten = False


    
    #đặt lại ma quái về lồng sau khi pacman chết
    def reset(self):
        self.position = self.setup.CAGE_CORDS
        self.direction = Direction.STOP
        self.subposition = (0,0)
        self.mode = 'chase'
        self.left_cage = False

    #di chuyển ma quái ra khỏi lồng, để bắt đầu theo dõi người chơi
    def leave_cage(self, maze):
        #đầu tiên điều hướng đến trung tâm của lồng
        if self.position != self.setup.CAGE_CORDS:
            self.target_tile = self.setup.CAGE_CORDS
            self.choose_direction(maze)
            self.move(maze)
        
        #nếu ma quái ở giữa lồng thì buộc di chuyển ra khỏi lồng
        elif self.position == self.setup.CAGE_CORDS:
            self.position = (self.position[0], self.position[1] - 2)
            self.subposition = (0,0)
            self.direction = Direction.UP
            self.left_cage = True

    #mỗi ma quái có một thuật toán theo dõi khác nhau sẽ được ghi đè bởi lớp con
    #xác định ô mục tiêu cho ma quái để di chuyển đến
    def chase(self, pacman, graph):
        pass

    def scatter(self):
        self.target_tile = self.scatter_tile
    
    #sẽ xác định hướng mà ma quái sẽ di chuyển để bắt pacman
    def choose_direction(self, maze):
        #xác định các ô có thể (hàng xóm của vị trí hiện tại)
        possible_tiles = maze.graph[self.position]
        #xác định các hướng có thể mà ma quái có thể di chuyển dựa trên các ô có sẵn cho nó
        possible_directions = {
            Direction.UP: None,
            Direction.DOWN: None,
            Direction.LEFT: None,
            Direction.RIGHT: None
        }

        #xác định khoảng cách đến ô mục tiêu cho mỗi hướng có thể
        for tile in possible_tiles:            
            if tile[0] == self.position[0] and tile[1] < self.position[1]:
                possible_directions[Direction.UP] = tile
            elif tile[0] == self.position[0] and tile[1] > self.position[1]:
                possible_directions[Direction.DOWN] = tile
            elif tile[1] == self.position[1] and tile[0] < self.position[0]:
                possible_directions[Direction.LEFT] = tile
            elif tile[1] == self.position[1] and tile[0] > self.position[0]:
                possible_directions[Direction.RIGHT] = tile

        #xác định khoảng cách đến ô mục tiêu cho mỗi hướng có thể
        directions = {
            Direction.UP: None,
            Direction.DOWN: None,
            Direction.LEFT: None,
            Direction.RIGHT: None
        }
        

        for direction in directions:
            #không thể chọn để đảo ngược hướng hoặc quay ở nơi bạn không thể đi
            if possible_directions[direction] is None or super().check_opposite_drection(direction):
                directions[direction] = float('inf')
            else:
                #khoảng cách từ ô có thể đến ô mục tiêu
                directions[direction] = self.distance(possible_directions[direction], self.target_tile)
            #chọn hướng có chi phí thấp nhất để di chuyển
        optimal_direction = min(directions, key=directions.get)
        #nếu đã đến cạnh của ô để quay theo hướng đó thì làm như vậy, nếu không thì chờ
        self.change_direction(optimal_direction, maze)
        

    #xác định khoảng cách euclidean giữa hai điểm
    def distance(self, start, end):
        return ((start[0] - end[0])**2 + (start[1] - end[1])**2)**0.5
    
    #ghi đè chức năng hiển thị để bao gồm chế độ sợ hãi
    def display(self, screen, flash):
        #hiển thị bình thường nếu không sợ hãi
        if self.mode != 'frightened':
            super().display(screen)
        
        #ma quái bị pacman ăn, hiển thị đôi mắt
        elif self.is_eaten:
            x,y = self.position
            sub_x, sub_y = self.subposition
            
            sprite = None
            #chọn sprite dựa trên việc miệng mở hay đóng và hướng mà pacman đang đối diện
            if self.direction == Direction.UP:
                sprite = self.sprites['up'][2]
            elif self.direction == Direction.DOWN:
                sprite = self.sprites['down'][2]
            elif self.direction == Direction.LEFT:
                sprite = self.sprites['left'][2]
            #bắt đầu trò chơi đối diện bên phải trong hướng dừng
            elif self.direction == Direction.RIGHT or self.direction == Direction.STOP:
                sprite = self.sprites['right'][2]
            #vì vị trí nằm ở điểm trung tâm của pacman nên chúng ta cần điều chỉnh vị trí đến góc trên bên trái của sprite
            screen.blit(sprite, ((x*8+sub_x-4)*self.setup.SCALE, (y*8+sub_y-4)*self.setup.SCALE))
        
        #hiển thị chế độ sợ hãi
        elif self.mode == 'frightened':
            x,y = self.position
            sub_x, sub_y = self.subposition
            sprite = None

            #trong chế độ sợ hãi bình thường, ma quái sẽ thay đổi giữa hai sprite màu xanh
            #khi ma quái bắt đầu nhấp nháy, sprite sẽ thay đổi giữa bốn sprite, 2 sprite nhấp nháy và 2 sprite màu xanh
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

            #vì vị trí nằm ở điểm trung tâm của pacman nên chúng ta cần điều chỉnh vị trí đến góc trên bên trái của sprite
            screen.blit(sprite, ((x*8+sub_x-4)*self.setup.SCALE, (y*8+sub_y-4)*self.setup.SCALE))

    #trong chế độ sợ hãi, ma quái sẽ di chuyển theo hướng ngược lại
    def reverse_direction(self):
        if self.direction == Direction.UP:
            self.direction = Direction.DOWN
        elif self.direction == Direction.DOWN:
            self.direction = Direction.UP
        elif self.direction == Direction.LEFT:
            self.direction = Direction.RIGHT
        elif self.direction == Direction.RIGHT:
            self.direction = Direction.LEFT

    #nhập chế độ sợ hãi và đảo ngược hướng
    def make_frightened(self):
        self.mode = 'frightened'
        self.reverse_direction()

    #ngẫu nhiên chọn một hướng tại giao lộ để di chuyển khi sợ hãi, nếu không ở giao lộ thì tiếp tục di chuyển thẳng
    def frightened(self, maze):
        #xác định các ô có thể (hàng xóm của vị trí hiện tại)
        possible_tiles = maze.graph[self.position]
        #xác định các hướng có thể mà ma quái có thể di chuyển dựa trên các ô có sẵn cho nó
        possible_directions = {
            Direction.UP: None,
            Direction.DOWN: None,
            Direction.LEFT: None,
            Direction.RIGHT : None
        }
        #xác định các hướng mà ma quái phải di chuyển để đến ô đó

        #trường hợp đặc biệt cho đường hầm
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

        #chọn hướng ngẫu nhiên
        directions = [direction for direction in possible_directions if possible_directions[direction] is not None and not super().check_opposite_drection(direction)]
        #nếu đã đến cạnh của ô để quay theo hướng đó thì làm như vậy, nếu không thì chờ 
        self.change_direction(random.choice(directions), maze)

    #cập nhật đầy đủ chuyển động của ma quái, chọn hướng để di chuyển và sau đó di chuyển
    def update(self, pacman, maze):
        if self.mode == 'chase':
            self.chase(pacman, maze)
            self.choose_direction(maze)
            self.move(maze)
        elif self.mode == 'scatter':
            self.scatter()
            self.choose_direction(maze)
            self.move(maze)
    
        elif self.mode == 'frightened':
            #nếu ma quái bị pacman ăn, anh ta sẽ di chuyển đến phía trước của lồng, đó là vị trí bắt đầu của Blinky
            if self.is_eaten and self.position != self.setup.BLINKY_CAGE_CORDS:
                self.target_tile = self.setup.BLINKY_CAGE_CORDS
                self.choose_direction(maze)
                self.move(maze)

            #đã đến điểm bắt đầu, ma quái tái sinh và không còn sợ hãi ngay cả khi pacman siêu cấp
            elif self.is_eaten and self.position == self.setup.BLINKY_CAGE_CORDS:
                self.is_eaten = False
                self.mode = 'chase'

            #di chuyển bình thường trong chế độ sợ hãi
            else:
                #không có ô mục tiêu trong chế độ sợ hãi chỉ có hướng
                self.frightened(maze)
                self.move(maze)

class Blinky(Ghost):
    def __init__(self, sprite, frightened_sprites,setup):
        super().__init__('red', sprite, frightened_sprites,setup)
        #blinky bắt đầu bên ngoài lồng
        self.position = setup.BLINKY_CAGE_CORDS
        self.left_cage = True
        #nhiều ô tán xạ của ma quái không thể truy cập, nhưng điều này không ảnh hưởng đến việc tìm đường đến nó
        self.scatter_tile = 25, -3

    #đặt lại ma quái về lồng sau khi pacman chết
    def reset(self):
        self.position = self.setup.BLINKY_CAGE_CORDS
        self.direction = Direction.STOP
        self.subposition = (0,0)
        self.mode = 'chase'

    def chase(self, pacman, maze):
        # Blinky trực tiếp nhắm đến vị trí của Pacman
        self.target_tile = pacman.position

class Pinky(Ghost):
    def __init__(self, sprite, frightened_sprites,setup):
        super().__init__('pink', sprite, frightened_sprites, setup)
        #nhiều ô tán xạ của ma quái không thể truy cập, nhưng điều này không ảnh hưởng đến việc tìm đường đến nó
        self.scatter_tile = (2,-3)

    def chase(self, pacman, maze):
        # Pinky nhắm đến một ô cách 4 ô phía trước hướng hiện tại của Pacman
        if(pacman.direction == Direction.UP):
            self.target_tile = (pacman.position[0], pacman.position[1] - 4)
        elif(pacman.direction == Direction.DOWN):
            self.target_tile = (pacman.position[0], pacman.position[1] + 4)
        elif(pacman.direction == Direction.LEFT):
            self.target_tile = (pacman.position[0] - 4, pacman.position[1])
        elif(pacman.direction == Direction.RIGHT):
            self.target_tile = (pacman.position[0] + 4, pacman.position[1])

class Inky(Ghost):
    def __init__(self, sprite, frightened_sprites, setup):
        super().__init__('cyan', sprite, frightened_sprites, setup)
        self.scatter_tile = (27, 33)

    '''
    Inky sử dụng sự kết hợp giữa vị trí của Pacman và Blinky
    đầu tiên kiểm tra ô cách 2 ô phía trước pacman và sau đó vẽ một vector từ blinky đến ô đó
    sau đó gấp đôi chiều dài của vector ô mà vector đó kết thúc là ô mục tiêu
    '''
    def chase(self, pacman, maze, blinky):
        initial_target = None
        # Pinky nhắm đến một ô cách 4 ô phía trước hướng hiện tại của Pacman
        if(pacman.direction == Direction.UP):
            initial_target = (pacman.position[0], pacman.position[1] - 4)
        elif(pacman.direction == Direction.DOWN):
            initial_target = (pacman.position[0], pacman.position[1] + 4)
        elif(pacman.direction == Direction.LEFT):
            initial_target = (pacman.position[0] - 4, pacman.position[1])
        
        #xem pacman đang đối diện bên phải nếu anh ta không di chuyển
        elif(pacman.direction == Direction.RIGHT or pacman.direction == Direction.STOP):
            initial_target = (pacman.position[0] + 4, pacman.position[1])
        
        #tính toán các thành phần của vector từ blinky đến ô mục tiêu
        dx = initial_target[0] - blinky.position[0]
        #đảo ngược thành phần y vì y tăng xuống dưới 
        dy = blinky.position[1] - initial_target[1]

        #gấp đôi chiều dài của vector
        self.target_tile = (blinky.position[0] + 2*dx, blinky.position[1] + 2*dy)

    #ghi đè cập nhật để bao gồm blinky như một tham số
    #cập nhật đầy đủ chuyển động của ma quái, chọn hướng để di chuyển và sau đó di chuyển
    def update(self, pacman, maze, blinky):
        if self.mode == 'chase':
            self.chase(pacman, maze, blinky)
            self.choose_direction(maze)
            self.move(maze)
        elif self.mode == 'scatter':
            self.scatter()
            self.choose_direction(maze)
            self.move(maze)
    
        elif self.mode == 'frightened':
            #nếu ma quái bị pacman ăn, anh ta sẽ di chuyển đến phía trước của lồng, đó là vị trí bắt đầu của Blinky
            if self.is_eaten and self.position != self.setup.BLINKY_CAGE_CORDS:
                self.target_tile = self.setup.BLINKY_CAGE_CORDS
                self.choose_direction(maze)
                self.move(maze)

            #đã đến điểm bắt đầu, ma quái tái sinh và không còn sợ hãi ngay cả khi pacman siêu cấp
            elif self.is_eaten and self.position == self.setup.BLINKY_CAGE_CORDS:
                self.is_eaten = False
                self.mode = 'chase'

            #di chuyển bình thường trong chế độ sợ hãi
            else:
                #không có ô mục tiêu trong chế độ sợ hãi chỉ có hướng
                self.frightened(maze)
                self.move(maze)

class Clyde(Ghost):
    def __init__(self,sprite, frightened_sprites, setup):
        super().__init__('orange', sprite, frightened_sprites, setup)
        self.scatter_tile = (0,33)

    def chase(self, pacman, maze):
        # Clyde chuyển đổi giữa việc nhắm đến Pacman và đi lang thang

        #nhắm đến như blinky khi xa hơn 8 ô
        if self.distance(self.position, pacman.position) > 8:
            self.target_tile = pacman.position
        #nhắm đến ô tán xạ khi gần hơn 8 ô
        else:
            self.scatter()

class Background:
    def __init__(self, sprite):
        self.sprite = sprite

#đại diện cho mê cung và các bức tường của nó
class Maze:
    def __init__(self, sprites, setup):
        self.setup = setup
        #tải tất cả các sprite cho nền mê cung như viên bi, viên bi siêu và nền
        self.sprites = sprites
        '''
        ranh giới mê cung tự nó được đại diện bởi mảng nhị phân 2d trong đó 1 đại diện cho một bức tường và 0 đại diện cho một không gian có thể di chuyển, loại bỏ việc khởi tạo mê cung ban đầu
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

        #giữ theo dõi nơi các viên bi ở trên mê cung
        self.maze_elems = [[elements.EMPTY for x in range(self.setup.X_CELLS)] for y in range(self.setup.Y_CELLS)]
        #bắt đầu với các viên bi ở vị trí ban đầu của chúng
        self.fill_maze()

        #xác định các điểm đường hầm mà pacman có thể đi qua
        self.tunnel_points = [(0,14), (27,14)]
        self.tunnel_left = self.tunnel_right[0]
        self.tunnel_right = self.tunnel_points[1]
        
        #biểu diễn đồ họa của mê cung cho việc tìm đường của ma quái
        self.graph = self.construct_graph()

    #hoàn toàn đặt lại mê cung mà không cần tải lại các sprite
    def reset(self):
        self.maze_elems = [[elements.EMPTY for x in range(self.setup.X_CELLS)] for y in range(self.setup.Y_CELLS)]
        self.fill_maze()

    #màu tất cả các đối tượng va chạm trong mê cung
    def debug_display_maze(self, screen):
        for y in range(len(self.maze_boundaries)):
            for x in range(len(self.maze_boundaries[y])):
                if self.maze_boundaries[y][x] == 1:
                    pyg.draw.rect(screen, (random.randint(0,255), random.randint(0,255), random.randint(0,255)), (x*8*self.setup.SCALE, y*8*self.setup.SCALE, 8*self.setup.SCALE, 8*self.setup.SCALE))
        pyg.display.flip()

    #điền mê cung với các phần tử đúng
    def fill_maze(self):
        for y in range(self.setup.Y_CELLS):
            for x in range(self.setup.X_CELLS):
                #đặt các đối tượng tường tại các ranh giới 
                if self.maze_boundaries[y][x] == 1:
                    self.maze_elems[y][x] = elements.WALL

                #đặt các viên bi siêu ở 4 vị trí sinh
                elif (y == 3 or y == 23) and (x == 1 or x == 26):
                    self.maze_elems[y][x] = elements.POWER_PELLET

                #đặt cột viên bi đi qua giữa mê cung
                elif x == 6 or x == 21:
                    self.maze_elems[y][x] = elements.PELLET
                
                #các viên bi được đặt trong mọi ô trống ngoại trừ lồng ma quái và đường hầm và giữa
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
        #bắt đầu với 240 viên bi 240-remaining là số viên bi mà anh ta đã ăn
        return 240 - remaining

    #đặt một quả anh đào trên bảng
    def place_cherry(self):
        placed = False
        #tìm một vị trí ngẫu nhiên để đặt quả anh đào
        while not placed:
            random_x = random.randint(0, self.setup.X_CELLS - 1)
            random_y = random.randint(0, self.setup.Y_CELLS - 1)
            #quả anh đào phải được đặt trên một không gian mở, không thể đặt bên trong lồng
            if (not (random_y > 12 and random_y < 16)) and self.maze_elems[random_y][random_x] == elements.EMPTY:
                self.maze_elems[random_y][random_x] = elements.CHERRY
                placed = True
        
    def construct_graph(self):
        graph = {}
        for y in range(self.setup.Y_CELLS):
            for x in range(self.setup.X_CELLS):
                if self.maze_boundaries[y][x] == 0:  # Chỉ xem xét các không gian trống
                    neighbors = []
                    #xem xét đường hầm như một kết nối giữa hai điểm
                    #trường hợp đặc biệt cho đường hầm
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

    #hiển thị mê cung trên màn hình
    def display(self, screen):
        #đặt lại màn hình
        screen.fill((0, 0, 0))
        #hiển thị nền
        screen.blit(self.sprites['background'], (0, 0))
        #thêm các viên bi và viên bi siêu lên nền
        for y in range(self.setup.Y_CELLS):
            for x in range(self.setup.X_CELLS):
                if self.maze_elems[y][x] == elements.PELLET:
                    screen.blit(self.sprites['pellet'], (x*8*self.setup.SCALE, y*8*self.setup.SCALE))
                elif self.maze_elems[y][x] == elements.POWER_PELLET:
                    screen.blit(self.sprites['power_pellet'], (x*8*self.setup.SCALE, y*8*self.setup.SCALE))
                elif self.maze_elems[y][x] == elements.CHERRY:
                    screen.blit(self.sprites['cherry'], (x*8*self.setup.SCALE, y*8*self.setup.SCALE))


class Game:
    def __init__(self, setup, clock, is_displaying):
        self.setup = setup
        self.screen = setup.SCREEN
        #khởi tạo đồ họa với bảng sprite chứa tất cả hình ảnh của pacman và ma quái
        graphics = Graphics(self.setup)

        #khởi tạo người chơi và các biến trò chơi
        self.player = Player('Schools Dollar')

        #thiết lập các sprite
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

        #được sử dụng để theo dõi khi nào hoạt ảnh khởi động đang phát và khi nào bắt đầu trò chơi
        self.start_frame = 0
        self.starting_up = True
        #khung mà hoạt ảnh khởi động kết thúc
        self.end_frames = 10

        self.death_frame = 0
        self.death_end_frames = 10

        self.is_dead = False

        #giữ theo dõi đồng hồ trò chơi
        self.game_timer = Stopwatch()
        self.frightened_timer = Stopwatch()
        #bao nhiêu giây ma quái sẽ bị sợ hãi
        self.frightened_time = 10

        #giữ theo dõi chế độ mà ma quái đang ở
        self.mode = 'scatter'

        #giữ theo dõi xem một quả anh đào đã được đặt hay chưa
        self.cherry_placed = False

        #giữ theo dõi khi trò chơi kết thúc
        self.game_over_bool = False

    #phát hoạt ảnh khởi động và bắt đầu vòng lặp trò chơi
    def start(self):
        #phát âm thanh khởi động bắt đầu từ khung đầu tiên
        if(self.start_frame == 0):
            #đặt lại vị trí ma quái 
            for ghost in self.ghosts.values():
                ghost.reset()
            #đặt lại vị trí pacman
            self.pacman.reset()

            #chỉ phát âm thanh trong vòng đầu tiên, không phải trong các lần đặt lại khác
            if self.player.lives == 3 and self.is_displaying:
                sound = pyg.mixer.Sound(SoundEffects.startup_effect)   
                sound.play()

        if self.is_displaying:
            #phát hoạt ảnh khởi động (chỉ là pacman chờ trong vài giây)
            self.maze.display(self.screen)
            #vì vị trí nằm ở điểm trung tâm của pacman nên chúng ta cần điều chỉnh vị trí đến góc trên bên trái của sprite
            sprite = self.pacman.sprites['start'][0]
            x,y = self.pacman.position
            sub_x, sub_y = self.pacman.subposition
            self.screen .blit(sprite, ((x*8+sub_x-4)*self.setup.SCALE, (y*8+sub_y-4)*self.setup.SCALE))        
            for ghost in self.ghosts.values():
                ghost.display(self.screen, flash = False)
                
            #hiển thị văn bản sẵn sàng ở giữa màn hình
            text = self.setup.ARCADE_FONT_LARGE.render('SẴN SÀNG?', True, (255, 255, 255))
            self.screen.blit(text, (self.setup.SCREEN_WIDTH/2.75, self.setup.SCREEN_HEIGHT/2.1))

        #tăng khung đếm
        self.start_frame += 1

        #khung cuối cùng của khởi động
        if(self.start_frame == self.end_frames - 1):
            #bắt đầu nhạc nền ngay khi khởi động kết thúc
            if self.is_displaying:
                SoundEffects.background_channel.play(SoundEffects.background_effect, loops = -1)
            #bắt đầu đồng hồ trò chơi
            self.game_timer.start()
            self.starting_up = False
    
    #phát hoạt ảnh cái chết và đặt lại trò chơi
    def reset_round(self):
        #phát âm thanh cái chết
        if self.death_frame == 0:
            #đặt lại đồng hồ
            self.game_timer.stop()
            if self.is_displaying:
                #cắt tất cả các âm thanh khác
                SoundEffects.background_channel.stop()
                SoundEffects.eating_channel.stop()
                SoundEffects.startup_channel.stop()

                SoundEffects.death_channel.play(SoundEffects.death_effect)
        #phát hoạt ảnh cái chết
        #Cứng hóa hoạt ảnh cái chết
        death_sprite = None
        if self.death_frame < self.death_end_frames/11:
            death_sprite = self.pacman.sprites['death'][0]
        elif self.death_frame < 2*self.death_end_frames/11:
            death_sprite = self.pacman.sprites['death'][1]
        elif self.death_frame < 3*self.death_end_frames/11:
            death_sprite = self.pacman.sprites['death'][2]
        elif self.death_frame < 4*self.death_end_frames/11:
            death_sprite = self.pacman.sprites['death'][3]
        elif self.death_frame < 5*self.death_end_frames/11:
            death_sprite = self.pacman.sprites['death'][4]
        elif self.death_frame < 6*self.death_end_frames/11:
            death_sprite = self.pacman.sprites['death'][5]
        elif self.death_frame < 7*self.death_end_frames/11:
            death_sprite = self.pacman.sprites['death'][6]
        elif self.death_frame < 8*self.death_end_frames/11:
            death_sprite = self.pacman.sprites['death'][7]
        elif self.death_frame < 9*self.death_end_frames/11:
            death_sprite = self.pacman.sprites['death'][8]
        elif self.death_frame < 10*self.death_end_frames/11:
            death_sprite = self.pacman.sprites['death'][9]
        else:
            death_sprite = self.pacman.sprites['death'][10]

        #tăng khung đếm
        self.death_frame += 1

        #phát hoạt ảnh cái chết
        self.maze.display(self.screen)
        #vì vị trí nằm ở điểm trung tâm của pacman nên chúng ta cần điều chỉnh vị trí đến góc trên bên trái của sprite
        x,y = self.pacman.position
        sub_x, sub_y = self.pacman.subposition
        self.screen.blit(death_sprite, ((x*8+sub_x-4)*self.setup.SCALE, (y*8+sub_y-4)*self.setup.SCALE))        

        #kết thúc việc đặt lại
        if (self.death_frame == self.death_end_frames-1):
            self.is_dead = False
            self.death_frame = 0
            self.start_frame = 0
            #điều này sẽ khiến trò chơi chạy lại hoạt ảnh khởi động và đặt lại bảng
            self.starting_up = True
            #đặt lại vị trí của ma quái và pacman
            self.pacman.position = self.setup.PACMAN_START

    def update(self):
        
        #vòng lặp cái chết
        if self.is_dead and self.death_frame < self.death_end_frames:
            self.reset_round()
            return
        
        #giữ trò chơi hoàn toàn kết thúc, đặt ở đây để cho phép hoạt ảnh cái chết cuối cùng phát
        elif self.player.lives <= 0:
            self.game_over()
            return
        
        elif self.check_win():
            self.win()
        
        #phát hoạt ảnh khởi động và bắt đầu vòng lặp trò chơi
        elif self.start_frame < self.end_frames:
            self.start()
            return

        #vòng lặp trò chơi

        #xác định chế độ của ma quái dựa trên đồng hồ trò chơi, khi không ở chế độ sợ hãi
        if not self.mode == 'frightened':
            self.choose_mode()
        #cố gắng đặt quả anh đào trên bảng
        self.place_cherry()

        # Cập nhật dựa trên đầu vào của người chơi
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

        #cố gắng thực hiện hướng được lưu trữ nếu có
        self.pacman.change_direction(self.pacman.buffered, self.maze)
        self.pacman.move(self.maze)
        #kiểm tra xem pacman đã ăn viên bi siêu chưa
        self.check_frightened()

        self.move_ghosts()

        #kiểm tra va chạm
        self.handle_collisions()

        #không vẽ hiển thị nếu trò chơi đã kết thúc
        if(self.game_over_bool != True):
            self.draw_screen()

    #kiểm tra xem tất cả các viên bi, viên bi siêu và anh đào đã được ăn chưa, nếu có thì trả về true và kết thúc trò chơi với chiến thắng
    def check_win(self):
        for y in range(self.setup.Y_CELLS):
            for x in range(self.setup.X_CELLS):
                if self.maze.maze_elems[y][x] == elements.PELLET or self.maze.maze_elems[y][x] == elements.POWER_PELLET or self.maze.maze_elems[y][x] == elements.CHERRY:
                    return False
        return True

    #kiểm tra xem pacman đã ăn viên bi siêu chưa, và vào chế độ sợ hãi nếu anh ta đã ăn
    def check_frightened(self):
        #kiểm tra xem pacman đã ăn viên bi siêu chưa, bắt đầu đồng hồ nếu có, cũng kéo dài đồng hồ nếu pacman ăn viên bi siêu khác
        if self.pacman.is_supercharged:
            #tạm dừng đồng hồ trò chơi bình thường
            self.game_timer.pause()
            self.mode = 'frightened'
            self.change_mode()
            #bắt đầu đồng hồ cho chế độ sợ hãi
            self.frightened_timer.start()
            self.pacman.is_supercharged = False
            #bắt đầu phát nhạc đáng sợ
            if self.is_displaying:
                SoundEffects.background_channel.stop()
                SoundEffects.background_channel.play(SoundEffects.frightened_effect, loops = -1)

        #chế độ siêu cấp kéo dài 10 giây
        elif self.mode == 'frightened' and self.frightened_timer.get_elapsed_time() > self.frightened_time:
            self.choose_mode()
            self.frightened_timer.stop()
            #bắt đầu phát nhạc nền bình thường
            if self.is_displaying:
                SoundEffects.background_channel.stop()
                SoundEffects.background_channel.play(SoundEffects.background_effect, loops = -1)       
            #khôi phục đồng hồ trò chơi
            self.game_timer.unpause()    
    
    #mỗi khung hình có một cơ hội rất nhỏ để đặt quả anh đào trên bảng
    def place_cherry(self):
        #trung bình nên mất 10 giây để đặt một quả anh đào
        if random.randint(0,600) == 42 and not self.cherry_placed:
            #đặt quả anh đào ở vị trí ngẫu nhiên
            self.maze.place_cherry()
            self.cherry_placed = True

    def handle_collisions(self):
        for ghost in self.ghosts.values():
            #va chạm với pacman trong trạng thái bình thường giết pacman
            if ghost.mode != 'frightened' and self.pacman.collision(ghost):
                self.game_over_bool = True
                self.is_dead = True
            #trong chế độ sợ hãi va chạm với ma quái giết ma qu ái
            elif ghost.mode == 'frightened' and self.pacman.collision(ghost):
                ghost.is_eaten = True
                self.player.update_score(200)
                #hiển thị đã ăn
                self.draw_screen()
                #tạm dừng trò chơi trong 1 giây
                #self.game_timer.pause()
                #self.frightened_timer.pause()
                #cắt tất cả âm thanh khác
                if self.is_displaying:
                    SoundEffects.background_channel.stop()
                    #phát âm thanh ăn ma quái
                    SoundEffects.ghost_eating_channel.play(SoundEffects.ghost_eating_effect)
                #chờ trong 1 giây
                #time.sleep(1)
                #khôi phục trò chơi
                #self.game_timer.unpause()
                #self.frightened_timer.unpause()
                if self.is_displaying:
                    #bắt đầu phát nhạc nền bình thường
                    SoundEffects.background_channel.play(SoundEffects.frightened_effect, loops=-1)

    #xác định chế độ của ma quái dựa trên đồng hồ trò chơi
    def choose_mode(self):
        #0-7 giây tán xạ
        if self.game_timer.get_elapsed_time() < 7:
            self.mode = 'scatter'
            self.change_mode()
        #7-27 giây theo dõi
        elif self.game_timer.get_elapsed_time() < 27:
            self.mode = 'chase'
            self.change_mode()

        #27-34 giây tán xạ
        elif self.game_timer.get_elapsed_time() < 34:
            self.mode = 'scatter'
            self.change_mode()

        #34-54 giây theo dõi
        elif self.game_timer.get_elapsed_time() < 54:
            self.mode = 'chase'
            self.change_mode()
        #54-59 giây tán xạ
        elif self.game_timer.get_elapsed_time() < 59:
            self.mode = 'scatter'
            self.change_mode()
        #59-79 giây theo dõi
        elif self.game_timer.get_elapsed_time() < 79:
            self.mode = 'chase'
            self.change_mode()
        #79-84 giây tán xạ
        elif self.game_timer.get_elapsed_time() < 84:
            self.mode = 'scatter'
            self.change_mode()
        #Theo dõi vô thời hạn
        else:
            self.mode = 'chase'
            self.change_mode()
        
    #thay đổi chế độ của tất cả ma quái trên màn hình
    def change_mode(self):
        for ghost in self.ghosts.values():
            ghost.mode = self.mode

    #cập nhật vị trí của ma quái và cũng giữ theo dõi việc giải phóng chúng khỏi lồng
    def move_ghosts(self):
        self.ghosts['blinky'].update(self.pacman, self.maze)

        #chậm rãi giải phóng ma quái ra khỏi lồng
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
        

    #xảy ra bất cứ khi nào pacman chết, đặt lại vòng nếu anh ta còn mạng và đặt lại trò chơi nếu không
    def lose_life(self):
        self.player.lives -= 1
        self.reset_round()

    def game_over(self):
        self.game_over_bool = True
        #đổ màn hình thành màu đen và hiển thị văn bản nói rằng bạn thua
        self.screen.fill((0,0,0))
        text = self.setup.ARCADE_FONT_LARGE.render('GAME OVER', True, (255, 255, 255))
        self.screen.blit(text, (self.setup.SCREEN_WIDTH/3,self.setup.SCREEN_HEIGHT/2))
        #hiển thị điểm số cuối cùng
        text = self.setup.ARCADE_FONT.render(f'Final Score: {self.player.score}', True, (255, 255, 255))
        self.screen.blit(text, (self.setup.SCREEN_WIDTH/3,self.setup.SCREEN_HEIGHT/1.5))
        #cắt tất cả âm thanh
        SoundEffects.background_channel.stop()
    
    #hiển thị màn hình chiến thắng và điểm cuối
    def win(self):
        if self.is_displaying:
            #đổ màn hình thành màu trắng và hiển thị văn bản nói rằng bạn thắng
            self.screen.fill((255,255,255))
            text = self.setup.ARCADE_FONT_LARGE.render('BẠN THẮNG', True, (0, 0, 0))
            self.screen.blit(text, (self.setup.SCREEN_WIDTH/3,self.setup.SCREEN_HEIGHT/2))
            #hiển thị điểm số cuối cùng
            text = self.setup.ARCADE_FONT.render(f'Final Score: {self.player.score}', True, (0, 0, 0))
            self.screen.blit(text, (self.setup.SCREEN_WIDTH/3,self.setup.SCREEN_HEIGHT/1.5))

        #ngay khi chiến thắng bắt đầu phát nhạc chiến thắng
        if not self.game_over_bool and self.is_displaying:
            #cắt tất cả âm thanh
            SoundEffects.background_channel.stop()
            #phát âm thanh chiến thắng
            SoundEffects.background_channel.play(SoundEffects.win_effect, loops=-1)
        self.game_over_bool = True
        self.won = True

    def draw_screen(self):
        self.maze.display(self.screen)
        self.pacman.display(self.screen)
        if self.mode == "frightened":
            #hiển thị màu xanh bình thường khi sợ hãi
            if self.frightened_timer.get_elapsed_time() < self.frightened_time - 5:
                for ghost in self.ghosts.values():
                    ghost.display(self.screen, flash = False)
            #nhấp nháy trong 5 giây cuối cùng của chế độ sợ hãi
            else:
                for ghost in self.ghosts.values():
                    ghost.display(self.screen, flash = True)
        else:
            for ghost in self.ghosts.values():
                ghost.display(self.screen, flash = False)

        #hiển thị quả anh đào ở góc dưới bên phải nếu chưa được đặt
        if not self.cherry_placed:
            self.screen.blit(self.maze.sprites['cherry'], (self.setup.SCREEN_WIDTH - 2*8*self.setup.SCALE, self.setup.SCREEN_HEIGHT - 2*8*self.setup.SCALE))
        #gỡ lỗi
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
                #bản đồ các chuyển động đến các hướng
        self.direction_map = {
            'L': Direction.LEFT,
            'R': Direction.RIGHT,
            'U': Direction.UP,
            'D': Direction.DOWN
        }

        '''
        thay thế cho các bộ đếm trong trò chơi là để theo dõi số lần
        nếu chúng ta giả định rằng chúng ta muốn trò chơi này hiển thị trên màn hình 60fps khi nó không được đào tạo thì 
        sẽ có 60 lần mỗi giây có nghĩa là mỗi lần là 1/60 giây hoặc khoảng 16.6666666667 mili giây
        '''
        self.ticks = {
            'game': 0,
            'frightened': 0
        }

        #được sử dụng để tạm dừng luồng trò chơi khi ở chế độ ngắt như sợ hãi hoặc cái chết
        self.game_ticks_paused = False
        #giữ theo dõi khi ở chế độ sợ hãi
        self.frightened_ticks_paused = True

        #giữ theo dõi xem trò chơi đã thắng hay thua
        self.won = False

        #xác định số lần di chuyển mà mỗi gen ánh xạ
        self.gene_multiplier = 1
        self.gene_current_number = 0

    #hàm trợ giúp để chuyển đổi giữa ticks và giây, chuyển đổi là mỗi tick là 1/60 giây
    def ticks_to_seconds(self, ticks):
        return ticks/60
    def seconds_to_ticks(self, seconds):
        return seconds*60
    
    #khởi động lại trò chơi hoàn toàn mà không cần tải lại các đối tượng
    def complete_restart(self, new_gene):
        self.gene = new_gene.upper()
        self.genetic_moves = iter(self.gene)

        self.ticks = {
            'game': 0,
            'frightened': 0
        }

        #được sử dụng để tạm dừng luồng trò chơi khi ở chế độ ngắt như sợ hãi hoặc cái chết
        self.game_ticks_paused = False
        #giữ theo dõi khi ở chế độ sợ hãi
        self.frightened_ticks_paused = True

        #giữ theo dõi xem trò chơi đã thắng hay thua
        self.won = False

        #xác định số lần di chuyển mà mỗi gen ánh xạ
        self.gene_multiplier = 1
        self.gene_current_number = 0

        self.player = Player('Schools Dollar')

        self.start_frame = 0
        self.starting_up = True
        #khung mà hoạt ảnh khởi động kết thúc
        self.end_frames = 10

        self.death_frame = 0
        self.death_end_frames = 10

        self.is_dead = False

        #bao nhiêu giây ma quái sẽ bị sợ hãi
        self.frightened_time = 10

        #giữ theo dõi chế độ mà ma quái đang ở
        self.mode = 'scatter'

        #giữ theo dõi xem một quả anh đào đã được đặt hay chưa
        self.cherry_placed = False

        #giữ theo dõi khi trò chơi kết thúc
        self.game_over_bool = False
        self.maze.reset()
        self.pacman.reset()
        for ghost in self.ghosts.values():
            ghost.reset()
        self.pacman.player = self.player

    #Thực hiện gen bằng cách đọc qua nhiễm sắc thể và trả về chuyển động tiếp theo trong chuỗi
    def choose_gene_move(self):
        next_move = next(self.genetic_moves, 'N')
        if next_move == 'N':
            return self.last_move
        self.last_move = next_move
        return self.direction_map[next_move]

    def start(self):
        #đặt lại vị trí ma quái 
        for ghost in self.ghosts.values():
            ghost.reset()
        #đặt lại vị trí pacman
        self.pacman.reset()
        #bắt đầu đồng hồ trò chơi
        self.game_timer.start()
        self.starting_up = False

    def update(self):
        
        #vòng lặp cái chết
        if self.is_dead and self.death_frame < self.death_end_frames:
            self.reset_round()
            return
        
        #giữ trò chơi hoàn toàn kết thúc, đặt ở đây để cho phép hoạt ảnh cái chết cuối cùng phát
        elif self.player.lives <= 0:
            self.game_over()
            return
        
        elif self.check_win():
            self.win()

        #phát hoạt ảnh khởi động và bắt đầu vòng lặp trò chơi
        elif self.starting_up:
            self.start()
            return

        #vòng lặp trò chơi

        #xác định chế độ của ma quái dựa trên đồng hồ trò chơi, khi không ở chế độ sợ hãi
        if not self.mode == 'frightened':
            self.choose_mode()
        #cố gắng đặt quả anh đào trên bảng

        #TẠM THỜI LOẠI BỎ ĐỂ THỬ NGHIỆM
        #self.place_cherry()

        gene_move_direction = self.choose_gene_move()
        Pacman.change_direction(self.pacman, gene_move_direction, self.maze)

        #cố gắng thực hiện hướng được lưu trữ nếu có
        self.pacman.change_direction(self.pacman.buffered, self.maze)
        self.pacman.move(self.maze)

        #kiểm tra xem pacman đã ăn viên bi siêu chưa
        self.check_frightened()

        self.move_ghosts()

        #kiểm tra va chạm
        self.handle_collisions()

        #cập nhật số lần trò chơi
        if not self.game_ticks_paused:
            self.ticks['game'] += 1
        if not self.frightened_ticks_paused:
            self.ticks['frightened'] += 1

        #không vẽ hiển thị nếu trò chơi đã kết thúc
        if(self.game_over_bool != True and self.is_displaying):
            self.draw_screen()
    
    #ghi đè logic chọn chế độ cơ bản để hoạt động dựa trên số lần thay vì đồng hồ thực tế
    def choose_mode(self):
        #0-7 giây tán xạ
        if self.ticks ['game'] < self.seconds_to_ticks(7):
            self.mode = 'scatter'
            self.change_mode()
        #7-27 giây theo dõi
        elif self.ticks['game'] < self.seconds_to_ticks(27):
            self.mode = 'chase'
            self.change_mode()

        #27-34 giây tán xạ
        elif self.ticks['game'] < self.seconds_to_ticks(34):
            self.mode = 'scatter'
            self.change_mode()

        #34-54 giây theo dõi
        elif self.ticks['game'] < self.seconds_to_ticks(54):
            self.mode = 'chase'
            self.change_mode()
        #54-59 giây tán xạ
        elif self.ticks['game'] < self.seconds_to_ticks(59):
            self.mode = 'scatter'
            self.change_mode()
        #59-79 giây theo dõi
        elif self.ticks['game'] < self.seconds_to_ticks(79):
            self.mode = 'chase'
            self.change_mode()
        #79-84 giây tán xạ
        elif self.ticks['game'] < self.seconds_to_ticks(84):
            self.mode = 'scatter'
            self.change_mode()
        #Theo dõi vô thời hạn
        else:
            self.mode = 'chase'
            self.change_mode()

    #ghi đè logic kiểm tra sợ hãi cơ bản để hoạt động dựa trên số lần thay vì đồng hồ thực tế
    #cập nhật vị trí của ma quái và cũng giữ theo dõi việc giải phóng chúng khỏi lồng
    def move_ghosts(self):
        self.ghosts['blinky'].update(self.pacman, self.maze)

        #chậm rãi giải phóng ma quái ra khỏi lồng
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

    #ghi đè logic kiểm tra sợ hãi cơ bản để hoạt động dựa trên số lần thay vì đồng hồ thực tế
    #kiểm tra xem pacman đã ăn viên bi siêu chưa, và vào chế độ sợ hãi nếu anh ta đã ăn
    def check_frightened(self):
        #kiểm tra xem pacman đã ăn viên bi siêu chưa, bắt đầu đồng hồ nếu có, cũng kéo dài đồng hồ nếu pacman ăn viên bi siêu khác
        if self.pacman.is_supercharged:
            #tạm dừng đồng hồ trò chơi bình thường
            self.game_ticks_paused = True
            self.mode = 'frightened'
            self.change_mode()
            #bắt đầu đồng hồ cho chế độ sợ hãi
            self.frightened_ticks_paused = False

            self.pacman.is_supercharged = False
            #bắt đầu phát nhạc đáng sợ
            if self.is_displaying:
                SoundEffects.background_channel.stop()
                SoundEffects.background_channel.play(SoundEffects.frightened_effect, loops = -1)

        #chế độ siêu cấp kéo dài 10 giây
        elif self.mode == 'frightened' and self.ticks['frightened'] > self.seconds_to_ticks(self.frightened_time):
            self.choose_mode()

            #đặt lại chế độ sợ hãi
            self.ticks['frightened'] = 0
            self.frightened_ticks_paused = True

            #bắt đầu phát nhạc nền bình thường
            if self.is_displaying:
                SoundEffects.background_channel.stop()
                SoundEffects.background_channel.play(SoundEffects.background_effect, loops = -1)       
            #khôi phục đồng hồ trò chơi
            self.game_ticks_paused = False

    #ghi đè logic vẽ màn hình cơ bản để hoạt động dựa trên số lần thay vì đồng hồ thực tế
    def draw_screen(self):
        self.maze.display(self.screen)
        self.pacman.display(self.screen)
        if self.mode == "frightened":
            #hiển thị màu xanh bình thường khi sợ hãi
            if self.ticks['frightened'] < self.seconds_to_ticks(self.frightened_time - 5):
                for ghost in self.ghosts.values():
                    ghost.display(self.screen, flash = False)
            #nhấp nháy trong 5 giây cuối cùng của chế độ sợ hãi
            else:
                for ghost in self.ghosts.values():
                    ghost.display(self.screen, flash = True)
        else:
            for ghost in self.ghosts.values():
                ghost.display(self.screen, flash = False)

        #hiển thị quả anh đào ở góc dưới bên phải nếu chưa được đặt
        if not self.cherry_placed:
            self.screen.blit(self.maze.sprites['cherry'], (self.setup.SCREEN_WIDTH - 2*8*self.setup.SCALE, self.setup.SCREEN_HEIGHT - 2*8*self.setup.SCALE))
        #gỡ lỗi
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
                #bản đồ các chuyển động đến các hướng
        self.direction_map = {
            'L': Direction.LEFT,
            'R': Direction.RIGHT,
            'U': Direction.UP,
            'D': Direction.DOWN
        }

        '''
        thay thế cho các bộ đếm trong trò chơi là để theo dõi số lần
        nếu chúng ta giả định rằng chúng ta muốn trò chơi này hiển thị trên màn hình 60fps khi nó không được đào tạo thì 
        sẽ có 60 lần mỗi giây có nghĩa là mỗi lần là 1/60 giây hoặc khoảng 16.6666666667 mili giây
        '''
        self.ticks = {
            'game': 0,
            'frightened': 0
        }

        #được sử dụng để tạm dừng luồng trò chơi khi ở chế độ ngắt như sợ hãi hoặc cái chết
        self.game_ticks_paused = False
        #giữ theo dõi khi ở chế độ sợ hãi
        self.frightened_ticks_paused = True

        #giữ theo dõi xem trò chơi đã thắng hay thua
        self.won = False

        #xác định số lần di chuyển mà mỗi gen ánh xạ
        self.gene_multiplier = 1
        self.gene_current_number = 0

    #hàm trợ giúp để chuyển đổi giữa ticks và giây, chuyển đổi là mỗi tick là 1/60 giây
    def ticks_to_seconds(self, ticks):
        return ticks/60
    def seconds_to_ticks(self, seconds):
        return seconds*60
    
    #khởi động lại trò chơi hoàn toàn mà không cần tải lại các đối tượng
    def complete_restart(self, new_gene):
        self.gene = new_gene.upper()
        self.genetic_moves = iter(self.gene)

        self.ticks = {
            'game': 0,
            'frightened': 0
        }

        #được sử dụng để tạm dừng luồng trò chơi khi ở chế độ ngắt như sợ hãi hoặc cái chết
        self.game_ticks_paused = False
        #giữ theo dõi khi ở chế độ sợ hãi
        self.frightened_ticks_paused = True

        #giữ theo dõi xem trò chơi đã thắng hay thua
        self.won = False

        #xác định số lần di chuyển mà mỗi gen ánh xạ
        self.gene_multiplier = 1
        self.gene_current_number = 0

        self.player = Player('Schools Dollar')

        self.start_frame = 0
        self.starting_up = True
        #khung mà hoạt ảnh khởi động kết thúc
        self.end_frames = 10

        self.death_frame = 0
        self.death_end_frames = 10

        self.is_dead = False

        #bao nhiêu giây ma quái sẽ bị sợ hãi
        self.frightened_time = 10

        #giữ theo dõi chế độ mà ma quái đang ở
        self.mode = 'scatter'

        #giữ theo dõi xem một quả anh đào đã được đặt hay chưa
        self.cherry_placed = False

        #giữ theo dõi khi trò chơi kết thúc
        self.game_over_bool = False
        self.maze.reset()
        self.pacman.reset()
        for ghost in self.ghosts.values():
            ghost.reset()
        self.pacman.player = self.player

    #Thực hiện gen bằng cách đọc qua nhiễm sắc thể và trả về chuyển động tiếp theo trong chuỗi
    def choose_gene_move(self):
        next_move = next(self.genetic_moves, 'N')
        if next_move == 'N':
            return self.last_move
        self.last_move = next_move
        return self.direction_map[next_move]

    def start(self):
        #đặt lại vị trí ma quái 
        for ghost in self.ghosts.values():
            ghost.reset()
        #đặt lại vị trí pacman
        self.pacman.reset()
        #bắt đầu đồng hồ trò chơi
        self.game_timer.start()
        self.starting_up = False

    def update(self):
        
        #vòng lặp cái chết
        if self.is_dead and self.death_frame < self.death_end_frames:
            self.reset_round()
            return
        
        #giữ trò chơi hoàn toàn kết thúc, đặt ở đây để cho phép hoạt ảnh cái chết cuối cùng phát
        elif self.player.lives <= 0:
            self.game_over()
            return
        
        elif self.check_win():
            self.win()

        #phát hoạt ảnh khởi động và bắt đầu vòng lặp trò chơi
        elif self.starting_up:
            self.start()
            return

        #vòng lặp trò chơi

        #xác định chế độ của ma quái dựa trên đồng hồ trò chơi, khi không ở chế độ sợ hãi
        if not self.mode == 'frightened':
            self.choose_mode()
        #cố gắng đặt quả anh đào trên bảng

        #TẠM THỜI LOẠI BỎ ĐỂ THỬ NGHIỆM
        #self.place_cherry()

        gene_move_direction = self.choose_gene_move()
        Pacman.change_direction(self.pacman, gene_move_direction, self.maze)

        #cố gắng thực hiện hướng được lưu trữ nếu có
        self.pacman.change_direction(self.pacman.buffered, self.maze)
        self.pacman.move(self.maze)

        #kiểm tra xem pacman đã ăn viên bi siêu chưa
        self.check_frightened()

        self.move_ghosts()

        #kiểm tra va chạm
        self.handle_collisions()

        #cập nhật số lần trò chơi
        if not self.game_ticks_paused:
            self.ticks['game'] += 1
        if not self.frightened_ticks_paused:
            self.ticks['frightened'] += 1

        #không vẽ hiển thị nếu trò chơi đã kết thúc
        if(self.game_over_bool != True and self.is_displaying):
            self.draw_screen()
    
    #ghi đè logic chọn chế độ cơ bản để hoạt động dựa trên số lần thay vì đồng hồ thực tế
    def choose_mode(self):
        #0-7 giây tán xạ
        if self.ticks ['game'] < self.seconds_to_ticks(7):
            self.mode = 'scatter'
            self.change_mode()
        #7-27 giây theo dõi
        elif self.ticks['game'] < self.seconds_to_ticks(27):
            self.mode = 'chase'
            self.change_mode()

        #27-34 giây tán xạ
        elif self.ticks['game'] < self.seconds_to_ticks(34):
            self.mode = 'scatter'
            self.change_mode()

        #34-54 giây theo dõi
        elif self.ticks['game'] < self.seconds_to_ticks(54):
            self.mode = 'chase'
            self.change_mode()
        #54-59 giây tán xạ
        elif self.ticks['game'] < self.seconds_to_ticks(59):
            self.mode = 'scatter'
            self.change_mode()
        #59-79 giây theo dõi
        elif self.ticks['game'] < self.seconds_to_ticks(79):
            self.mode = 'chase'
            self.change_mode()
        #79-84 giây tán xạ
        elif self.ticks['game'] < self.seconds_to_ticks(84):
            self.mode = 'scatter'
            self.change_mode()
        #Theo dõi vô thời hạn
        else:
            self.mode = 'chase'
            self.change_mode()

    #ghi đè logic kiểm tra sợ hãi cơ bản để hoạt động dựa trên số lần thay vì đồng hồ thực tế
    #cập nhật vị trí của ma quái và cũng giữ theo dõi việc giải phóng chúng khỏi lồng
    def move_ghosts(self):
        self.ghosts['blinky'].update(self.pacman, self.maze)

        #chậm rãi giải phóng ma quái ra khỏi lồng
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

    #xảy ra bất cứ khi nào pacman chết, đặt lại vòng nếu anh ta còn mạng và đặt lại trò chơi nếu không
    def lose_life(self):
        self.player.lives -= 1
        self.reset_round()

    def game_over(self):
        self.game_over_bool = True
        #đổ màn hình thành màu đen và hiển thị văn bản nói rằng bạn thua
        self.screen.fill((0,0,0))
        text = self.setup.ARCADE_FONT_LARGE.render('GAME OVER', True, (255, 255, 255))
        self.screen.blit(text, (self.setup.SCREEN_WIDTH/3,self.setup.SCREEN_HEIGHT/2))
        #hiển thị điểm số cuối cùng
        text = self.setup.ARCADE_FONT.render(f'Final Score: {self.player.score}', True, (255, 255, 255))
        self.screen.blit(text, (self.setup.SCREEN_WIDTH/3,self.setup.SCREEN_HEIGHT/1.5))
        #cắt tất cả âm thanh
        SoundEffects.background_channel.stop()
    
    #hiển thị màn hình chiến thắng và điểm cuối
    def win(self):
        if self.is_displaying:
            #đổ màn hình thành màu trắng và hiển thị văn bản nói rằng bạn thắng
            self.screen.fill((255,255,255))
            text = self.setup.ARCADE_FONT_LARGE.render('BẠN THẮNG', True, (0, 0, 0))
            self.screen.blit(text, (self.setup.SCREEN_WIDTH/3,self.setup.SCREEN_HEIGHT/2))
            #hiển thị điểm số cuối cùng
            text = self.setup.ARCADE_FONT.render(f'Final Score: {self.player.score}', True, (0, 0, 0))
            self.screen.blit(text, (self.setup.SCREEN_WIDTH/3,self.setup.SCREEN_HEIGHT/1.5))

        #ngay khi chiến thắng bắt đầu phát nhạc chiến thắng
        if not self.game_over_bool and self.is_displaying:
            #cắt tất cả âm thanh
            SoundEffects.background_channel.stop()
            #phát âm thanh chiến thắng
            SoundEffects.background_channel.play(SoundEffects.win_effect, loops=-1)
        self.game_over_bool = True
        self.won = True

    def draw_screen(self):
        self.maze.display(self.screen)
        self.pacman.display(self.screen)
        if self.mode == "frightened":
            #hiển thị màu xanh bình thường khi sợ hãi
            if self.ticks['frightened'] < self.seconds_to_ticks(self.frightened_time - 5):
                for ghost in self.ghosts.values():
                    ghost.display(self.screen, flash = False)
            #nhấp nháy trong 5 giây cuối cùng của chế độ sợ hãi
            else:
                for ghost in self.ghosts.values():
                    ghost.display(self.screen, flash = True)
        else:
            for ghost in self.ghosts.values():
                ghost.display(self.screen, flash = False)

        #hiển thị quả anh đào ở góc dưới bên phải nếu chưa được đặt
        if not self.cherry_placed:
            self.screen.blit(self.maze.sprites['cherry'], (self.setup.SCREEN_WIDTH - 2*8*self.setup.SCALE, self.setup.SCREEN_HEIGHT - 2*8*self.setup.SCALE))
        #gỡ lỗi
        font = pyg.font.Font(None, 36)
        text = self.setup.ARCADE_FONT.render(f'FPS: {self.clock.get_fps()}', True, (255, 255, 255))
        self.screen.blit(text, (450,10))
        #text = ARCADE_FONT.render(f'Mode: {self.mode}', True, (255, 255, 255))
        #self.screen.blit(text, (250, SCREEN_HEIGHT - 30))

class Pacman_Game():
    def test_game(self, frame_rate):
        # Tạo trò chơi
        clock = pyg.time.Clock()
        setup = Game_Setup()
        game = Game(setup, clock, True)

        # Vòng lặp trò chơi chính
        while True:
            # Cập nhật trò chơi
            game.update()

            #cập nhật hiển thị
            pyg.display.flip()

            #giới hạn tốc độ khung hình 
            clock.tick(frame_rate)
    
    def execute_moves(self, move_string):
        #bản đồ các chuyển động đến các hướng
        direction_map = {
            'L': Direction.LEFT,
            'R': Direction.RIGHT,
            'U': Direction.UP,
            'D': Direction.DOWN
        }

        #chỉ số của chuyển động hiện tại trong chuỗi
        moves = move_string.upper()
        print(moves)
        move_iter = iter(moves)
        setup = Game_Setup()
        # Tạo trò chơi
        game = Game(setup, pyg.time.Clock(), False)
        while True:
            try:
                move = next(move_iter)
            except StopIteration:
                break

    def genetic_test(self, gene):
        # Tạo trò chơi
        clock = pyg.time.Clock()
        setup = Game_Setup()

        best_score = 0
        is_displaying = False
        for i in range(100):
            game = Genetic_Game(setup, clock, gene, is_displaying)
            # Vòng lặp trò chơi chính
            while game.game_over_bool != True:
                # Cập nhật trò chơi
                game.update()

                #cập nhật hiển thị
                if is_displaying:
                    pyg.display.flip()
                    clock.tick(60)

            if game.player.score > best_score:
                best_score = game.player.score

        return game.player.score

if __name__ == "__main__":
    main()
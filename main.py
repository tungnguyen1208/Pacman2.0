import pygame
import sys
import subprocess

def draw_button(screen, rect, color, text, text_color, shadow_offset=3, border_radius=5):
    shadow_rect = rect.move(shadow_offset, shadow_offset)
    pygame.draw.rect(screen, (50, 50, 50), shadow_rect, border_radius=border_radius)  # Đổ bóng
    pygame.draw.rect(screen, color, rect, border_radius=border_radius)  # Nút chính
    pygame.draw.rect(screen, (0, 0, 0), rect, 5, border_radius=border_radius)  # Viền

    font = pygame.font.Font(None, 40)
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)

def start_screen():
    pygame.init()
    screen = pygame.display.set_mode((736, 443))  # Kích thước màn hình start menu
    background_image = pygame.image.load("assets/start_images/image2.jpg")
    background_image = pygame.transform.scale(background_image, (736, 443))

    start_button_rect = pygame.Rect(300, 290, 150, 50)  # Điều chỉnh lại vị trí nút Start
    quit_button_rect = pygame.Rect(300, 350, 150, 50)  # Điều chỉnh lại vị trí nút Quit

    while True:
        screen.blit(background_image, (0, 0))
        draw_button(screen, start_button_rect, (255, 69, 0), "Start", (255, 255, 255))
        draw_button(screen, quit_button_rect, (200, 0, 0), "Quit", (255, 255, 255))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button_rect.collidepoint(event.pos):
                    pygame.quit()
                    subprocess.run(["python", "pacman.py"])  # Chạy game
                    sys.exit()
                if quit_button_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

if __name__ == "__main__":
    start_screen()

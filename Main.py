import pygame, sys, os, random

clock = pygame.time.Clock()

from pygame.locals import *

pygame.init()  # Inicia Pygame

pygame.display.set_caption('Pygame Plataformero')

WINDOW_SIZE = (600, 400)

screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)  # Inicio de pantalla

display = pygame.Surface((300, 200))  # Usado como la superficie de renderizado, la cual es escalada

moving_right = False
moving_left = False
vertical_momentum = 0
air_timer = 0
jump_counter = 0

true_scroll = [0, 0]


def load_map(path):
    f = open(path + '.txt', 'r')
    data = f.read()
    f.close()
    data = data.split('\n')
    game_map = []
    for row in data:
        game_map.append(list(row))
    return game_map


global animation_frames
animation_frames = {}


def load_animation(path, frame_durations):
    global animation_frames
    animation_name = path.split('/')[-1]
    animation_frame_data = []
    n = 0
    for frame in frame_durations:
        animation_frame_id = animation_name + '_' + str(n)
        img_loc = path + '/' + animation_frame_id + '.png'
        # animaciones/Dragoncito/Dragoncito_#.png
        animation_image = pygame.image.load(img_loc).convert_alpha()
        animation_frames[animation_frame_id] = animation_image.copy()
        for i in range(frame):
            animation_frame_data.append(animation_frame_id)
        n += 1
    return animation_frame_data


def change_action(action_var, frame, new_value):
    if action_var != new_value:
        action_var = new_value
        frame = 0
    return action_var, frame


animation_database = {}

animation_database['run'] = load_animation('animaciones/Dragoncito caminando', [5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5])
animation_database['idle'] = load_animation('animaciones/Dragoncito', [5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5])
animation_database['jumping'] = load_animation('animaciones/Dragoncito Saltando', [20,20])

game_map = load_map('map')

grass_img = pygame.image.load('grass.png')
dirt_img = pygame.image.load('dirt.png')
plataforma_grass_img = pygame.image.load('plataform grass.png')

jump_sound = pygame.mixer.Sound('jump.wav')
grass_sounds = [pygame.mixer.Sound('grass_0.wav'),pygame.mixer.Sound('grass_1.wav')]
grass_sounds[0].set_volume(0.2)
grass_sounds[1].set_volume(0.2)

pygame.mixer.music.load('music.mp3')
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.4)

player_action = 'idle'
player_frame = 0
player_flip = False

grass_sound_timer = 0

player_rect = pygame.Rect(100, 100, 28, 30)

background_objects = [[0.25, [120, 10, 70, 400]], [0.25, [280, 30, 40, 400]], [0.5, [30, 40, 40, 400]],
                      [0.5, [130, 90, 100, 400]], [0.5, [300, 80, 120, 400]]]


def collision_test(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list


def move(rect, movement, tiles):
    collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
    rect.x += movement[0]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types['right'] = True
        elif movement[0] < 0:
            rect.left = tile.right
            collision_types['left'] = True
    rect.y += movement[1]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types['bottom'] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collision_types['top'] = True
    return rect, collision_types


while True:  # Bucle de juego
    display.fill((146, 244, 255))  # Pantalla clara llenandola con azul

    if grass_sound_timer > 0:
        grass_sound_timer -= 1

    true_scroll[0] += (player_rect.x - true_scroll[0] - 152) / 20
    true_scroll[1] += (player_rect.y - true_scroll[1] - 106) / 20
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])

    pygame.draw.rect(display, (7, 80, 75), pygame.Rect(0, 120, 300, 80))
    for background_object in background_objects:
        obj_rect = pygame.Rect(background_object[1][0] - scroll[0] * background_object[0],
                               background_object[1][1] - scroll[1] * background_object[0], background_object[1][2],
                               background_object[1][3])
        if background_object[0] == 0.5:
            pygame.draw.rect(display, (14, 222, 150), obj_rect)
        else:
            pygame.draw.rect(display, (9, 91, 85), obj_rect)

    tile_rects = []
    y = 0
    for layer in game_map:
        x = 0
        for tile in layer:
            if tile == '1':
                display.blit(dirt_img, (x * 16 - scroll[0], y * 16 - scroll[1]))
            if tile == '2':
                display.blit(grass_img, (x * 16 - scroll[0], y * 16 - scroll[1]))
            if tile == '3':
                display.blit(plataforma_grass_img, (x * 16 - scroll[0], y * 16 - scroll[1]))
            if tile != '0':
                tile_rects.append(pygame.Rect(x * 16, y * 16, 16, 16))
            x += 1
        y += 1

    player_movement = [0, 0]
    if moving_right == True:
        player_movement[0] += 2
    if moving_left == True:
        player_movement[0] -= 2
    player_movement[1] += vertical_momentum
    vertical_momentum += 0.2
    if vertical_momentum > 3:
        vertical_momentum = 3

    if player_movement[0] == 0 and player_movement[1] == 0:
        player_action, player_frame = change_action(player_action, player_frame, 'idle')
    if player_movement[0] > 0 and player_movement[1] == 0:
        player_flip = False
        player_action, player_frame = change_action(player_action, player_frame, 'run')
    if player_movement[0] < 0 and player_movement[1] == 0:
        player_flip = True
        player_action, player_frame = change_action(player_action, player_frame, 'run')
        
    if player_movement[1] > 1:
        player_action, player_frame = change_action(player_action, player_frame, 'jumping')
    if player_movement[0] > 0 and player_movement[1] > 1:
        player_flip = False
        player_action, player_frame = change_action(player_action, player_frame, 'jumping')
    if player_movement[0] < 0 and player_movement[1] > 1:
        player_flip = True
        player_action, player_frame = change_action(player_action, player_frame, 'jumping')
    if player_movement[1] < 0:
        player_action, player_frame = change_action(player_action, player_frame, 'jumping')
    if player_movement[0] > 0 and player_movement[1] < 0:
        player_flip = False
        player_action, player_frame = change_action(player_action, player_frame, 'jumping')
    if player_movement[0] < 0 and player_movement[1] < 0:
        player_flip = True
        player_action, player_frame = change_action(player_action, player_frame, 'jumping')


    player_rect, collisions = move(player_rect, player_movement, tile_rects)

    if collisions['bottom'] == True:
        air_timer = 0
        jump_counter = 0
        vertical_momentum = 0
        if player_movement[0] != 0:
            if grass_sound_timer == 0:
                grass_sound_timer = 30
                random.choice(grass_sounds).play()
    else:
        air_timer += 1

    player_frame += 1
    if player_frame >= len(animation_database[player_action]):
        player_frame = 0
    player_img_id = animation_database[player_action][player_frame]
    player_img = animation_frames[player_img_id]
    display.blit(pygame.transform.flip(player_img, player_flip, False),
                 (player_rect.x - scroll[0], player_rect.y - scroll[1]))

    for event in pygame.event.get():  # Bucle de evento
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_RIGHT:
                moving_right = True
            if event.key == K_LEFT:
                moving_left = True
            if jump_counter == 0:
                if event.key == K_UP:
                    if air_timer < 6:
                        jump_sound.play()
                        vertical_momentum = -5
                    if event.key == K_UP:
                        if air_timer > 6:
                            jump_sound.play()
                            vertical_momentum = -5
                            jump_counter = 1


        if event.type == KEYUP:
            if event.key == K_RIGHT:
                moving_right = False
            if event.key == K_LEFT:
                moving_left = False

    screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))
    pygame.display.update()
    clock.tick(60)

import pygame, sys, random

pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)#in pygame docs
pygame.init()

screen = pygame.display.set_mode((432, 768))
clock = pygame.time.Clock()
game_font = pygame.font.Font('FontFlappy.TTF', 40)

gravity = 0.25
bird_movement = 0
game_active = False
score = 0
highscore = 0

#sound
flap_sound = pygame.mixer.Sound('sound/sfx_wing.wav')
hit_sound = pygame.mixer.Sound('sound/sfx_hit.wav')
score_sound = pygame.mixer.Sound('sound/sfx_point.wav')

#create background
bg = pygame.image.load('assests/background-night.png').convert()
bg = pygame.transform.scale2x(bg)

#create floor
floor = pygame.image.load('assests/floor.png').convert()
floor = pygame.transform.scale2x(floor)
floor_x_pos = 0

#create bird
bird_down = pygame.transform.scale2x(pygame.image.load('assests/yellowbird-downflap.png').convert_alpha())
bird_mid = pygame.transform.scale2x(pygame.image.load('assests/yellowbird-midflap.png').convert_alpha())
bird_up = pygame.transform.scale2x(pygame.image.load('assests/yellowbird-upflap.png').convert_alpha())

bird_list = [bird_down, bird_mid, bird_up]

bird_index = 0
bird = bird_list[bird_index]
bird_rect = bird.get_rect(center = (100, 384))

#make bird_index change so that the bird flap its wings
birdflap = pygame.USEREVENT + 1
pygame.time.set_timer(birdflap, 200)

#create a pipe
pipe_surface = pygame.image.load('assests/pipe-green.png').convert()
pipe_surface = pygame.transform.scale2x(pipe_surface)
pipe_list = []

#insert timer
spawnpipe = pygame.USEREVENT
pygame.time.set_timer(spawnpipe, 900)
bottom_pipe_centery = [300, 350, 400, 430]

#game over interface
gameover_surface = pygame.transform.scale2x(pygame.image.load('assests/message.png').convert_alpha())
gameover_rect = gameover_surface.get_rect(center=(216, 384))


#Make floor consecutively
def draw_floor():
    screen.blit(floor, (floor_x_pos, 650))
    screen.blit(floor, (floor_x_pos+432, 650))


#Create new pipe
def create_pipe():
    random_pipe_pos = random.choice(bottom_pipe_centery)

    bottom_pipe = pipe_surface.get_rect(midtop = (500, random_pipe_pos))
    top_pipe = pipe_surface.get_rect(midtop = (500, random_pipe_pos-680))

    return bottom_pipe, top_pipe


#Move the pipe
def move_pipe(pipes):
    for pipe in pipes:
        pipe.centerx -= 5

    return pipes


#draw bottom pipe and draw flipped top pipe
def draw_pipe(pipes):
    for pipe in pipes:
        if pipe.bottom >= 650:
            screen.blit(pipe_surface, pipe)
        else:
            flip_pipe = pygame.transform.flip(pipe_surface, False, True)
            screen.blit(flip_pipe, pipe)


#check if game over
def check_collision(pipes):
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            hit_sound.play()
            return False
        
    if bird_rect.top <= -75 or bird_rect.bottom >= 650:
        hit_sound.play()
        return False
    
    return True


#make the bird rotate
def rotate_bird(bird):
    new_bird = pygame.transform.rotozoom(bird, -bird_movement*3, 1)
    return new_bird


#return the bird with new flapping state and its bird_rect
def bird_animation():
    new_bird = bird_list[bird_index]
    new_bird_rect = new_bird.get_rect(center = (100, bird_rect.centery))
    return new_bird, new_bird_rect


#diplay score and highscore
def score_display(game_state):
    if game_state == 'main_game':
        score_surface = game_font.render('Score: {}'.format(score), True, '#ffffff')
        score_rect = score_surface.get_rect(center = (216, 100))
        screen.blit(score_surface, score_rect)

    if game_state == 'game_over':
        score_surface = game_font.render('Score: {}'.format(score), True, '#ffffff')
        score_rect = score_surface.get_rect(center = (216, 100))
        screen.blit(score_surface, score_rect)

        highscore_surface = game_font.render('High Score: {}'.format(highscore), True, '#ffffff')
        highscore_rect = highscore_surface.get_rect(center = (216, 630))
        screen.blit(highscore_surface, highscore_rect)


#update score
def check_score(score, pipes):
    for pipe in pipes:
        if pipe.bottomright[1] > 650:
            if pipe.topright[0] <= 100 and pipe.topright[0] >= 95:
                score_sound.play()
                score+=1

    return score


#update highscore
def update_highscore(score, highscore):
    if score > highscore:
        highscore = score
    return highscore


while True:
    #Catch all event happen in pygame
    for event in pygame.event.get():
        #event = quit game
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        #press spacebar will rise the bird
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_active:
                # bird_movement = 0
                bird_movement = -6
                flap_sound.play()
            if event.key == pygame.K_SPACE and not game_active:
                game_active = True
                score = 0

                pipe_list.clear()

                bird_rect.center = (100, 384)
                bird_movement = 0

        #create and add new pipe into list each loop
        if event.type == spawnpipe:
            pipe_list.extend(create_pipe())

        #Change bird_index frequently
        if event.type == birdflap:
            bird_index = (bird_index+1)%3
            bird, bird_rect = bird_animation()

    #insert background
    screen.blit(bg, (0,0))
    if game_active:
        #make the bird falling down
        bird_movement += gravity
        rotated_bird = rotate_bird(bird)
        bird_rect.centery += bird_movement
        screen.blit(rotated_bird, bird_rect)
        game_active = check_collision(pipe_list)

        #Move pipes in list and draw it
        pipe_list = move_pipe(pipe_list)
        draw_pipe(pipe_list)
        score = check_score(score, pipe_list)
        score_display('main_game')
    else:
        screen.blit(gameover_surface, gameover_rect)
        highscore = update_highscore(score, highscore)
        score_display('game_over')
        
    #insert floor
    floor_x_pos -= 1
    draw_floor()
    if floor_x_pos <= -432:
        floor_x_pos = 0

    #update after each loop
    pygame.display.update()
    clock.tick(120)

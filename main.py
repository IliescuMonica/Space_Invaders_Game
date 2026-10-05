#Import libraries
import pygame
import random


#Pygame setup
pygame.init()

#Background music
pygame.mixer.init()
pygame.mixer.music.load("sounds/spaceinvaders_song.mpeg")
pygame.mixer.music.play(-1)

#Game window
screen = pygame.display.set_mode((800, 600))
title = pygame.display.set_caption("Space Invaders")
clock = pygame.time.Clock()

#Backround setup
background_image = pygame.image.load("images/background.png")
background_image = pygame.transform.scale(background_image, (800, 600))

#Block size
block_size = 10

def reset_game():
    global player, player_image
    global aliens, alien_image
    global lives, heart_image
    global score, font
    global bomb, alien_bomb
    global barriers
    global game_over, game_won
    global alien_direction
    global explosion_frame, explosion_rect, explosion_timer

    # Score setup
    score = 0
    font = pygame.font.Font("fonts/8bit_font.ttf", 10)

    # Player setup
    player_image = pygame.image.load("images/spaceship.png")
    player = pygame.Rect(375, 550, 50, 30)
    player_image = pygame.transform.scale(player_image, (50, 30))


    #Aliens setup
    aliens = []
    for y in range(80, 201, 40):
        for x in range(100, 641, 100):
            alien = pygame.Rect(x, y, 40, 25)
            aliens.append(alien)

    alien_image = pygame.image.load("images/alien.png")
    alien_image = pygame.transform.scale(alien_image, (40, 25))

    # Lives setup
    heart_image = pygame.image.load("images/heart_life.png")
    heart_image = pygame.transform.scale(heart_image, (35, 35))
    lives_number = 3
    lives = []
    for i in range(lives_number):
        lives.append(pygame.Rect(10 + i * 40, 10, 35, 35))

    # Barriers setup
    barriers = []

    pattern = [
        "  ######  ",
        " ######## ",
        "##########",
        "##      ##",
        "##      ##",
    ]

    for x in range(150, 651, 200):
        barrier = []

        for row, line in enumerate(pattern):
            for col, block in enumerate(line):
                if block == "#":
                    barrier.append(
                        pygame.Rect(
                            x + col * block_size,
                            450 + row * block_size,
                            block_size,
                            block_size
                        )
                    )

        barriers.append(barrier)

    # Bomb setup
    bomb = None
    alien_bomb = None

    # Alien movement setup
    alien_direction = 1

    # Game state setup
    game_over = False
    game_won = False

    # Explosion setup
    explosion_frame = 0
    explosion_rect = None
    explosion_timer = 0


#Explosion animation setup
explosion_images = []
for i in range(1,7):
    image = pygame.image.load(f"images/explosion_{i}.png")
    image = pygame.transform.scale(image, (40, 25))
    explosion_images.append(image)

#Player bombs setup
bombs_image = pygame.image.load("images/bombs.png")
bombs_image = pygame.transform.scale(bombs_image,(15,20))

#Game over setup
gameover_image = pygame.image.load("images/game_over.png")
gameover_image = pygame.transform.scale(gameover_image,(100,50))


# Alien movement setup
alien_speed = 1
alien_drop = 1


# Main game loop
running = True
reset_game()
while running:

    # Draw background
    screen.blit(background_image, (0, 0))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Restart game after Game Over / You Win
        elif event.type == pygame.KEYDOWN:
            if game_over or game_won:
                reset_game()
    # Game state
    if not game_over and not game_won:
        # Alien movement
        for alien in aliens:
            alien.move_ip(alien_direction * alien_speed, 0)
        # Change direction and move aliens down when they reach either side of the screen
        if any(alien.right >= screen.get_width() or alien.left <= 0 for alien in aliens):
            alien_direction *= -1

            for alien in aliens:
                alien.move_ip(0, alien_drop)

        # Player movement and shooting
        key_input = pygame.key.get_pressed()
        if key_input[pygame.K_RIGHT]:
            player.move_ip(5,0)
        elif key_input[pygame.K_LEFT]:
            player.move_ip(-5,0)
        elif key_input[pygame.K_SPACE] and bomb is None:
            bomb = pygame.Rect(player.centerx-7, player.top - 25, 15, 25)

        # Alien attack
        if alien_bomb is None and aliens:
            attacking_alien = random.choice(aliens)

            alien_bomb = pygame.Rect(
                attacking_alien.centerx - 7,
                attacking_alien.bottom,
                15,
                25
            )

        # Alien bomb movement
        if alien_bomb is not None:
            alien_bomb.move_ip(0, 1)

            if alien_bomb.top > screen.get_height():
                alien_bomb = None

        # Alien bomb collisions
        if alien_bomb is not None:

            alien_hit = False

            for barrier in barriers:
                for block in barrier:

                    if alien_bomb.colliderect(block):
                        explosion_rect = pygame.Rect(0, 0, 40, 25)
                        explosion_rect.center = block.center
                        explosion_frame = 0

                        barrier.remove(block)
                        alien_bomb = None
                        alien_hit = True
                        break

                if alien_hit:
                    break

            if alien_bomb is not None and alien_bomb.colliderect(player):
                explosion_rect = pygame.Rect(0, 0, 40, 25)
                explosion_rect.center = player.center
                explosion_frame = 0

                lives.pop()
                alien_bomb = None

        # Check collision with player's bomb
        if alien_bomb is not None and bomb is not None:
            if alien_bomb.colliderect(bomb):
                explosion_rect = pygame.Rect(0, 0, 40, 25)
                explosion_rect.center = alien_bomb.center
                explosion_frame = 0

                alien_bomb = None
                bomb = None

        # Player bomb movement
        if bomb is not None:
            bomb.move_ip(0, -2)

            # Remove bomb when it leaves the screen
            if bomb.bottom < 0:
                bomb = None

        # Player bomb collisions
        if bomb is not None:
            hit = False

            # Check collision with aliens
            for alien in aliens:
                if bomb.colliderect(alien):
                    explosion_rect = pygame.Rect(0, 0, 40, 25)
                    explosion_rect.center = alien.center
                    explosion_frame = 0
                    aliens.remove(alien)
                    bomb = None
                    hit = True
                    score += 100
                    break

            # Check barriers only if no alien was hit
            if not hit and bomb is not None:
                for barrier in barriers:
                    for block in barrier:
                        if bomb.colliderect(block):
                            explosion_rect = pygame.Rect(0, 0, block_size, block_size)
                            explosion_rect.center = block.center
                            explosion_frame = 0
                            barrier.remove(block)
                            bomb = None
                            hit = True
                            break
                    if hit:
                        break

        # Player / alien collision
        for alien in aliens:
            if alien.colliderect(player):
                game_over = True

        # Game Over / Win conditions
        if len(lives) == 0:
            game_over = True


        elif any(alien.bottom >= player.top for alien in aliens):
            game_over = True

        elif len(aliens) == 0:
            game_won = True


    # Explosion animation
    if explosion_rect is not None:
        screen.blit(explosion_images[explosion_frame], explosion_rect)
        explosion_timer += 1

        if explosion_timer >= 5:
            explosion_frame += 1
            explosion_timer = 0

        if explosion_frame >= len(explosion_images):
            explosion_rect = None
            explosion_frame = 0
    #Draw Lives
    for life in lives:
        screen.blit(heart_image, life)

    # Draw barriers
    for barrier in barriers:
        for block in barrier:
            pygame.draw.rect(screen, (0, 255, 0), block)

    #Draw bombs
    if bomb is not None:
        screen.blit(bombs_image, bomb)
    if alien_bomb is not None:
        screen.blit(bombs_image,alien_bomb)

    #Draw player
    screen.blit(player_image, player)

    #Draw aliens
    for alien in aliens:
        screen.blit(alien_image, alien)

    # Draw score
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (640, 15))

    #Draw Game Over screen
    if game_over:
        screen.blit(gameover_image, (350, 275))

    # Draw You Win message
    if game_won:
        message = font.render("You Win!", True, (255, 255, 255))
        message_rect = message.get_rect(center=(400, 300))
        screen.blit(message, message_rect)

    # Update display
    pygame.display.flip()

    # Limit game to 60 FPS
    clock.tick(60)  # limits FPS to 60


# Quit Pygame
pygame.quit()
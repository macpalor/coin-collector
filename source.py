import pygame
from random import random, randint

class CoinCollector:
    def __init__(self, display_width: int=640, display_height: int=480):
        """Initialize all values and start the main game loop."""

        pygame.init()
        self.load_images()

        self.display_width = display_width
        self.display_height = display_height
        self.display = pygame.display.set_mode((self.display_width, self.display_height))

        self.velocity_y = 1 # how many pixels objects move vertically per iteration
        self.new_game()

        self.font = pygame.font.SysFont("Arial", 24)
        pygame.display.set_caption("Coin collector")
        
        self.game_loop()

    def load_images(self):
        """Load the images used in the game to a dictionary."""

        images = ["robot", "coin", "monster"]
        self.images = {image:pygame.image.load(image + ".png") for image in images}

    def examine_events(self):
        """Get player keypresses and act accordingly."""

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.to_left = True
                if event.key == pygame.K_RIGHT:
                    self.to_right = True
                
                if event.key == pygame.K_F1:
                    self.new_game()
                if event.key == pygame.K_ESCAPE:
                    exit()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.to_left = False
                if event.key == pygame.K_RIGHT:
                    self.to_right = False

            if event.type == pygame.QUIT:
                exit()

    def draw_display(self):
        """Draw all objects and text to the screen."""

        self.display.fill((200, 200, 200))
        
        score = self.font.render(f"Score: {self.score}", True, (255, 0, 0))
        lives = self.font.render(f"Lives: {self.player_lives * '* '}", True, (255, 0, 0))
        
        self.display.blit(score, (self.display_width - 120, 40))
        self.display.blit(lives, (self.display_width - 120, 70))

        text = self.font.render("F1 = New game", True, (255, 0, 0))
        # text is placed horizontally such that its center is the first quarter of the screen
        self.display.blit(text, (self.display_width // 4 - text.get_width()/2, 10))

        text = self.font.render("Esc = Exit game", True, (255, 0, 0))
        # text is placed horizontally such that its center is the third quarter of the screen
        self.display.blit(text, (self.display_width // 4 * 3 - text.get_width()/2, 10))
        
        self.display.blit(self.images["robot"], (self.player_x, self.player_y))

        for (x, y) in self.coins:
            self.display.blit(self.images["coin"], (x, y))
        for (x, y) in self.monsters:
            self.display.blit(self.images["monster"], (x, y))

        # text is drawn in the middle of the screen inside a black box
        if self.game_over():
            text = self.font.render("Game over!", True, (255, 0, 0))
            text_x = self.display_width / 2 - text.get_width() / 2
            text_y = self.display_height / 2 - text.get_height() / 2
            pygame.draw.rect(self.display, (0, 0, 0), (text_x, text_y, text.get_width(), text.get_height()))
            self.display.blit(text, (text_x, text_y))
        
        pygame.display.flip()  

    def move_player(self):
        """Move the player controlled robot 2 pixels to the left or right. You cannot move
        past the screen."""

        if self.to_right and self.player_x + self.images["robot"].get_width() < self.display_width:
            self.player_x += 2
        if self.to_left and self.player_x > 0:
            self.player_x -= 2

    def move_objects(self, objects: list):
        """Moves an object vertically across the screen. There are two kinds of objects:
        coins and monsters. The player score is increased by 1 for every coin the player collects.
        The monsters try to prevent the player from collecting coins and if they catch the player,
        the player loses one life. In addition, if the player fails to catch a coin, the monsters
        grow in power and start to move faster."""

        is_coin = objects == self.coins 
        image = "coin" if is_coin else "monster"
        
        if objects != []:
            for i, (x, y) in enumerate(objects):
                # remove objects that are out of the screen to avoid filling memory 
                # and proceed to the next one
                if y - self.images[image].get_height() >= self.display_height:
                    if is_coin:
                        self.missed_coins += 1
                    objects.pop(i) # enumerate is used to get the index i
                    continue
                
                # collision is detected by forming rectangle objects and checking if they collide
                object_rect = self.images[image].get_rect(topleft=(x, y))
                robot_rect = self.images["robot"].get_rect(topleft = (self.player_x, self.player_y))

                if object_rect.colliderect(robot_rect):
                    if is_coin:
                        self.score += 1
                    else:
                        self.reset_player_position()
                        self.player_lives -= 1
                    objects.pop(i) # remove objects that the player hits
                else:
                    # coins have constant vertical velocity while the monsters' velocity can change
                    y += self.velocity_y if is_coin else self.velocity_y * 2 + self.missed_coins // 2
                    objects[i] = (x, y) # update position
   
    def generate_image(self, image_positions: list, image, prob: float=0.5):
        """Generate random position for an image with probability prob. The image starts falling
        down with random x coordinate from the top edge of the screen."""

        if random() <= prob:
            x = randint(0, self.display_width - image.get_width())
            y = -image.get_height()
            image_positions.append((x, y))

    def reset_player_position(self):
        """Resets player position to the left corner. This is done when the player starts a
        new game or loses a life."""

        self.player_x = 0
        self.player_y = self.display_height - self.images["robot"].get_height()        
        self.to_left = self.to_right = False

    def new_game(self):
        """Resets all variables to initial values."""

        self.reset_player_position()
        self.monsters = []
        self.coins = []

        self.score = 0
        self.player_lives = 3
        self.missed_coins = 0

    def game_over(self):
        """Game is over when the player loses all his/her lives."""

        return self.player_lives == 0

    def game_loop(self):
        """Main game loop."""

        clock = pygame.time.Clock()
        time = pygame.time.get_ticks()

        while True:
            self.examine_events()

            if not self.game_over(): # screen frozen if game is over
                # coins and monsters are randomly generated every 1000 ms (i.e. every second) with
                # certain probabilities
                if pygame.time.get_ticks() - time > 1000:
                    self.generate_image(self.coins, self.images["coin"], prob=0.25)
                    self.generate_image(self.monsters, self.images["monster"], prob=0.5)
                    time = pygame.time.get_ticks()

                self.move_player()
                self.move_objects(self.coins)
                self.move_objects(self.monsters)
            self.draw_display()
            clock.tick(60) # force 60 fps

if __name__ == "__main__":
    CoinCollector()

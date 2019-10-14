import pygame, sys, random, uuid
from pygame.locals import *
from pygame import gfxdraw

# we only set global to variables that will be asigned to new value 
# HELP

# Start/Pause: Space
#
# Show/Hide Radar: R
#
# Show/Hide Health: H
#
# Show/Hide Analytics: A
#
# Add Food: F
# Del Food: 
#
# Restart: Enter (Return)

rnd = random.randint

FOOD = []
FPS = 60

ANALYTICS = False
HEALTH = False
RADAR = False
RUN = False

pygame.init()
pygame.font.init()

GUI_SIZE = (1020, 650)
gx, gy = GUI_SIZE
DISPLAY = pygame.display.set_mode(GUI_SIZE, 0, 32)
DISPLAY.convert_alpha()

pygame.display.set_caption('Eco-System')

class Rabbit:
    def __init__(self, name=None):
        self.name = name
        self.x = rnd(0, gx)
        self.y = rnd(0, gy)
        self.age = 5
        self.color = (255, 255, 255)
        self.chosen_food = None
        self.counter = 0
        # End Destinations
        self.end = (rnd(0, gx), rnd(0, gy))
        # Radar
        self.scan_area = 25
        self.radar_color = (255, 0, 0)
        # Health
        self.death = False
        self.hunger = 100
        self.thrist = 100
        # Analytics
        self.eaten_food = 0
        self.life_timer = 0

    ##### Coordination Config ####

    def distance(self, v1, v2):
        x_dist = abs(v2[0] - v1[0])
        y_dist = abs(v2[1] - v1[1])
        radius = (x_dist**2 + y_dist**2)**0.5
        return int(radius)

    def random_position(self):
        self.end = (rnd(0, gx - 5), rnd(0, gy - 5))

    def xy(self):
        return (self.x, self.y)
    
    #### Status Config ####

    def draw_stats(self):
        # move x to the right
        x_pos = self.x - 20
        # move y up to rabbit
        y_pos = self.y - self.age - 5
        # start point of health bar
        start = (x_pos, y_pos)
        # get dynamic delta for hunger to draw
        x_hunger = int((self.hunger / 100) * 40)
        # draw main bar
        pygame.draw.line(DISPLAY, (255, 0, 0), start, (x_pos + 40, y_pos))
        # draw health bar
        pygame.draw.line(DISPLAY, (0, 255, 0), start, (x_pos + x_hunger, y_pos))

    def update_stats(self):
        if HEALTH:
            self.draw_stats()
        
        if RUN:
            self.counter += 1
            
            # Calculate life in seconds
            if not self.counter % FPS:
                self.life_timer += 1
                self.hunger -= 1

            '''
            # Feel hungry if 5 seconds passed without food
            if not self.counter % (FPS * 2):
                self.hunger -= 1
            '''
            
            # Die if no food found
            if self.hunger <= 0:
                self.death = True
    
    def draw_analytics(self):
        add_text(str(self.name), 10, self.x, self.y - self.age - 25)
        add_text(str(self.hunger), 10, self.x, self.y - self.age - 10)
        add_text(str(self.eaten_food), 10, self.x, self.y + self.age + 5)
        add_text(str(self.life_timer), 10, self.x, self.y + self.age + 15)


    def radar(self):
        if RADAR:
            pygame.gfxdraw.aacircle(DISPLAY, self.x, self.y, self.scan_area, self.radar_color)
            if self.chosen_food:
                pygame.draw.line(DISPLAY, self.radar_color, self.xy(), self.chosen_food)

    #### Instinct Config ####

    def search_for_food(self):
        if FOOD:
            for piece in FOOD:
                # if piece is inside radar area then go to it
                if self.distance(piece, self.xy()) <= self.scan_area:
                    # Eat only if hungry
                    if self.hunger < 90:
                        self.radar_color = (0, 255, 0)
                        self.chosen_food = piece
        
    def hunt(self, isfood=True):
        # Add more speed when more hunger
        # like making him nervous
        n = 0
        self.color = (255, 255, 255)

        # Key: Health
        # Val: [n, decrease in Greens in (R, G, B) of self.color]
        speed_states = {
            100:[0, 0],
            80:[1, 55],
            60:[2, 105],
            40:[3, 155],
            20:[4, 205]
            }
        
        for health in speed_states:
            if self.hunger < health:
                data = speed_states[health]
                n = data[0]
                self.color = (255, 255-data[1], 255)

        fx, fy = 0, 0
        # Random move when no food detected
        if not isfood:
            fx, fy = self.end
        else:
            # Handle Bot Movement
            fx, fy = self.chosen_food
        # (X) after (and) we add a case to prevent shaking effect
        if not fx + 3 > self.x > fx - 3:
            # food is left
            if self.x - fx > 1:
                self.x -= 1 + n
            # food is right
            else:
                self.x += 1 + n
        # (Y) after (and) we add a case to prevent shaking effect
        if not fy + 3 > self.y > fy - 3:
            # food is up
            if self.y - fy > 0:
                self.y -= 1 + n 
            # food is down
            else:
                self.y += 1 + n
        # When Eaten a piece of food
        if fx+3 > self.x > fx-3 and fy+3 >= self.y >= fy-3:
            # if we catch food then process this
            if isfood:
                # remove the piece of food
                FOOD.pop(FOOD.index(self.chosen_food))
                self.chosen_food = None
                # reset piece coordinates
                fx, fy = None, None
                # get new position to target
                self.random_position()
                # more health
                self.hunger = 100 if self.hunger + 5 > 100 else self.hunger + 5
                self.eaten_food += 1
                # grow the Fish BOT
                if self.age < 15:
                    self.age += 1
                    # update scan area for radar
                    self.scan_area = self.age * 5
            # if not then process a random move
            else:
                self.random_position()

    def live(self):
        global DISPLAY, FOOD
        if not self.death:
            
            if RUN:
                # Search for nearby food
                self.search_for_food()

                if self.chosen_food:
                    # in case any fish has eaten this piece
                    if self.chosen_food in FOOD:
                        self.hunt()

                    # do a random move and reset detection
                    else:
                        self.hunt(False)
                        self.chosen_food = None

                # random move if no food
                else:
                    self.radar_color = (255, 0, 0)
                    self.hunt(False)
            
            # Draw Radar
            self.radar()

            # Update states of Rabbit
            self.update_stats()
        else:
            self.color = (255, 0, 0)
        # Draw Analytics
        if ANALYTICS:
            self.draw_analytics()
        pygame.draw.circle(DISPLAY, self.color, self.xy(), self.age, 0)

def add_text(text, size, x, y):
    myfont = pygame.font.SysFont('timesnewroman', size)
    typed_text = myfont.render(text, False, (255, 255, 255))
    rect_text = typed_text.get_rect()
    rect_text.center = (x, y)
    DISPLAY.blit(typed_text, rect_text)

def main():
    global RADAR, FOOD, HEALTH, RUN, ANALYTICS
    count = 0
    YELLOW = (0, 255, 255)
    BLACK = (0, 0, 0)


    # Create a Group of Rabbits (n)
    Herd = [Rabbit() for _ in range(10)]
    for i in Herd:
        # Generate Random Names
        i.name = str(uuid.uuid4())[:8]
        #i.color = (rnd(100,255), rnd(100,255), rnd(100,255))
    
    while True:
        DISPLAY.fill(BLACK)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            
            # add new food when clicked
            if event.type == MOUSEBUTTONUP:
                FOOD.append(event.pos)

            if event.type == KEYDOWN:
                # RESTART
                if event.key == K_RETURN:
                    Herd = [Rabbit() for _ in range(10)]
                    for i in Herd:
                        i.name = str(uuid.uuid4())[:8]
                    RUN = False
                    FOOD = []

                # Show or Hide Food
                if event.key == K_f:
                    for _ in range(10):
                        FOOD.append((rnd(0, gx - 3), rnd(0, gy - 3)))
                if event.key == K_g:
                    FOOD = []
                
                # Start or Pause
                if event.key == K_SPACE:
                    if RUN:
                        RUN = False
                    else:
                        RUN = True
                
                # Show or Hide Radar
                if event.key == K_r:
                    if RADAR:
                        RADAR = False
                    else:
                        RADAR = True

                # Show or Hide Health
                if event.key == K_h:
                    if HEALTH:
                        HEALTH = False
                    else:
                        HEALTH = True
                
                # Show or Hide Health
                if event.key == K_a:
                    if ANALYTICS:
                        ANALYTICS = False
                    else:
                        ANALYTICS = True
        
        # Random Food
        if RUN:
            count += 1
            if not count % FPS:
                FOOD.append((rnd(0, gx - 3), rnd(0, gy - 3)))

        # Redraw food if found
        for pix in FOOD:
            pygame.draw.circle(DISPLAY, YELLOW, pix, 2, 0)
        
        # Draw Rabbits
        for one in Herd:
            one.live()

        pygame.display.update()
        pygame.time.Clock().tick(FPS)


if __name__ == "__main__":
    main()

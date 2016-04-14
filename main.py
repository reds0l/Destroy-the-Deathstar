import pygame
import math


class Laser(pygame.sprite.Sprite):
    def __init__(self, gs=None, ship=None):
        pygame.sprite.Sprite.__init__(self)

        self.gs = gs
        self.image = pygame.image.load('images/laser.png')
        self.scale_image(2)
        self.orig_image = self.image
        self.rect = self.image.get_rect()
        
        self.angle = ship.angle
        
        self.rect.centerx = ship.rect.centerx
        self.rect.centery = ship.rect.centery 

        # rotate to ship angle
        self.image = pygame.transform.rotate(self.orig_image,self.angle)
        self.rect = self.image.get_rect(center=(self.rect.center))

    def scale_image(self, amnt):
        self.size = self.image.get_size()
        self.image = pygame.transform.scale(self.image, (int(self.size[0]/amnt), int(self.size[1]/amnt)))

    def animate(self):
        mv = 10 
        x = mv * math.cos(math.radians(self.angle + 90))
        y = mv * math.sin(math.radians(self.angle - 90))
        self.rect = self.rect.move(x,y)

    def detect_collision(self):
        if self.rect.centerx > 640 or self.rect.centerx < 0 or self.rect.centery > 480 or self.rect.centery < 0:
            return 1

        if gs.deathstar.exploding_flag == 0:
            ds_center = gs.deathstar.rect.center
            ds_radius = gs.deathstar.rect.height

            if self.rect.colliderect(gs.deathstar.rect):
                gs.deathstar.got_hit()
                return 1
            else:
                return 0


class Deathstar(pygame.sprite.Sprite):
    def __init__(self, gs=None):
        pygame.sprite.Sprite.__init__(self)

        self.gs = gs
        self.image = pygame.image.load('images/deathstar.png')
        self.scale_image(0.7)
        self.orig_image = self.image
        self.rect = self.image.get_rect()

        self.rect.centerx = 100
        self.rect.centery = 100

        # Game stats
        self.health = 200
        self.exploding_flag = 0
        self.exploding_frame = 0

    def scale_image(self, amnt):
        self.size = self.image.get_size()
        self.image = pygame.transform.scale(self.image, (int(self.size[0]/amnt), int(self.size[1]/amnt)))

    def got_hit(self):
        if self.health > 0:
            self.health -= 1

        if self.health == 80:
            self.image = pygame.image.load('images/dead_deathstar.png')
            self.scale_image(0.7)
            self.orig_image = self.image
            self.rect = self.image.get_rect()

            self.rect.centerx = 100
            self.rect.centery = 100

        if self.health == 0:
            self.exploding_flag = 1
            self.explode_audio()
            self.health = -1

    def tick(self):
        if self.exploding_flag == 1 and self.exploding_frame < 16:
            if self.exploding_frame < 10:
                self.image = pygame.image.load('explosion/frames00' + str(self.exploding_frame) + 'a.png')
            else:
                self.image = pygame.image.load('explosion/frames0' + str(self.exploding_frame) + 'a.png')
            #self.scale_image(0.7)
            self.orig_image = self.image
            self.rect = self.image.get_rect()
            self.rect.centerx = 100
            self.rect.centery = 100
            self.exploding_frame += 1

    def explode_audio(self):
        print "play explode audio"
        mixer = pygame.mixer.init()
        explode_sound = mixer.Sound('expolde.wav')
        explode_sound.play()
        

class Player(pygame.sprite.Sprite):
    def __init__(self, gs=None):
        pygame.sprite.Sprite.__init__(self)

        self.gs = gs
        self.image = pygame.image.load('images/spaceship.png')
        self.scale_image(5)
        self.orig_image = self.image
        self.rect = self.image.get_rect()

        self.rect.centerx = 640/2
        self.rect.centery = 480 - 60
        self.angle = 0

        # game stats
        self.laser_list = []

    def scale_image(self, amnt):
        self.size = self.image.get_size()
        self.image = pygame.transform.scale(self.image,
                (int(self.size[0]/amnt), int(self.size[1]/amnt)))

    def tick(self):
        self.rotate()
        self.animate_lasers()

    def rotate(self):
        mx, my = pygame.mouse.get_pos()
        self.angle = 270 - math.atan2(my-self.rect.centery, mx-self.rect.centerx)*180/math.pi
        self.image = pygame.transform.rotate(self.orig_image,self.angle)
        self.rect = self.image.get_rect(center=(self.rect.center))

    def handle_key_press(self):
        # get key and mouse click
        key = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()
        # movement amount
        mv = 5

        # handles movement of ship
        if key[pygame.K_w]:
            self.rect = self.rect.move(0, -mv)
        elif key[pygame.K_s]:
            self.rect = self.rect.move(0, mv)
        if key[pygame.K_a]:
            self.rect = self.rect.move(-mv, 0)
        elif key[pygame.K_d]:
            self.rect = self.rect.move(mv, 0)

        # handles laser shooting
        if mouse[0]:
            print "Left Click!"
            self.fire_laser()

    def fire_laser(self):
        print "firing laser"
        laser = Laser(gs,self)
        self.laser_list.append(laser)

    def animate_lasers(self):
        rmv_lsr_list =[]
        if len(self.laser_list) > 0:
            for lsr in self.laser_list:
                lsr.animate()
                if lsr.detect_collision():
                    rmv_lsr_list.append(lsr)
                gs.screen.blit(lsr.image, lsr.rect)

            # laser clean up
            for lsr in rmv_lsr_list:
                self.laser_list.remove(lsr)
                rmv_lsr_list.remove(lsr)


class GameSpace:
    def main(self):
        # step 1
        pygame.init()

        self.size = self.width, self.height = 640, 480
        self.black = 0, 0, 0

        self.screen = pygame.display.set_mode(self.size)
        # step 2
        self.clock = pygame.time.Clock()

        self.player = Player(self)
        self.deathstar = Deathstar(self)

        running = True
        while running:
            event = pygame.event.poll()
            if event.type == pygame.QUIT:
                running = False

            self.clock.tick(60)

            self.player.handle_key_press()

            self.screen.fill(self.black)

            # put here because player tick creates laser
            self.player.tick()
            self.deathstar.tick()
            self.screen.blit(self.player.image, self.player.rect)
            self.screen.blit(self.deathstar.image, self.deathstar.rect)

            pygame.display.flip()

if __name__ == '__main__':
    gs = GameSpace()
    gs.main()

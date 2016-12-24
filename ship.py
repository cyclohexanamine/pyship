import sys, time
from math import pi
import pygame, pygame.gfxdraw
from objects import armour, ship, projectile
import graphics


graphics.scale = 3. # camera scale
speed = 0.04 # simulation speed
screen_size = 1000, 700
fps_cap = 30



### Logic ###
def ship_template():
    l,w = 100.,30.
    s = ship( ([(-l/6,-w/2),(l/2,-w/4),(l/2,w/4),(-l/6,w/2),(-l/2,w/4),(-l/2,-w/4)],[(1,1)]*6) )
    s.children.append(armour((10,3,1),ia=pi/2))
    return s

## Initialise objects
def initstate():
    p = projectile((0.5,1), im=3000, ip=(100,-0), iv=(-4000, 0))
    s = ship_template()
    s.a = pi/7
    return [s, p]

def main():
    ## Globals
    objects = []
    keys = [False]*500 # keys that are down
    black = 0, 0, 0
    white = 255, 255, 255

    ## Init
    pygame.init()
    screen = pygame.display.set_mode(screen_size)
    screen.fill(white)
    font_mono = pygame.font.SysFont("monospace", 15)
    objects = initstate()


    ## Main loop
    last_frame = time.clock()
    while 1:

        ## Timing
        this_frame = time.clock()
        frame_time = this_frame - last_frame
        if fps_cap:
            time.sleep(max(1./float(fps_cap) - frame_time, 0))
        previous_frame = last_frame
        last_frame = time.clock()
        delta = last_frame - previous_frame

        ## Events & controls
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            elif event.type == pygame.KEYDOWN: keys[event.key] = True
            elif event.type == pygame.KEYUP: keys[event.key] = False

            if event.type==pygame.KEYDOWN and event.key == pygame.K_F5:
                # reset world
                screen.fill(black)
                objects = initstate()

        ## Physics
        dt = delta*speed
        for obj in objects:
            obj.update(dt, objects)

        ## Graphics
        screen.fill(black)
        for obj in objects:
            obj.draw(screen)

        fps_text = "%.1f  %.1f" % (1./delta, 1./frame_time) if delta and frame_time else "NA"
        graphics.show_text(screen, font_mono, (0, 0), fps_text, white)

        pygame.display.flip()


main()

#### Graphics ####
import pygame.gfxdraw
from geom import dims, box, addc, rotc
scale = 1.

## Transform a vector from game space into screen space
def to_screen(c, screen_size):
    x,y = c
    screen_w, screen_h = screen_size
    screen_x = screen_w//2 + int(x*scale)
    screen_y = screen_h//2 - int(y*scale)
    return screen_x, screen_y

## Is the screen coordinate c not off the screen by a margin?
def on_screen_s(c, screen_size, margin=0):
    x,y = c
    screen_w, screen_h = screen_size
    return -margin <= x and x <= screen_w+margin and -margin <= y and y <= screen_h+margin

## For the draw_ functions below, points and distances are given in game space ##
def draw_poly(surf, colour, points):
    screen_size = surf.get_size()
    pointlist = [to_screen(point, screen_size) for point in points]
    dx,dy = dims(box(pointlist))
    if not on_screen_s(pointlist[0], screen_size, max(dx,dy)): return
    pygame.gfxdraw.filled_polygon(surf, pointlist, colour)

def draw_circle(surf, colour, pos, r):
    screen_size = surf.get_size()
    px, py = to_screen(pos, screen_size)
    if not on_screen_s((px,py), screen_size, r): return
    pygame.gfxdraw.filled_circle(surf, px, py, int(r*scale), colour)

## Draw a triangle with _screen_ length l and width w, at _world_ position pos
##  and angle a; l will be along a.
def show_triangle(surf, colour, pos, l, w, a):
    screen_size = surf.get_size()
    vl = [(2./3.*l,0),(-1./3.*l,w/2.),(-1./3.*l,-w/2.)]
    pointlist = [addc(to_screen(pos, screen_size),rotc(v,a)) for v in vl]
    pygame.gfxdraw.filled_polygon(surf, pointlist, colour)

def show_text(surf, font, pos, text, colour):
    label = font.render(text, 1, colour)
    surf.blit(label, pos)
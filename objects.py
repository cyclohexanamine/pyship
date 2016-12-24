#### Objects ####
from math import sin, sqrt, fabs
from geom import ptoc, ctop, addc, subc, mulc, rotc, lenc, awrap, box, boxb, dims, seg_seg_test, box_seg_test, sortbydist
from graphics import draw_poly, draw_circle, show_triangle, scale


### Generic physics object
class object:

    def __init__(self, ip=(0.,0.), iv=(0.,0.), im=1., ia=0., iav=0., imi=1.):
        ## All of these vectors are Cartesian
        self.p = ip # position
        self.v = iv # velocity
        self.m = im # mass
        self.a = ia # angle
        self.av = iav # angular velocity
        self.mi = imi # moment of inertia

        ## Any children have a position and angular orientation relative to the parent.
        ## In many functions below, p and a are the absolute position and orientation of the parent.
        self.children = []

    ## Calculates a new absolute position given the parent's absolute position p,a
    def relp(self, p, a):
        return addc(p, rotc(self.p, a)), a+self.a

    ## Update the physics object given a time step dt
    def update(self, dt, objects):
        self.p = addc(self.p, mulc(self.v, dt))
        self.a += self.av * dt

    ## Recursive bounding box
    def box(self, p=(0.,0.), a=0.):
        np,na = self.relp(p,a)
        boxes = [child.box(np, na) for child in self.children]
        return boxb(boxes)

    ## Intersect self with line segment recursively, returning all intersections.
    ##   Intersection results will have the form (point, object, (p,a))
    def intersect_segment(self, s, p=(0.,0.), a=0.):
        np,na = self.relp(p,a)
        return sum([child.intersect_segment(s, np, na) for child in self.children], [])

    ## Render the object to the screen
    def draw(self, surf, p=(0.,0.), a=0.):
        np,na = self.relp(p,a)
        for child in self.children:
            child.draw(surf, np, na)



### A plate of armour
class armour(object):

    def __init__(self, attrs, *args, **kwargs):
        object.__init__(self, *args, **kwargs)
        ## length, thickness, density - its length will be horizontal at a=0
        self.l, self.t, self.d = attrs
        self.m = self.l * self.t * self.d * 2.e3
        self.colour = (0, 0, 255)

    def box(self, p=(0.,0.), a=0.):
        cbox = object.box(self, p, a)
        abox = box(self.points(p, a))
        return boxb([cbox, abox])

    ## The line segment along the centre length of the plate
    def segment(self, p=(0.,0.), a=0.):
        np,na = self.relp(p,a)
        v = rotc((self.l*0.5,0), na)
        return (addc(np,v), subc(np,v))

    def intersect_segment(self, s, p=(0.,0.), a=0.):
        if box_seg_test(self.box(p,a), s):
            ip = seg_seg_test(s, self.segment(p, a))
            i1 = [(ip, self, (p, a))]
        else:
            i1 = []
        i2 = object.intersect_segment(self, s, p, a)
        return i1 + i2

    ## The points of the bounding polygon of the plate, including its thickness
    def points(self, p=(0.,0.), a=0.):
        np,na = self.relp(p,a)
        v1, v2 = (self.l*0.5,self.t*0.5),(self.l*0.5,-self.t*0.5)
        [v1,v2] = [rotc(v,na) for v in [v1,v2]]
        return [addc(np,v1), addc(np,v2), subc(np,v1), subc(np,v2)]

    def draw(self, surf, p=(0.,0.), a=0.):
        object.draw(self, surf, p, a)
        draw_poly(surf, self.colour, self.points(p, a))



### Ship: polygon with each side being a piece of armour
## The attributes here are ( list of points of polygon, list of (thickness, density) for each side )
class ship(object):
    def __init__(self, attrs, *args, **kwargs):
        object.__init__(self, *args, **kwargs)
        self.colour = (0,0,255,100)
        self.pointlist = attrs[0]
        for ii in range(len(attrs[0])):
            p1, p2 = attrs[0][ii], attrs[0][(ii+1)%len(attrs[0])]
            t, d = attrs[1][ii]
            l,a = ctop(subc(p2,p1))
            p = mulc(addc(p1,p2), 0.5)
            p = mulc(p, (lenc(p)-t*0.5)/lenc(p))
            side = armour((l, t, d), ip=p, ia=a)
            self.children.append(side)

    def points(self, p=(0.,0.), a=0.):
        np,na = self.relp(p,a)
        return [addc(np,rotc(v,na)) for v in self.pointlist]

    def draw(self, surf, p=(0.,0.), a=0.):
        ## If the ship is smaller on the screen than some minimum dimension MIN_DIM, show an icon. Otherwise render it fully.
        MIN_DIM = 5.
        dx,dy = dims(self.box())
        if min(dx,dy)*scale < MIN_DIM:
            if dx > dy: l,w = dx/dy*MIN_DIM, MIN_DIM
            else: l,w = MIN_DIM, dy/dx*MIN_DIM
            show_triangle(surf, self.colour[:3], self.p, l, w, self.a + a)
        else:
            object.draw(self, surf, p, a)
            draw_poly(surf, self.colour, self.points(p, a))



### A fast-moving point projectile, which is collided differently to slow objects
class projectile(object):

    def __init__(self, attrs, *args, **kwargs):
        object.__init__(self, *args, **kwargs)
        self.d, self.k = attrs
        self.colour = (255, 255, 0, 255)


    ## Update physically, including all collisions with slow objects
    def update(self, dt, objects):
        ## Recursive, to allow multiple collisions in one frame.
        ## Given a segment s to travel this frame, collide it with all objects.
        ## If the projectile changes direction, it will be called again with the new direction and remaining distance to travel
        def update_seg(self, s, objects):
            ## We collide the nearest first, and abandon subsequent collisions if the direction changes.
            intersections = sum([object.intersect_segment(s) for object in objects if not isinstance(object, projectile)], [])
            intersections = sortbydist(s[0], intersections, key=lambda i:i[0])

            for i in intersections:
                ## r1 is the distance to travel this frame and r2 the distance already travelled.
                ## the angles a1 and aa are used to calculate the incident angle
                ## of the projectile
                r1,a1 = ctop(subc(s[1], s[0]))
                r2 = lenc(subc(i[0], s[0]))
                r3 = lenc(self.v)
                aa = i[1].a + i[2][1]

                ## Calculate the shell's potential armour penetration
                pen = lenc(self.v) * sqrt(self.m) * self.k / 7.6e4 / sqrt(self.d)
                ## And the effective thickness
                sina = fabs(sin(aa - a1))
                dep = i[1].t * i[1].d / sina if sina > 1e-3 else i[1].l * i[1].d

                if pen > dep:
                    # Projectile has penetrated
                    i[1].colour = (255, 0, 0)
                    ## Bleed speed
                    self.v = mulc(self.v, (pen-dep)/pen)
                    continue

                ## Projectile will change direction
                i[1].colour = (0, 255, 0)
                ## Here we calculate the new velocity angle anew as a reflection off the face of the armour plate
                anew = 2.*aa - a1 - (180 if awrap(a1-aa)>180 else 0)
                vnew = ptoc((r3, anew))
                self.v = mulc(vnew, 0.5)
                ## We take the starting point as the collision point, with a small fraction of the new velocity added to take it away from the intersection.
                ## The end point is the start point plus the distance left to travel this frame, in the direction of the new velocity.
                snew = (addc(i[0], mulc(vnew, 0.001*dt)), addc(i[0], ptoc((r1-r2, anew))))
                update_seg(self, snew, objects)
                break
            else:
                ## Projectile has not changed direction during this call
                self.p = s[1]

        np = addc(self.p, mulc(self.v, dt))
        s = (self.p, np)
        update_seg(self, s, objects)


    def draw(self, surf, p=(0.,0.), a=0.):
        np,na = self.relp(p,a)
        object.draw(self, surf, p, a)
        draw_circle(surf, self.colour, np, self.d/2.)
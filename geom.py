#### Spatial and vector geometry library ####
from math import cos, sin, atan2, pi, sqrt, fabs, copysign
import algos



### Vector maths ###
## Polar to Cartesian vector
def ptoc(p):
    r, a = p
    x = r*cos(a)
    y = r*sin(a)
    return (x, y)

## Cartesian to polar vector
def ctop(c):
    x, y = c
    r = sqrt(x*x + y*y)
    a = atan2(y, x)
    return (r, a)

## Add two Cartesian vectors
def addc(c1, c2):
    (x1, y1), (x2, y2) = c1, c2
    return (x1 + x2, y1 + y2)

## Subtract two Cartesian vectors
def subc(c1, c2):
    (x1, y1), (x2, y2) = c1, c2
    return (x1 - x2, y1 - y2)

## Multiply a Cartesian vector by a scalar
def mulc(c, scalar):
    x, y = c
    return (x*scalar, y*scalar)

## Rotate the Cartesian vector c anticlockwise by ang radians
def rotc(c, ang):
    r, a = ctop(c)
    return ptoc((r,a+ang))

def lenc(c):
    x, y = c
    return sqrt(x*x + y*y)

## Wrap an angle a to the range 0,2pi
def awrap(a):
    while a < 0: a += 2*pi
    while a > 2*pi: a -= 2*pi
    return a

## Sign function
def sgn(x): return copysign(1.,x)

## Get all distinct pairs of distinct elements in a list l
def pairs(l):
    res = []
    for ii in range(len(l)):
        for jj in range(ii+1, len(l)):
            res.append((l[ii],l[jj]))
    return res



### Geometry ###
## Bounding box for a list of points
def box(pl):
    if not pl: return None
    (minx,miny),(maxx, maxy) = pl[0],pl[0]
    for (x,y) in pl[1:]:
        (minx,miny), (maxx,maxy) = (min(x,minx),min(y,miny)), (max(x,maxx),max(y,maxy))
    return ((minx,miny),(maxx, maxy))

## Bounding box for a list of bounding boxes
def boxb(ll):
    pl = []
    for i in ll:
        if not i: continue
        pl.append(i[0])
        pl.append(i[1])
    return box(pl)

## Absolute width and height of a box
def dims(b):
    b1,b2 = b
    dx,dy = subc(b1,b2)
    return fabs(dx),fabs(dy)

## Is point p in the bounding box b?
def in_box(p, b):
    x,y = p
    (x1,y1), (x2,y2) = b
    return x1 < x and x < x2 and y1 < y and y < y2

## Is point p on the segment s (assuming it's on the line that s is on)?
def on_seg(p, s):
    (px, py), ((xmin, ymin),(xmax,ymax)) = p, box(s)
    return (xmin < px and px < xmax) or (ymin < py and py < ymax)

## Find the intersection point between s1 and s2, or None
def seg_seg_test(s1, s2):
    ((x11,y11), (x12,y12)),  ((x21,y21), (x22,y22))  = s1,  s2
    A1, B1 = y12 - y11, x11 - x12
    C1 = A1 * x11 + B1 * y11
    A2, B2 = y22 - y21, x21 - x22
    C2 = A2 * x21 + B2 * y21

    det = A1 * B2 - A2 * B1
    if det == 0: return None
    p = ((B2*C1 - B1*C2)/det, (A1*C2 - A2*C1)/det)
    if not on_seg(p, s1): return None
    return p

## Clip s to the box, or else None if it's outside
def box_seg_test(box, s):
    ((xmin, ymin), (xmax, ymax)), ((x1, y1), (x2, y2)) = box, s
    clip = algos.cohensutherland(xmin, ymax, xmax, ymin, x1, y1, x2, y2)
    if clip == (None, None, None, None): return None
    else: return clip

## Sort items in l by their distance from the point p, where key gives the items' point given an item
def sortbydist(p, l, key=lambda x:x):
    l = [i for i in l if i and key(i)]
    if not l: return []
    def sortkey(i):
        (ox,oy), (ix,iy) = p, key(i)
        return fabs(ix-ox) + fabs(iy-oy)
    return sorted(l, key=sortkey)

## As in sortbydist, but returns the closest
def closest(p, l, key=lambda x:x):
    sl = sortbydist(p,l,key)
    return sl[0] if sl else None

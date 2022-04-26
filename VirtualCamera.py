from asyncio.windows_events import NULL
from datetime import datetime
import pyglet
from pyglet import shapes
from dataclasses import dataclass
import numpy as np
import math

refreshRate = 60  # Hz
tx, ty, tz, rx, ry, rz = 0, 0, 0, 0, 0, 0  # translacje i obroty
f = 300  # ogniskowa
min_f = 50  # minimalna wartosc ogniskowej
flaga = 0  # flaga do klawiszy
width = 900  # szerokosc okna
height = 500  # wysokosc okna
line_width = 1  # szerokosc pojedynczej linii
disappearance = 0  # prog zanikania krawedzi
window = pyglet.window.Window(width, height)  # szerokosc, wysokosc
batch = pyglet.graphics.Batch()
point_list = []  # lista punktow 3d
shape = []  # ksztalty
lines = []
lines2d = []


@dataclass
class Point:
    x: float
    y: float
    z: float


@dataclass
class Point2d:
    x: float
    y: float


@dataclass
class Line:
    p1: Point
    p2: Point


@dataclass
class Line2d:
    p1: Point2d
    p2: Point2d


point_list.append(Point(0.0, 0.0, 0.0))
point_list.append(Point(100, 0.0, 0.0))
point_list.append(Point(100, 100, 0.0))
point_list.append(Point(0.0, 100, 0.0))
point_list.append(Point(0.0, 0.0, 100))
point_list.append(Point(100, 0.0, 100))
point_list.append(Point(100, 100, 100))
point_list.append(Point(0.0, 100, 100))

for i in range(len(point_list)):
    x = point_list[i].x
    y = point_list[i].y
    z = point_list[i].z
    point_list.append(Point(x + 150.0, y, z))

for i in range(len(point_list)):
    x = point_list[i].x
    y = point_list[i].y
    z = point_list[i].z
    point_list.append(Point(x, y + 150.0, z))

for i in range(len(point_list)):
    x = point_list[i].x
    y = point_list[i].y
    z = point_list[i].z
    point_list.append(Point(x, y, z + 150.0))

for n in range(0, 8):
    for i in range(4):
        if i == 3:
            lines.append(Line(Point(point_list[i + 8*n].x, point_list[i + 8*n].y, point_list[i + 8*n].z),
                              Point(point_list[0 + 8*n].x, point_list[0 + 8*n].y, point_list[0 + 8*n].z)))
            lines.append(Line(Point(point_list[i + 8*n+4].x, point_list[i + 8*n+4].y, point_list[i + 8*n+4].z),
                              Point(point_list[4 + 8*n].x, point_list[4 + 8*n].y, point_list[4 + 8*n].z)))
        else:
            lines.append(Line(Point(point_list[i + 8*n].x, point_list[i + 8*n].y, point_list[i + 8*n].z),
                              Point(point_list[i + 8*n + 1].x, point_list[i + 8*n + 1].y, point_list[i + 8*n + 1].z)))
            lines.append(Line(Point(point_list[i + 8*n+4].x, point_list[i + 8*n+4].y, point_list[i + 8*n+4].z),
                              Point(point_list[i + 8*n + 5].x, point_list[i + 8*n + 5].y, point_list[i + 8*n + 5].z)))
        lines.append(Line(Point(point_list[i + 8*n].x, point_list[i + 8*n].y, point_list[i + 8*n].z),
                          Point(point_list[i + 8*n + 4].x, point_list[i + 8*n + 4].y, point_list[i + 8*n + 4].z)))


def calculateRX(fi):
    RX = [[1, 0, 0],
          [0, math.cos(math.radians(fi)), -math.sin(math.radians(fi))],
          [0, math.sin(math.radians(fi)), math.cos(math.radians(fi))]]
    return RX


def rotateMatrixX(lines, RX):
    lines = multiplyLines(lines, RX)
    return lines


def calculateRY(fi):
    RY = [[math.cos(math.radians(fi)), 0, math.sin(math.radians(fi))],
          [0, 1, 0],
          [-math.sin(math.radians(fi)), 0, math.cos(math.radians(fi))]]
    return RY


def rotateMatrixY(lines, RY):
    lines = multiplyLines(lines, RY)
    return lines


def calculateRZ(fi):
    RZ = [[math.cos(math.radians(fi)), -math.sin(math.radians(fi)), 0],
          [math.sin(math.radians(fi)), math.cos(math.radians(fi)), 0],
          [0, 0, 1]]
    return RZ


def rotateMatrixZ(lines, RZ):
    lines = multiplyLines(lines, RZ)
    return lines


def projection(lines, f):
    for i in range(len(lines)):
        two_points = []
        pkt1 = lines[i].p1
        pkt2 = lines[i].p2
        if pkt1.z < disappearance or pkt2.z < disappearance:
            lines[i] = NULL
            continue
        two_points.append(pkt1)
        two_points.append(pkt2)
        for j, point in enumerate(two_points):
            if point.z == 0.0:
                point.z = 0.00001
            k = f / point.z
            x = k * point.x + (width / 2)
            y = (height / 2) - k * point.y
            two_points[j] = Point2d(x, y)
        lines[i] = Line2d(two_points[0], two_points[1])
    return lines


def multiplyPoint(point, Matrix):
    V = [[point.x],
         [point.y],
         [point.z]]
    M = np.matmul(Matrix, V)
    point = Point(M[0][0], M[1][0], M[2][0])
    return point


def multiplyLines(lines, Matrix):
    for i in range(len(lines)):
        pkt1 = multiplyPoint(lines[i].p1, Matrix)
        pkt2 = multiplyPoint(lines[i].p2, Matrix)
        lines[i] = Line(pkt1, pkt2)
    return lines


def translationX(lines, value):
    for i in range(len(lines)):
        pkt1 = lines[i].p1
        pkt2 = lines[i].p2
        lines[i] = Line(Point(pkt1.x + value, pkt1.y, pkt1.z),
                        Point(pkt2.x + value, pkt2.y, pkt2.z))
    return lines


def translationY(lines, value):
    for i in range(len(lines)):
        pkt1 = lines[i].p1
        pkt2 = lines[i].p2
        lines[i] = Line(Point(pkt1.x, pkt1.y + value, pkt1.z),
                        Point(pkt2.x, pkt2.y + value, pkt2.z))
    return lines


def translationZ(lines, value):
    for i in range(len(lines)):
        pkt1 = lines[i].p1
        pkt2 = lines[i].p2
        lines[i] = Line(Point(pkt1.x, pkt1.y, pkt1.z + value),
                        Point(pkt2.x, pkt2.y, pkt2.z + value))
    return lines


@window.event
def on_key_press(key, modifiers):
    global flaga
    if key == pyglet.window.key.A:
        flaga = 1
    if key == pyglet.window.key.D:
        flaga = 2
    if key == pyglet.window.key.R:
        flaga = 3
    if key == pyglet.window.key.F:
        flaga = 4
    if key == pyglet.window.key.S:
        flaga = 5
    if key == pyglet.window.key.W:
        flaga = 6
    if key == pyglet.window.key.DOWN:
        flaga = 7
    if key == pyglet.window.key.UP:
        flaga = 8
    if key == pyglet.window.key.LEFT:
        flaga = 9
    if key == pyglet.window.key.RIGHT:
        flaga = 10
    if key == pyglet.window.key.Q:
        flaga = 11
    if key == pyglet.window.key.E:
        flaga = 12
    if key == pyglet.window.key.NUM_ADD:
        flaga = 13
    if key == pyglet.window.key.NUM_SUBTRACT:
        flaga = 14
    if key == pyglet.window.key.P:
        now = datetime.now()
        dt_string = now.strftime("%d-%m-%Y %H_%M_%S")
        pyglet.image.get_buffer_manager().get_color_buffer().save(
            "Desktop/scr_" + dt_string + ".png")


@window.event
def on_key_release(key, modifiers):
    global flaga
    flaga = 0


lines_list = []
lines_list = lines.copy()
RXP = calculateRX(1)
RXM = calculateRX(-1)
RYP = calculateRY(1)
RYM = calculateRY(-1)
RZP = calculateRZ(1)
RZM = calculateRZ(-1)


def update(dt):
    global flaga
    global tx, ty, tz, rx, ry, rz, f
    tx, ty, tz, rx, ry, rz = 0, 0, 0, 0, 0, 0

    if flaga == 1:
        tx = 5
    elif flaga == 2:
        tx = -5
    elif flaga == 3:
        ty = 5
    elif flaga == 4:
        ty = -5
    elif flaga == 5:
        tz = 2
    elif flaga == 6:
        tz = -2
    elif flaga == 7:
        rotateMatrixX(lines_list, RXP)
    elif flaga == 8:
        rotateMatrixX(lines_list, RXM)
    elif flaga == 9:
        rotateMatrixY(lines_list, RYP)
    elif flaga == 10:
        rotateMatrixY(lines_list, RYM)
    elif flaga == 11:
        rotateMatrixZ(lines_list, RZP)
    elif flaga == 12:
        rotateMatrixZ(lines_list, RZM)
    elif flaga == 13:
        f = f + 5
    elif flaga == 14:
        f = f - 5
        if f < 50:
            f = min_f

    translationX(lines_list, tx)
    translationY(lines_list, ty)
    translationZ(lines_list, tz)

    lines2d = []
    lines2d = projection(lines_list.copy(), f)

    shape.clear()

    colors = [(220, 20, 0), (50, 220, 0), (200, 200, 0), (0, 20, 200),
              (250, 100, 0), (20, 160, 220), (170, 0, 250), (200, 0, 100)]

    for n in range(len(lines2d)):
        if(lines2d[n] == NULL):
            continue
        pkt1 = lines2d[n].p1
        pkt2 = lines2d[n].p2
        '''
        ad = f/300
        if f < 0:
            ad = 0.0
        line_width = 1 + ad  # sposób na zwiększenie imersji?
        '''
        shape.append(shapes.Line(pkt1.x, pkt1.y, pkt2.x, pkt2.y,
                     width=line_width, color=colors[math.floor(n/12)], batch=batch))


pyglet.clock.schedule_interval(update, 1/refreshRate)


@window.event
def on_draw():
    window.clear()
    batch.draw()


pyglet.app.run()

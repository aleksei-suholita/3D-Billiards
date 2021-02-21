from random import randint

from vpython import *


class Ball(sphere):  # Billiard ball class
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.step = vec(kwargs["velocity"] * sin(kwargs["theta"]) * cos(kwargs["phi"]),
                        kwargs["velocity"] * sin(kwargs["theta"]) * sin(kwargs["phi"]),
                        kwargs["velocity"] * cos(kwargs["theta"]))


deg = 10  # Rounding value
count_balls = 10
L = 100  # Rib length
radius_of_ball = 5
r = 2  # Rib radius

scene = canvas(width=1200,
               height=720)

box_bottom = curve(color=color.white, radius=r, opacity=50)
box_bottom.append([vector(-L, -L, -L),
                   vector(-L, -L, L),
                   vector(L, -L, L),
                   vector(L, -L, -L),
                   vector(-L, -L, -L)])
box_top = curve(color=color.white,
                radius=r, opacity=50)
box_top.append([vector(-L, L, -L),
                vector(-L, L, L),
                vector(L, L, L),
                vector(L, L, -L),
                vector(-L, L, -L)])
vert1 = curve(vector(-L, -L, -L), vector(-L, L, -L), color=color.white, radius=r, opacity=50)
vert2 = curve(vector(-L, -L, L), vector(-L, L, L), color=color.white, radius=r, opacity=50)
vert3 = curve(vector(L, -L, L), vector(L, L, L), color=color.white, radius=r, opacity=50)
vert4 = curve(vector(L, -L, -L), vector(L, L, -L), color=color.white, radius=r, opacity=50)
balls = []
vectors_vel = []  # Vectors of velocity
pos_pos = L - radius_of_ball  # Possible position

# Generating random balls
for i in range(count_balls):
    balls.append(Ball(
        pos=vector(randint(-pos_pos, pos_pos), randint(-pos_pos, pos_pos), randint(-pos_pos, pos_pos)),
        radius=radius_of_ball, phi=2 * pi * random(), theta=pi * random(), velocity=randint(1, 10),
        color=vec(vector((i + 1) / count_balls, 0, 0)), opacity=0.3))
    vectors_vel.append(attach_arrow(balls[i], "step", scale=0.5 * radius_of_ball, shaftwidth=0.1 * radius_of_ball,
                                    color=balls[i].color))


def check_collisions():
    hits = []
    for first in range(len(balls)):
        for second in range(first + 1, len(balls)):
            if sqrt((balls[first].pos.x - balls[second].pos.x) ** 2 +
                    (balls[first].pos.y - balls[second].pos.y) ** 2 +
                    (balls[first].pos.z - balls[second].pos.z) ** 2) <= radius_of_ball * 2:
                hits.append([balls[first], balls[second]])
    return hits


def solve_plane(norm, v):
    global center
    t = -((norm.x * v.x + norm.y * v.y + norm.z * v.z + norm.x * -center.x + norm.y * -center.y + norm.z * -center.z) /
          (norm.x ** 2 + norm.y ** 2 + norm.z ** 2))
    return vec(norm.x * t + v.x, norm.y * t + v.y, norm.z * t + v.z)


def direction(a, b):
    return vec(b.x - a.x, b.y - a.y, b.z - a.z)


while True:
    rate(80)

    for i in range(count_balls):
        # Next pos
        balls[i].pos = balls[i].pos + balls[i].step

    for i in check_collisions():
        first_ball = i[0]
        second_ball = i[1]
        # time.sleep(5)
        center = vec((second_ball.pos.x + first_ball.pos.x) / 2,
                     (second_ball.pos.y + first_ball.pos.y) / 2,
                     (second_ball.pos.z + first_ball.pos.z) / 2)
        normal = direction(first_ball.pos, second_ball.pos)
        # Normal that going from the center between balls to their centers
        normal1 = direction(center, first_ball.pos)
        normal2 = direction(center, second_ball.pos)
        # Projections of velocity vectors on their normal
        projection_v1_n = first_ball.step.proj(normal1)
        projection_v2_n = second_ball.step.proj(normal2)
        # Visualization of projections
        # proj_1_1 = arrow(pos=first_ball.pos, axis=projection_v1_n, scale=0.5 * radius_of_ball,
        #                  shaftwidth=0.1 * radius_of_ball, )
        # proj_2_1 = arrow(pos=second_ball.pos, axis=projection_v2_n, scale=0.5 * radius_of_ball,
        #                  shaftwidth=0.1 * radius_of_ball, )
        # Real next position
        v1 = first_ball.pos + first_ball.step
        v2 = second_ball.pos + second_ball.step
        # Projection of velocity vectors on the plane lying between the centers of these spheres
        projection_v1_p = solve_plane(normal, v1) - center
        projection_v2_p = solve_plane(normal, v2) - center
        # Visualization of projections
        # proj_1_2 = arrow(pos=center, axis=projection_v1_p,
        #                  scale=0.5 * radius_of_ball, shaftwidth=0.1 * radius_of_ball)
        # proj_2_2 = arrow(pos=center, axis=projection_v2_p,
        #                  scale=0.5 * radius_of_ball, shaftwidth=0.1 * radius_of_ball)
        # Restore velocity
        first_ball.step = projection_v1_p + projection_v2_n
        second_ball.step = projection_v2_p + projection_v1_n
        # time.sleep(5)

    for i in range(count_balls):
        real_pos = balls[i].pos

        if abs(real_pos.x) > L - r:
            if real_pos.x < 0:
                balls[i].step.x = abs(balls[i].step.x)
            else:
                balls[i].step.x = -abs(balls[i].step.x)

        if abs(real_pos.y) > L - r:
            if real_pos.y < 0:
                balls[i].step.y = abs(balls[i].step.y)
            else:
                balls[i].step.y = -abs(balls[i].step.y)

        if abs(real_pos.z) > L - r:
            if real_pos.z < 0:
                balls[i].step.z = abs(balls[i].step.z)
            else:
                balls[i].step.z = -abs(balls[i].step.z)

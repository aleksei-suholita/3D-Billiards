from vpython import *


class Ball(sphere):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, pos=sphere_to_cartesian(kwargs["theta_pos"], kwargs["phi_pos"]))
        if "velocity" in kwargs.keys():
            self.step = vec(kwargs["velocity"] * sin(kwargs["theta"]) * cos(kwargs["phi"]),
                            kwargs["velocity"] * sin(kwargs["theta"]) * sin(kwargs["phi"]),
                            kwargs["velocity"] * cos(kwargs["theta"]))
        else:
            self.step = vec(0, 0, 0)
        self.in_game = True

    def set_next_pos(self):
        next_pos = self.pos + self.step
        perpendicular = cross(self.pos, self.step)
        tang = cross(self.pos, perpendicular)
        self.pos = next_pos.norm() * R
        self.step = - tang.norm() * self.step.mag * coefficient_of_friction


def cartesian_to_sphere(vel):
    global R
    return vec(R, acos(vel.z / R), atan(vel.y / vel.x))


def sphere_to_cartesian(theta, phi):
    global R
    return vec(R * sin(theta) * cos(phi), R * sin(theta) * sin(phi), R * cos(theta))


def moving():
    global balls
    return max([i.step.mag for i in balls] + [general_ball.step.mag])


def solve_plane(norm, v):
    global center
    t = -((norm.x * v.x + norm.y * v.y + norm.z * v.z + norm.x * -center.x + norm.y * -center.y + norm.z * -center.z) /
          (norm.x ** 2 + norm.y ** 2 + norm.z ** 2))
    return vec(norm.x * t + v.x, norm.y * t + v.y, norm.z * t + v.z)


def direction(a, b):
    return vec(b.x - a.x, b.y - a.y, b.z - a.z)


def check_collisions():
    global balls, general_ball
    balls.append(general_ball)
    hits = []
    for i in range(len(balls)):
        if balls[i].in_game:
            for j in range(i + 1, len(balls)):
                if sqrt((balls[i].pos.x - balls[j].pos.x) ** 2 +
                        (balls[i].pos.y - balls[j].pos.y) ** 2 +
                        (balls[i].pos.z - balls[j].pos.z) ** 2) <= radius_of_ball * 2:
                    hits.append([balls[i], balls[j]])
    balls.pop()
    return hits


def set_constant(radius=None, coefficient_1=None, coefficient_2=None):
    global R, coefficient_of_friction, coefficient_of_elasticity, radius_of_ball, \
        radius_of_ball_text, coefficient_of_friction_text, coefficient_of_elasticity_text
    if radius is not None:
        radius_of_ball = radius
        R = radius + radius_of_earth
        radius_of_ball_text.text = str(radius)
    if coefficient_1 is not None:
        coefficient_of_friction = coefficient_1
        coefficient_of_friction_text.text = str(coefficient_1)
    if coefficient_2 is not None:
        coefficient_of_elasticity = coefficient_2
        coefficient_of_elasticity_text.text = str(coefficient_2)


def del_object(*args):
    for v_object in args:
        v_object.visible = False


def reset():
    global xy_pocket, xz_pocket, yz_pocket, pocket_radius, balls_count, balls, radius_of_ball, general_ball, cue, in_game
    del_object(xy_pocket, xz_pocket, yz_pocket, general_ball, *balls)
    if not in_game:
        del_object(cue)
    in_game = False
    pocket_radius = radius_of_ball * 1.25
    general_ball = Ball(theta_pos=pi / 2, phi_pos=pi / 4, radius=radius_of_ball)
    cue = cylinder(pos=general_ball.pos,
                   axis=vector(1, 1, (general_ball.pos.x + general_ball.pos.y) / general_ball.pos.z).norm() *
                        radius_of_ball * 15,
                   radius=radius_of_ball * 0.1, color=color.orange)
    xy_pocket = cylinder(radius=pocket_radius, pos=vec(0, 0, radius_of_earth),
                         axis=vec(0, 0, -radius_of_earth * 2), opacity=0.1, color=color.green)
    xz_pocket = cylinder(radius=pocket_radius, pos=vec(0, radius_of_earth, 0),
                         axis=vec(0, -radius_of_earth * 2, 0), opacity=0.1, color=color.green)
    yz_pocket = cylinder(radius=pocket_radius, pos=vec(radius_of_earth, 0, 0),
                         axis=vec(- radius_of_earth * 2, 0, 0), opacity=0.1, color=color.green)
    for i in range(balls_count - 1):
        balls.append(Ball(phi_pos=round(((360 * i // balls_count + 2) * pi / 180), dig),
                          theta_pos=round(round(pi / 2 if i % 2 == 0 else 3 * pi / 2, dig)),
                          radius=radius_of_ball,
                          color=vec(vector((i + 1) / balls_count, 0, 0))))


def validate(ball):
    if (vec(R, 0, 0) - vec(abs(ball.pos.x), abs(ball.pos.y), abs(ball.pos.z))).mag < 1.5 * radius_of_ball:
        return False
    elif (vec(0, R, 0) - vec(abs(ball.pos.x), abs(ball.pos.y), abs(ball.pos.z))).mag < 1.5 * radius_of_ball:
        return False
    elif (vec(0, 0, R) - vec(abs(ball.pos.x), abs(ball.pos.y), abs(ball.pos.z))).mag < 1.5 * radius_of_ball:
        return False
    else:
        return True


"""
# Don't work
def validate(ball):
    return not (vec(R, 0, 0) - vec(abs(ball.pos.x), abs(ball.pos.y), abs(ball.pos.z))).mag < 1.5 * radius_of_ball or \
           (vec(0, R, 0) - vec(abs(ball.pos.x), abs(ball.pos.y), abs(ball.pos.z))).mag < 1.5 * radius_of_ball or \
           (vec(0, 0, R) - vec(abs(ball.pos.x), abs(ball.pos.y), abs(ball.pos.z))).mag < 1.5 * radius_of_ball
"""


def move():
    global balls, general_ball
    balls.append(general_ball)
    general_ball.set_next_pos()
    for i in range(len(balls)):
        if not validate(balls[i]):
            balls[i].in_game = False
            balls[i].pos = vec(0, 0, 0)
            del_object(balls[i])
        balls[i].set_next_pos()
    balls.pop()

    for i in check_collisions():
        first_ball = i[0]
        second_ball = i[1]
        original_step_1 = first_ball.step
        original_step_2 = second_ball.step
        first_ball.step = - first_ball.step * epsilon
        second_ball.step = - second_ball.step * epsilon
        while (second_ball.pos - first_ball.pos).mag <= 2 * radius_of_ball:
            first_ball.set_next_pos()
            second_ball.set_next_pos()
        first_ball.step = original_step_1
        second_ball.step = original_step_2
        global center
        center = vec((second_ball.pos.x + first_ball.pos.x) / 2,
                     (second_ball.pos.y + first_ball.pos.y) / 2,
                     (second_ball.pos.z + first_ball.pos.z) / 2)
        normal = direction(first_ball.pos, second_ball.pos)
        normal1 = direction(center, first_ball.pos)
        normal2 = direction(center, second_ball.pos)
        projection_v1_n = first_ball.step.proj(normal1)
        projection_v2_n = second_ball.step.proj(normal2)
        v1 = first_ball.pos + first_ball.step
        v2 = second_ball.pos + second_ball.step
        projection_v1_p = solve_plane(normal, v1) - center
        projection_v2_p = solve_plane(normal, v2) - center
        first_ball.step = (projection_v1_p + projection_v2_n) * coefficient_of_elasticity
        second_ball.step = (projection_v2_p + projection_v1_n) * coefficient_of_elasticity


# Constants
dig = 10  # Value to round
balls_count = 11
radius_of_earth = 370
radius_of_ball = 30
R = radius_of_earth + radius_of_ball
epsilon = 0.01
coefficient_of_friction = 0.996
coefficient_of_elasticity = 0.87
standard_angle = 180 / (5000 * pi)
balls = []
vectors_vel = []
scene = canvas(width=1440,
               height=600)
earth = sphere(radius=radius_of_earth,
               color=color.green,
               opacity=0.25)
general_ball = Ball(theta_pos=pi / 2, phi_pos=pi / 4)
pocket_radius = 1.25 * radius_of_ball
xy_pocket = cylinder()
xz_pocket = cylinder()
yz_pocket = cylinder()
cue = cylinder()

scene.append_to_caption("\nSelect coefficient of friction\n")
"""
set_coefficients_of_friction = slider(value=coefficient_of_friction, max=0.999,
                                      bind=lambda x: set_constant(coefficient_1=x.value))
coefficient_of_friction_text = wtext(text=str(coefficient_of_friction))
scene.append_to_caption("\nSelect coefficient of elasticity\n")
set_coefficients_of_elasticity = slider(value=coefficient_of_elasticity, max=0.999,
                                        bind=lambda x: set_constant(coefficient_2=x.value))
coefficient_of_elasticity_text = wtext(text=str(coefficient_of_elasticity))
scene.append_to_caption("\nSelect radius of balls\n")
set_radius_of_ball = slider(value=radius_of_ball, max=30,
                            bind=lambda x: set_constant(radius=x.value))
radius_of_ball_text = wtext(text=str(radius_of_ball))
scene.append_to_caption("\n")
"""
scene.up = vector(0, 0, 1)
scene.camera.pos = vector(660, 660, 500)
scene.camera.axis = vector(-660, -660, -500)
in_game = False
reset()
while True:
    rate(30)
    keys = keysdown()
    if not in_game:
        if 'left' in keys:
            cue.rotate(angle=standard_angle, axis=general_ball.pos, origin=general_ball.pos)
        if 'right' in keys:
            cue.rotate(angle=-standard_angle, axis=general_ball.pos, origin=general_ball.pos)
        if 'up' in keys:
            if (general_ball.pos - cue.pos).mag < 4 * radius_of_ball:
                cue.pos += cue.axis * 0.01
        if 'down' in keys:
            if (general_ball.pos - cue.pos).mag > radius_of_ball:
                cue.pos -= cue.axis * 0.01
        if 'backspace' in keys:
            general_ball.step = (general_ball.pos - cue.pos) * 0.49
            del_object(cue)
            in_game = True
    else:
        del cue
        while moving() > 0.1:
            rate(80)
            move()
        else:
            cue = cylinder(pos=general_ball.pos,
                           axis=vector(1, 1,
                                       (general_ball.pos.x + general_ball.pos.y) / -general_ball.pos.z).norm() *
                                radius_of_ball * 15, radius=radius_of_ball * 0.1, color=color.orange)
            in_game = False

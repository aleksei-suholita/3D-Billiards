from vpython import sphere, vec, sin, cos, cross, cylinder, color, sqrt, shapes, pi, extrusion, textures, canvas, \
    slider, wtext, button, rate, keysdown


class Ball(sphere):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, pos=ball_pos(kwargs["phi_pos"], z=kwargs["z"]))
        if "velocity" in kwargs.keys():
            self.step = vec(kwargs["velocity"] * sin(kwargs["theta"]) * cos(kwargs["phi"]),
                            kwargs["velocity"] * sin(kwargs["theta"]) * sin(kwargs["phi"]),
                            kwargs["velocity"] * cos(kwargs["theta"]))
        else:
            self.step = vec(0, 0, 0)
        self.in_game = True

    def set_next_pos(self, back=False):
        original_pos_z = self.pos.z
        original_step_z = self.step.z
        self.pos.z = 0
        self.step.z = 0
        next_pos = self.pos + self.step
        perpendicular = cross(self.pos, self.step)
        tang = cross(self.pos, perpendicular)
        self.pos = next_pos.norm() * R
        self.pos.z = original_pos_z + original_step_z
        if not back:
            self.step = - tang.norm() * self.step.mag * coefficient_of_friction
            self.step.z = original_step_z * coefficient_of_friction
        else:
            self.step = - tang.norm() * self.step.mag
            self.step.z = original_step_z


def ball_pos(phi, z):
    return vec(R * cos(phi), R * sin(phi), z)


def moving():
    global balls
    return max([i.step.mag for i in balls] + [general_ball.step.mag])


def solve_plane(normal, vel):
    global center
    t = -((normal.x * vel.x + normal.y * vel.y + normal.z * vel.z + normal.x * -center.x +
           normal.y * -center.y + normal.z * -center.z) /
          (normal.x ** 2 + normal.y ** 2 + normal.z ** 2))
    return vec(normal.x * t + vel.x, normal.y * t + vel.y, normal.z * t + vel.z)


def direction(a, b):
    return vec(b.x - a.x, b.y - a.y, b.z - a.z)


def generate_cue():
    global cue
    cue = cylinder(pos=general_ball.pos,
                   axis=vec(0, 0, 1) * radius_of_ball * 15,
                   radius=radius_of_ball * 0.1, color=color.orange)


def check_collisions():
    global balls, general_ball
    balls.append(general_ball)
    hits = []
    for i in range(len(balls)):
        if balls[i].in_game:
            for j in range(i + 1, len(balls)):
                if balls[j].in_game and sqrt((balls[i].pos.x - balls[j].pos.x) ** 2 +
                                             (balls[i].pos.y - balls[j].pos.y) ** 2 +
                                             (balls[i].pos.z - balls[j].pos.z) ** 2) <= radius_of_ball * 2:
                    hits.append([balls[i], balls[j]])
    balls.pop()
    return hits


def set_constant(radius=None, coefficient_1=None, coefficient_2=None):
    global coefficient_of_friction, coefficient_of_elasticity, radius_of_ball, next_radius_of_ball, \
        next_coefficient_of_elasticity, radius_of_ball_text, coefficient_of_friction_text, \
        coefficient_of_elasticity_text, next_coefficient_of_friction

    if radius is not None:
        next_radius_of_ball = radius
        radius_of_ball_text.text = str(radius)
    if coefficient_1 is not None:
        next_coefficient_of_friction = coefficient_1
        coefficient_of_friction_text.text = str(coefficient_1)
    if coefficient_2 is not None:
        next_coefficient_of_elasticity = coefficient_2
        coefficient_of_elasticity_text.text = str(coefficient_2)


def del_object(*args):
    for v_object in args:
        v_object.visible = False


def reset():
    global R, pocket_radius, next_radius_of_ball, radius_of_ball, pocket_top, pocket_bottom, pocket_positions, \
        next_coefficient_of_elasticity, next_coefficient_of_friction, coefficient_of_elasticity, \
        balls_count, balls, radius_of_ball, general_ball, cue, in_game, coefficient_of_friction, circle
    del_object(general_ball, *balls)
    if "pocket_top" in globals():
        del_object(pocket_top, pocket_bottom)
    coefficient_of_elasticity = next_coefficient_of_elasticity
    coefficient_of_friction = next_coefficient_of_friction
    radius_of_ball = next_radius_of_ball
    R = radius_of_ball + radius_of_earth
    pocket_radius = radius_of_ball * 1.25
    circle = shapes.circle(radius=radius_of_earth + radius_of_ball * 3.2)
    positions = []
    pocket_positions = []
    angle = (2 * pi) / 3
    for _ in range(3):
        new_position = ball_pos(angle, 0)
        new_real_position = ball_pos(angle + pi / 3, 0)
        pocket_positions.append([new_real_position.x, new_real_position.y])
        positions.append(shapes.rectangle(height=pocket_radius * 2, width=pocket_radius * 2,
                                          pos=[new_position.x, new_position.y],
                                          rotate=angle))
        angle += (2 * pi) / 3
    pocket_top = extrusion(path=[vec(0, 0, L * 1.01), vec(0, 0, L * 1.05)], shape=[circle, *positions],
                           texture=textures.wood, opacity=0.7)
    pocket_bottom = extrusion(path=[vec(0, 0, -L * 1.05), vec(0, 0, -L * 1.01)], shape=[circle, *positions],
                              texture=textures.wood, opacity=0.7)
    scene.title = "3D Billiards v2"
    general_ball = Ball(phi_pos=pi / 4, z=0, radius=radius_of_ball, in_game=True)
    if 'cue' in globals():
        del_object(cue)
        del cue
    generate_cue()
    in_game = False
    balls = []
    for i in range(balls_count - 1):
        balls.append(Ball(phi_pos=round(((360 * i // balls_count + 2) * pi / 180), dig),
                          z=-L / 2 if i % 2 == 0 else L / 2,
                          radius=radius_of_ball,
                          color=vec(vec((i + 1) / balls_count, 0, 0))))


def validate(ball):
    global pocket_positions
    for i in pocket_positions:
        if sqrt((i[0] - ball.pos.x) ** 2 + (i[1] - ball.pos.y) ** 2) < radius_of_ball * 1.1:
            return False
    return True


def move():
    global balls, general_ball, center
    balls.append(general_ball)
    for i in range(len(balls)):
        if balls[i].in_game and abs(balls[i].pos.z) > L - radius_of_ball:
            if validate(balls[i]):
                if balls[i].pos.z < 0:
                    balls[i].step.z = abs(balls[i].step.z) * 0.56
                else:
                    balls[i].step.z = -abs(balls[i].step.z) * 0.56
            else:
                del_object(balls[i])
                balls[i].step = vec(0, 0, 0)
                balls[i].in_game = False
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
            first_ball.set_next_pos(back=True)
            second_ball.set_next_pos(back=True)
        first_ball.step = original_step_1
        second_ball.step = original_step_2
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
balls_count = 13
radius_of_earth = 370
radius_of_ball = 30
next_radius_of_ball = 30
R = radius_of_earth + radius_of_ball
epsilon = 0.01
L = 500
coefficient_of_friction = 0.996
next_coefficient_of_friction = 0.996
coefficient_of_elasticity = 0.87
next_coefficient_of_elasticity = 0.87
standard_angle = 180 / (5000 * pi)
balls = []
vectors_vel = []
scene = canvas(width=800,
               height=700,
               title="3D Cylinder Billiards")
earth = cylinder(pos=vec(0, 0, -L), axis=vec(0, 0, 2 * L), radius=radius_of_earth, opacity=0.3, color=color.green)
general_ball = Ball(phi_pos=pi / 4, z=0)
circle = shapes.circle()
pocket_radius = 1.25 * radius_of_ball
cue = cylinder()
pocket_positions = []
center = vec(0, 0, 0)

scene.append_to_caption(
    "\nWelcome to the game 3D billiards. If there is a cue on the screen, you can move it with the up, down, left,\n"
    "right buttons, press backspace to strike. You can also change the game parameters by moving the sliders, they\n"
    "will change after pressing the 'play again' button. To rotate 'camera', drag with right button or Ctrl-drag.\n"
    "To zoom, drag with middle button, or use scroll wheel.\n\nSelect coefficient of friction\n")

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
reset_button = button(text="play again", bind=reset)
scene.up = vec(0, 0, 1)
scene.camera.pos = vec(660, 660, 500)
scene.camera.axis = vec(-660, -660, -500)
in_game = False
reset()
while True:
    rate(30)
    keys = keysdown()
    if not in_game:
        if 'left' in keys:
            cue.rotate(angle=standard_angle, axis=vec(general_ball.pos.x, general_ball.pos.y, 0),
                       origin=general_ball.pos)
        if 'right' in keys:
            cue.rotate(angle=-standard_angle, axis=vec(general_ball.pos.x, general_ball.pos.y, 0),
                       origin=general_ball.pos)
        if 'up' in keys and (general_ball.pos - cue.pos).mag < 4 * radius_of_ball:
            cue.pos += cue.axis * 0.01
        if 'down' in keys and (general_ball.pos - cue.pos).mag > radius_of_ball:
            cue.pos -= cue.axis * 0.01
        if 'backspace' in keys:
            general_ball.step = (general_ball.pos - cue.pos) * 0.49
            del_object(cue)
            del cue
            in_game = True
    else:
        while moving() > 0.1:
            rate(80)
            move()
        if general_ball.in_game:
            if "cue" not in globals():
                generate_cue()
            in_game = False
        else:
            scene.title = "Game over"

# note: import * is there for ease of use, specific imports for lsp
from manim import *
from manim import (
    np,
    config,
    MovingCameraScene,
    LEFT,
    RIGHT,
    UP,
    DOWN,
    ValueTracker,
    Dot,
    Line,
    linear,
    TracedPath,
    VMobject,
    ManimColor,
)
import random

# rendering constants
runtime = 60.0  # runtime of animation
simulation_time = 90.0  # time experienced by simulation
dt = simulation_time / (config.frame_rate * runtime)
dissipate_after = -1.0  # -1.0 for no dissipation
num_pends = 5
mode = "single"  # sequential, random, single

# physical constants
g = 9.81
l1, l2 = 2.0, 1.0
m1, m2 = 1.0, 1.0
theta1_i, theta2_i = 0.75 * np.pi, 0.75 * np.pi
dtheta1_i, dtheta2_i = 0.0, 0.0

#  #  #  #  #  #  #  #


# get derivative info for runge-kutta
def diff(state):
    theta1 = state[0]
    dtheta1 = state[1]
    theta2 = state[2]
    dtheta2 = state[3]

    delta_theta = theta1 - theta2
    M = m1 + m2
    alpha = m1 + m2 * (np.sin(delta_theta) ** 2)

    eq6 = (
        -m2 * l2 * (dtheta2**2) * np.sin(delta_theta)
        - m2 * l1 * (dtheta1**2) * np.sin(delta_theta) * np.cos(delta_theta)
        - M * g * np.sin(theta1)
        + m2 * g * np.sin(theta2) * np.cos(delta_theta)
    )
    ddtheta1 = eq6 / (l1 * alpha)

    eq7 = (
        M * l1 * (dtheta1**2) * np.sin(delta_theta)
        + m2 * l2 * (dtheta2**2) * np.sin(delta_theta) * np.cos(delta_theta)
        + M * g * np.sin(theta1) * np.cos(delta_theta)
        - M * g * np.sin(theta2)
    )
    ddtheta2 = eq7 / (l2 * alpha)

    return np.array((dtheta1, ddtheta1, dtheta2, ddtheta2))


# rk4 yass
def update_pendulum(theta1, dtheta1, theta2, dtheta2):
    state = np.array((theta1[-1], dtheta1[-1], theta2[-1], dtheta2[-1]))

    k1 = diff(state)
    k2 = diff(state + dt * (k1 / 2))
    k3 = diff(state + dt * (k2 / 2))
    k4 = diff(state + dt * k3)

    state += (dt / 6) * (k1 + 2 * k2 + 2 * +k3 + k4)

    theta1.append(state[0])
    dtheta1.append(state[1])
    theta2.append(state[2])
    dtheta2.append(state[3])


# double pendulum object
class DoublePendulum(VMobject):
    def __init__(self, theta1_i, theta2_i, color, **kwargs):
        VMobject.__init__(self, **kwargs)

        # values to keep track of
        self.theta1 = ValueTracker(theta1_i)
        self.hist_theta1 = [self.theta1.get_value()]
        self.theta2 = ValueTracker(theta2_i)
        self.hist_theta2 = [self.theta2.get_value()]

        self.dtheta1 = ValueTracker(dtheta1_i)
        self.hist_dtheta1 = [self.dtheta1.get_value()]
        self.dtheta2 = ValueTracker(dtheta2_i)
        self.hist_dtheta2 = [self.dtheta2.get_value()]

        # update function called once per frame
        def custom_update(self, **kwargs):
            update_pendulum(
                self.hist_theta1, self.hist_dtheta1, self.hist_theta2, self.hist_dtheta2
            )

            self.theta1.set_value(self.hist_theta1[-1])
            self.theta2.set_value(self.hist_theta2[-1])

            self.dtheta1.set_value(self.hist_dtheta1[-1])
            self.dtheta2.set_value(self.hist_dtheta2[-1])

        self.add_updater(custom_update)

        # draw mass and arm
        self.mass1 = Dot(color=ManimColor(color))
        self.mass1.add_updater(
            lambda mob: mob.move_to(
                (l1 * np.sin(self.theta1.get_value())) * RIGHT
                + (l1 * np.cos(self.theta1.get_value())) * DOWN
            )
        )

        self.add(self.mass1)

        self.mass2 = Dot(color=ManimColor(color))
        self.mass2.add_updater(
            lambda mob: mob.move_to(
                self.mass1.get_center()
                + (l2 * np.sin(self.theta2.get_value())) * RIGHT
                + (l2 * np.cos(self.theta2.get_value())) * DOWN
            )
        )

        self.add(self.mass2)

        self.trace = TracedPath(
            self.mass2.get_start,
            stroke_color=ManimColor(color),
            dissipating_time=(dissipate_after if (dissipate_after != -1.0) else None),
        )
        self.add(self.trace)

        self.origin = Dot()

        self.line1 = Line(color=ManimColor(color))
        self.line1.add_updater(
            lambda mob: mob.put_start_and_end_on(
                self.origin.get_center(), self.mass1.get_center()
            )
        )
        self.line2 = Line(color=ManimColor(color))
        self.line2.add_updater(
            lambda mob: mob.put_start_and_end_on(
                self.mass1.get_center(), self.mass2.get_center()
            )
        )

        self.add(self.line1, self.line2, self.origin)


# simulation happens here
class Simulation(MovingCameraScene):
    def construct(self):
        # print out some basic info about sim
        print("frame rate: " + str(config.frame_rate))
        print("runtime: " + str(runtime))
        print("simulation_time: " + str(simulation_time))
        print("dt: " + str(dt))

        # scale frame to zoom out
        self.camera.frame.scale(((l1 + l2) * 2 * 1.15) / (self.camera.frame.height))

        # time tracker needed for animation length
        time = ValueTracker(0)

        match mode:
            case "sequential":
                for i in range(num_pends):
                    color = hex(int((theta1_i + i * 0.00075) / (2 * np.pi) * 2**24))
                    pend = DoublePendulum(
                        theta1_i + i * 0.01, theta2_i + i * 0.01, str(color)
                    )
                    self.add(pend)
            case "random":
                for i in range(num_pends):
                    color = hex(random.randrange(0, 2**24))
                    theta1 = random.uniform(0, 2 * np.pi)
                    theta2 = random.uniform(0, 2 * np.pi)
                    pend = DoublePendulum(theta1, theta2, str(color))
                    self.add(pend)
            case "single":
                pend = DoublePendulum(theta1_i, theta2_i, "#c95792")
                self.add(pend)

        self.play(
            time.animate.set_value(simulation_time), rate_func=linear, run_time=runtime
        )

        print("yayay")
        print()

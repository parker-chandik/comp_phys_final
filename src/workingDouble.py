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
)

# rendering constants
runtime = 20.0  # runtime of animation
simulation_time = 10.0  # time experienced by simulation
dt = simulation_time / (config.frame_rate * runtime)

# physical constants
g = 9.81
l1, l2 = 1.0, 2.0
m1, m2 = 1.0, 1.0
theta1_i, theta2_i = 0.75, 0.75
dtheta1_i, dtheta2_i = 0.0, 0.0

#  #  #  #  #  #  #  #

# simple pendulum example
#
# theta'' + (g / l) * np.sin(theta) = 0
#   -> theta'' = - (g / l) * np.sin(theta)


# 2nd order Euler
# def update_pendulum(theta, dtheta, dt):
#     a = - (g / l) * np.np.sin(theta[-1])

#     theta_new = theta[-1] + dtheta[-1] * dt + 0.5 * a * dt**2
#     dtheta_new = dtheta[-1] + a * dt

#     return theta_new, dtheta_new


# acceleration for first pendulum
# all inputs are lists with all historical values up to this point
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
    # print("eq7: " + str(eq7))
    # print("l2: " + str(l2))
    # print("alpha: " + str(alpha))
    ddtheta2 = eq7 / (l2 * alpha)

    return np.array((dtheta1, ddtheta1, dtheta2, ddtheta2))


# rk4 yass
def update_pendulum(theta1, dtheta1, theta2, dtheta2):
    state = np.array((theta1[-1], dtheta1[-1], theta2[-1], dtheta2[-1]))

    k1 = diff(state)
    k2 = diff(state + dt * (k1 / 2))
    k3 = diff(state + dt * (k2 / 2))
    k4 = diff(state + dt * k3)

    # print("initial state:")
    # print(state)

    # print("diff")
    # print(k1)

    state += (dt / 6) * (k1 + 2 * k2 + 2 * +k3 + k4)

    # print("final state:")
    # print(state)

    theta1.append(state[0])
    dtheta1.append(state[1])
    theta2.append(state[2])
    dtheta2.append(state[3])


class DoublePendulum(MovingCameraScene):
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
        hist_time = [time.get_value(), time.get_value()]

        # values to keep track of
        theta1 = ValueTracker(theta1_i)
        hist_theta1 = [theta1.get_value(), theta1.get_value()]
        theta2 = ValueTracker(theta2_i)
        hist_theta2 = [theta2.get_value(), theta2.get_value()]

        dtheta1 = ValueTracker(dtheta1_i)
        hist_dtheta1 = [dtheta1.get_value(), dtheta1.get_value()]
        dtheta2 = ValueTracker(dtheta2_i)
        hist_dtheta2 = [dtheta2.get_value(), dtheta2.get_value()]

        print("time: " + str(hist_time[0]))
        print("initial theta 1:  " + str(hist_theta1[0]))
        print("initial dtheta 1: " + str(hist_dtheta1[0]))
        print("initial theta 2:  " + str(hist_theta2[0]))
        print("initial dtheta 2: " + str(hist_dtheta2[0]))
        print()

        # update func to run per frame
        def update(self):
            hist_time.append(time.get_value())
            # dt = hist_time[-1] - hist_time[-2]

            update_pendulum(hist_theta1, hist_dtheta1, hist_theta2, hist_dtheta2)

            theta1.set_value(hist_theta1[-1])
            theta2.set_value(hist_theta2[-1])
            # hist_theta1.append(theta1_new)

            dtheta1.set_value(hist_dtheta1[-1])
            dtheta2.set_value(hist_dtheta2[-1])
            # hist_dtheta.append(dtheta_new)

        # draw mass and arm
        mass1 = Dot()
        mass1.add_updater(update)
        mass1.add_updater(
            lambda mob: mob.move_to(
                (l1 * np.sin(theta1.get_value())) * RIGHT
                + (l1 * np.cos(theta1.get_value())) * DOWN
            )
        )

        self.add(mass1)

        mass2 = Dot()
        mass2.add_updater(
            lambda mob: mob.move_to(
                mass1.get_center()
                + (l2 * np.sin(theta2.get_value())) * RIGHT
                + (l2 * np.cos(theta2.get_value())) * DOWN
            )
        )

        self.add(mass2)

        trace = TracedPath(mass2.get_start)
        self.add(trace)

        origin = Dot()
        line1 = Line()
        line1.add_updater(
            lambda mob: mob.put_start_and_end_on(
                origin.get_center(), mass1.get_center()
            )
        )
        line2 = Line()
        line2.add_updater(
            lambda mob: mob.put_start_and_end_on(mass1.get_center(), mass2.get_center())
        )

        self.add(line1, line2, origin)

        self.play(
            time.animate.set_value(simulation_time), rate_func=linear, run_time=runtime
        )

        # print("yayay")
        print(f"end time: {hist_time[-1]:.2f}")
        print(f"final theta 1: {hist_theta1[-1]:.2f}")
        print(f"final dtheta 1: {hist_dtheta1[-1]:.2f}")
        print(f"final theta 2: {hist_theta2[-1]:.2f}")
        print(f"final dtheta 2: {hist_dtheta2[-1]:.2f}")
        print()

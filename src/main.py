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
)

# rendering constants
runtime = 10.0  # runtime of animation
simulation_time = 20.0  # time experienced by simulation
dt = simulation_time / (config.frame_rate * runtime)

# physical constants
g = 9.81
l1, l2 = 1.0, 2.0
m1, m2 = 1.0, 1.0

#  #  #  #  #  #  #  #

# simple pendulum example
#
# theta'' + (g / l) * sin(theta) = 0
#   -> theta'' = - (g / l) * sin(theta)


# 2nd order Euler
# def update_pendulum(theta, dtheta, dt):
#     a = - (g / l) * np.sin(theta[-1])

#     theta_new = theta[-1] + dtheta[-1] * dt + 0.5 * a * dt**2
#     dtheta_new = dtheta[-1] + a * dt

#     return theta_new, dtheta_new


# bashforth adams
def update_pendulum(theta, dtheta, dt):
    theta_new = theta[-1] + 1.5 * dt * dtheta[-1] - 0.5 * dt * dtheta[-2]
    dtheta_new = (
        dtheta[-1]
        + 1.5 * dt * (-g / l1) * np.sin(theta[-1])
        - 0.5 * dt * (-g / l1) * np.sin(theta[-2])
    )

    return theta_new, dtheta_new


class SimplePendulum(MovingCameraScene):
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
        theta = ValueTracker(0.75)
        hist_theta = [theta.get_value(), theta.get_value()]

        dtheta = ValueTracker(0)
        hist_dtheta = [dtheta.get_value(), dtheta.get_value()]

        print("time: " + str(hist_time[0]))
        print("initial theta:  " + str(hist_theta[0]))
        print("initial dtheta: " + str(hist_dtheta[0]))
        print()

        # update func to run per frame
        def update(self):
            hist_time.append(time.get_value())
            # dt = hist_time[-1] - hist_time[-2]

            theta_new, dtheta_new = update_pendulum(hist_theta, hist_dtheta, dt)

            theta.set_value(theta_new)
            hist_theta.append(theta_new)

            dtheta.set_value(dtheta_new)
            hist_dtheta.append(dtheta_new)

        # draw mass and arm
        ball = Dot()
        ball.add_updater(update)
        ball.add_updater(
            lambda mob: mob.move_to(
                (l1 * np.sin(theta.get_value())) * RIGHT
                + (l1 * np.cos(theta.get_value())) * DOWN
            )
        )

        self.add(ball)

        origin = Dot()
        line = Line()
        line.add_updater(
            lambda mob: mob.put_start_and_end_on(origin.get_center(), ball.get_center())
        )

        self.add(line, origin)

        self.play(
            time.animate.set_value(simulation_time), rate_func=linear, run_time=runtime
        )

        print("yayay")
        print(f"end time: {hist_time[-1]:.2f}")
        print(f"final theta: {hist_theta[-1]:.2f}")
        print(f"final dtheta: {hist_dtheta[-1]:.2f}")
        print()

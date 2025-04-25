from manim import *
from manim import config

# rendering constants
runtime = 10.0          # runtime of animation
total_time = 20.0      # time experienced by simulation

print("frame rate: " + str(config.frame_rate))
print("runtime: " + str(runtime))
print("total_time: " + str(total_time))

# physical constants
g = 9.81
l = 2.0

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
    dtheta_new = dtheta[-1] + 1.5 * dt * (-g/l) * np.sin(theta[-1]) - 0.5 * dt * (-g/l) * np.sin(theta[-2])

    return theta_new, dtheta_new


class SimplePendulum(Scene):
    def construct(self):
        circ = Circle(radius=l)
        self.add(circ)

        # time tracker needed for animation length
        time = ValueTracker(0)
        # old_time = ValueTracker(time.get_value())
        hist_time = [ time.get_value(), time.get_value() ]

        # values to keep track of
        theta   = ValueTracker(0.75)
        hist_theta = [ theta.get_value(), theta.get_value() ]

        dtheta  = ValueTracker(0)
        hist_dtheta = [ dtheta.get_value(), dtheta.get_value() ]

        print("time: " + str(hist_time[0]))
        print("initial theta:  " + str(hist_theta[0]))
        print("initial dtheta: " + str(hist_dtheta[0]))
        print()

        # update func
        def update(self):
            hist_time.append( time.get_value() )
            dt = hist_time[-1] - hist_time[-2]

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
                (l * np.sin(theta.get_value())) * RIGHT +
                (l * np.cos(theta.get_value())) * DOWN
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
            time.animate.set_value(total_time), rate_func=linear, run_time=runtime
        )

        print("yaya")
        print(f"end time: {hist_time[-1]:.2f}")
        print(f"final theta: {hist_theta[-1]:.2f}")
        print(f"final dtheta: {hist_dtheta[-1]:.2f}")
        print()

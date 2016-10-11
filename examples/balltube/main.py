from PyQt5.QtWidgets import QApplication

from pymoskito import Simulator, PostProcessor
# import self defined simulation modules
from model import BallInTubeModel, BallInTubeSpringModel
from control import ExactInputOutputLinearisation, OpenLoop
from feedforward import BallInTubeFeedforward
from visualization import BallInTubeVisualizer

from processing import ErrorProcessor


if __name__ == "__main__":
    # create an Application instance (needed)
    app = QApplication([])

    if 1:
        # create gui
        sim = Simulator()

        # load default config
        sim.load_regimes_from_file("default.sreg")
        sim.apply_regime_by_name("PID_Controller")
        # gui.start_simulation()

        sim.show()
    else:
        post = PostProcessor()
        post.show()

    app.exec_()

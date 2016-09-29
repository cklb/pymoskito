import sys
import os

if __name__ == '__main__':
   if __package__ is None or __package__ == '':
        import car
        __package__ = "car"

    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, parent_dir)

    from PyQt5.QtWidgets import QApplication
    import pymoskito as pm

    from .visualization import CarVisualizer
    from .model import CarModel

    pm.register_simulation_module(pm.Model, CarModel)
    pm.register_visualizer(CarVisualizer)

    app = QApplication([])
    sim = pm.Simulator()
    sim.load_regimes_from_file(os.path.join(parent_dir, "car", "default.sreg"))
    sim.apply_regime_by_name("test")
    sim.show()

    app.exec_()

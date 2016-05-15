from abc import ABCMeta, abstractmethod
from PyQt4.QtGui import QMessageBox


class Visualizer:
    """
    Base Class with some function the help visualizing the system using vtk
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        self.can_reset_view = False

    @abstractmethod
    def update_scene(self, x):
        """
        Hook to update the current visualization state
        :param x: system state vector
        """
        pass

    def reset_camera(self):
        """
        reset camera to original view, will be available if you implement the attributes below and ste the
        'can_reset_view' flag
        :return:
        """
        if self.can_reset_view:
            camera = self.ren.GetActiveCamera()
            camera.SetPosition(self.position)
            camera.SetFocalPoint(self.focal_point)
            camera.SetViewUp(self.view_up)
            camera.SetViewAngle(self.view_angle)
            camera.SetParallelProjection(self.parallel_projection)
            camera.SetParallelScale(self.parallel_scale)
            camera.SetClippingRange(self.clipping_range)


class MplVisualizer(Visualizer):

    def __init__(self):
        Visualizer.__init__(self)

    def on_pick(self, event):
        # The event received here is of the type
        # matplotlib.backend_bases.PickEvent
        #
        # It carries lots of information, of which we're using
        # only a small amount here.
        box_points = event.artist.get_bbox().get_points()
        msg = "You've clicked on a bar with coords:\n %s" % box_points

        QMessageBox.information(self, "Click!", msg)

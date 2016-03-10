from abc import ABCMeta, abstractmethod


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


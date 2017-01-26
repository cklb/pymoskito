from abc import ABCMeta, abstractmethod

from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT, FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

try:
    import vtk
    from vtk.qt.QVTKRenderWindowInteractor import *

    class QVTKRenderWindowInteractor(QVTKRenderWindowInteractor):
        """
        overload class to patch problem with zooming in vtk window
        the reason is that the QWheelEvent in PyQt5 hasn't the function delta()
        so we have to replace that with angleDelta()
        the error is caused by vtk 7.0.0
        """
        # override function
        def wheelEvent(self, ev):
            if ev.angleDelta().y() >= 0:
                self._Iren.MouseWheelForwardEvent()
            else:
                self._Iren.MouseWheelBackwardEvent()

except ImportError as e:
    QVTKRenderWindowInteractor = None


class Visualizer(metaclass=ABCMeta):
    """
    Base Class for animation
    """

    def __init__(self):
        self.can_reset_view = False

    @abstractmethod
    def update_scene(self, x):
        """
        Hook to update the current visualization state
        :param x: system state vector
        """
        pass


class VtkVisualizer(Visualizer):
    """
    Base Class with some function the help visualizing the system using vtk
    """

    def __init__(self):
        Visualizer.__init__(self)

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
    """
    Base Class with some function the help visualizing the system using matplotlib
    """

    def __init__(self, q_widget, q_layout):
        Visualizer.__init__(self)
        self.qWidget = q_widget
        self.qLayout = q_layout
        self.dpi = 100
        self.fig = Figure((5.0, 4.0), facecolor='white', dpi=self.dpi)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.qWidget)
        self.axes = self.fig.add_subplot(111)
        self.mpl_toolbar = NavigationToolbar2QT(self.canvas, self.qWidget)
        self.qLayout.addWidget(self.mpl_toolbar)
        self.qLayout.addWidget(self.canvas)
        self.qWidget.setLayout(self.qLayout)

from abc import ABCMeta, abstractmethod

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from PyQt4 import QtCore, QtGui
import os
import time

class Visualizer:
    """
    Base Class for animation
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
        self.q_widget = q_widget
        self.q_layout = q_layout

        # figure
        self.dpi = 100
        self.fig = Figure((15.0, 11.0), facecolor='white', dpi=self.dpi)
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.canvas.setParent(self.q_widget)
        self.axes = self.fig.add_subplot(111)

        # toolbar
        self.mpl_toolbar = NavigationToolbar2QT(self.canvas, self.q_widget)

        # save pictures
        self.max_height = 15
        self.picture_path = self.create_dir('animation_pictures')

        self.save_cb = QtGui.QCheckBox("&Save")
        self.save_cb.setMaximumHeight(self.max_height)
        self.save_cb.setChecked(False)
        self.q_widget.connect(self.save_cb, QtCore.SIGNAL('stateChanged(int)'), self.save_cb_changed)
        self.time_stamps = list()
        self.frame_counter = 0
        self.file_name_counter = 0

        self.label1 = QtGui.QLabel('each')
        self.label1.setMaximumHeight(self.max_height)
        self.label2 = QtGui.QLabel('')
        self.label2.setMaximumHeight(self.max_height)
        self.label3 = QtGui.QLabel('')
        self.label3.setMaximumHeight(self.max_height)

        self.save_each = 1
        self.combo_box = QtGui.QComboBox()
        self.combo_box.setMaximumHeight(self.max_height)
        self.combo_box_content = ['frame'] + [str(num) for num in range(2, 25)+range(35, 250, 11)]
        self.combo_box.addItems(self.combo_box_content)
        self.q_widget.connect(self.combo_box, QtCore.SIGNAL("currentIndexChanged(const QString&)"), self.index_changed)

        self.push_button = QtGui.QPushButton("&Convert saved pictures to video file")
        self.push_button.setMaximumHeight(self.max_height)
        self.push_button.setToolTip('To implement from user:\n'
                                    '- derive your own Visualizer (class) from MplVisualizer\n'
                                    '- write/call your script in/through self.convert_button_clicked()  (e.g. by use of FFmpeg)\n'
                                    '- CURRENT picture path: '+self.picture_path+'\n'
                                    '- enable this button: self.push_button.setEnabled()\n'
                                    '- rewrite or remove this tooltip: self.push_button.setToolTip(\'My awesome script do ...\')'
                                    )
        self.push_button.setDisabled(True)
        self.q_widget.connect(self.push_button, QtCore.SIGNAL("clicked()"), self.convert_button_clicked)

        # arrange objects inside the dock/widget
        hbox1 = QtGui.QHBoxLayout()
        hbox1.setAlignment(QtCore.Qt.AlignBottom)
        hbox2 = QtGui.QHBoxLayout()
        hbox2.setAlignment(QtCore.Qt.AlignBottom)
        vbox = QtGui.QVBoxLayout()
        vbox.setAlignment(QtCore.Qt.AlignBottom)
        for w in [self.save_cb, self.label1, self.combo_box, self.label2, self.label3]:
            hbox1.addWidget(w)
            hbox1.setAlignment(w, QtCore.Qt.AlignLeft)
        vbox.addLayout(hbox1)
        vbox.addWidget(self.push_button)
        vbox.setAlignment(self.push_button, QtCore.Qt.AlignLeft)
        hbox2.addWidget(self.mpl_toolbar)
        hbox2.setAlignment(self.mpl_toolbar, QtCore.Qt.AlignBottom)
        hbox2.addLayout(vbox)
        hbox2.setAlignment(vbox, QtCore.Qt.AlignTop)
        self.q_layout.addLayout(hbox2)
        self.q_layout.addWidget(self.canvas)
        self.q_layout.setAlignment(QtCore.Qt.AlignVCenter)
        self.q_widget.setLayout(self.q_layout)

    def convert_button_clicked(self):
        raise NotImplementedError

    def index_changed(self):
        current_value = self.combo_box.currentText()
        if current_value == self.combo_box_content[0]:
            self.save_each = 1
        else:
            self.save_each = int(current_value)
        self.set_numerals()

    def save_cb_changed(self):
        self.frame_counter = 0
        self.file_name_counter = 0
        if self.save_cb.isChecked():
            self.time_stamp = time.ctime().replace(' ','_')+'_'
            self.time_stamps.append(self.time_stamp)

    def save_if_checked(self):
        """
        Save each self.save_each'th frame if desired.
        Should called at the end of the users self.update_scene() implementation.
        """
        if self.save_cb.isChecked():
            if self.frame_counter % self.save_each == 0:
                self.fig.savefig(self.picture_path + os.path.sep + self.time_stamp + "%04d"%self.file_name_counter,
                                 format="png",
                                 dpi=self.dpi)
                self.file_name_counter += 1
            self.frame_counter += 1

    def create_dir(self, dir_name):
        path = os.getcwd() + os.path.sep + dir_name
        if not os.path.exists(path) or not os.path.isdir(path):
            os.mkdir(path)
        return path

    def set_numerals(self):
        if self.save_each == 1:
            self.label2.setText('')
            self.label3.setText('')
        elif self.save_each % 10 == 1:
            if self.save_each % 100 == 11:
                self.label2.setText('th')
            else:
                self.label2.setText('st')
        elif self.save_each % 10 == 2:
            if self.save_each % 100 == 12:
                self.label2.setText('th')
            else:
                self.label2.setText('nd')
        elif self.save_each % 10 == 3:
            if self.save_each % 100 == 13:
                self.label2.setText('th')
            else:
                self.label2.setText('rd')
        else:
            self.label2.setText('th')
        if self.save_each != 1:
            self.label3.setText('frame')


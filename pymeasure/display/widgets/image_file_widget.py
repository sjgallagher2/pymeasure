#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import logging

from functools import partial

import matplotlib as mpl
from matplotlib import widgets as wdg
import matplotlib.image as mpimg
mpl.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg,NavigationToolbar2QT
from matplotlib.figure import Figure

from ..curves import ResultsCurve
from ..Qt import QtCore, QtWidgets
from .tab_widget import TabWidget
from .table_widget import ResultsTable

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


# A QWidget that can be added to containers
# Represents the matplotlib plotting area
class MplCanvas(FigureCanvasQTAgg):
    def __init__(self,parent=None,width=5,height=4,dpi=100):
        self.fig = Figure(figsize=(width,height),dpi=dpi)
        self.ax = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)


class ImageFileWidget(TabWidget, QtWidgets.QWidget):
    """Widget to show an image given a filename.
    """

    def __init__(self, name, fname_column, *args, parent=None, **kwargs):
        super().__init__(name, parent)
        self.fname_column = fname_column
        self._setup_ui()
        self._layout()

    def _setup_ui(self):
        self.canvas = MplCanvas(
            parent=self,
        )
        self.fig = self.canvas.fig
        self.ax = self.canvas.ax
        self.ax.axis('off')
        self.fig.canvas.draw()
        self.toolbar = NavigationToolbar2QT(self.canvas,self)

    def _layout(self):
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addWidget(self.toolbar)
        vbox.addWidget(self.canvas)
        self.setLayout(vbox)


    def new_curve(self, results, **kwargs):
        """ Create a new curve """
        return ResultsTable(results,wdg=self,**kwargs)

    def load(self, table):
        """ Add image file to widget """
        table.data_changed.connect(partial(self._update_plot,table))
        table.init()
        table.start()
        table.update_data()

    def _update_plot(self, table,r1,c1,r2,c2):
        # table.data now holds the pandas dataframe
        fname = table.data[self.fname_column].iloc[-1]  # Always most recent screenshot
        img = mpimg.imread(fname)
        self.ax.imshow(img)
        self.ax.axis('off')  # Hide axis grid lines
        self.fig.tight_layout()
        self.fig.canvas.draw()

    def remove(self, curve):
        """ Remove curve from widget """
        pass

    def set_color(self, curve, color):
        """ Set color for widget """
        pass

    def preview_widget(self, parent=None):
        """ Return a Qt widget suitable for preview during loading

        See also :class:`ResultsDialog<pymeasure.display.widgets.results_dialog.ResultsDialog>`
        If the object returned is not None, then it should have also an
        attribute `name`.
        """

        return None

    def clear_widget(self):
        """ Clear widget content

        Behaviour is widget specific and it is currently used in preview mode
        """
        return None

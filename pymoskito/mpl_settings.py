import logging
import matplotlib as mpl

from .tools import get_figure_size

_logger = logging.getLogger("mpl_settings")

orig_settings = {**mpl.rcParams}
latex_settings = {
    # change this if using contex, xetex or lualatex
    "pgf.texsystem": "pdflatex",
    # use LaTeX to write all text
    "text.usetex": True,
    'font.family': 'lmodern',
    # blank entries should cause plots to inherit fonts from the document
    # "font.serif": [],
    # "font.sans-serif": [],
    # "font.monospace": [],
    # "text.fontsize": 11,
    "legend.fontsize": 9,  # Make the legend/label fonts a little smaller
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "figure.figsize": get_figure_size(1),  # default fig size of 1\textwidth
    "lines.linewidth": 0.5,
    "axes.labelsize": 11,  # LaTeX default is 10pt font.
    "axes.linewidth": 0.5,
    "axes.unicode_minus": False,
    # subfig related
    "figure.subplot.left": 0.1,
    "figure.subplot.right": 0.95,
    "figure.subplot.bottom": 0.125,
    "figure.subplot.top": 0.95,
    # the amount of width reserved for blank space between subplots
    "figure.subplot.wspace": 0.4,
    # the amount of height reserved for white space between subplots
    "figure.subplot.hspace": 0.4,
    # Patches are graphical objects that fill 2D space, like polygons or circles
    "patch.linewidth": 0.5,
}


def enable_latex():
    _logger.info("LaTeX export enabled")
    mpl.rcParams['text.latex.preamble'].append(r'\usepackage{lmodern}'),
    mpl.rcParams['text.latex.preamble'].append(r'\usepackage{siunitx}'),
    mpl.rcParams.update(latex_settings)


def disable_latex():
    _logger.info("LaTeX export disabled")
    mpl.rcParams = orig_settings

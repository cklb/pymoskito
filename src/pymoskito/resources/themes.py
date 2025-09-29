from PyQt5.QtWidgets import QStyle, QProxyStyle
from PyQt5.QtGui import QPalette, QColor, QIcon, QPainter

# as light is the default, just remember that
lightPalette =  QPalette()

darkPalette = QPalette()

bg_color = QColor(53, 53, 53)
fg_color = QColor(239, 239, 239)
disabled_color = QColor(127, 127, 127)
ac_color1 = QColor("#00FF85")  # neon green
ac_color2 = QColor("#1E90FF")  # electric blue
ac_color3 = QColor("#FF0099")  # vivid pink

darkPalette.setColor(QPalette.ColorRole.Window, bg_color)
darkPalette.setColor(QPalette.ColorRole.WindowText, fg_color)
darkPalette.setColor(
    QPalette.ColorGroup.Disabled,
    QPalette.ColorRole.WindowText,
    disabled_color,
)
darkPalette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
darkPalette.setColor(QPalette.ColorRole.AlternateBase, bg_color)

darkPalette.setColor(QPalette.ColorRole.ToolTipBase, bg_color)
darkPalette.setColor(QPalette.ColorRole.ToolTipText, fg_color)

# text
darkPalette.setColor(QPalette.ColorRole.Text, fg_color)
darkPalette.setColor(
    QPalette.ColorGroup.Disabled,
    QPalette.ColorRole.Text,
    disabled_color,
)
darkPalette.setColor(QPalette.ColorRole.BrightText, ac_color1)
darkPalette.setColor(
    QPalette.ColorGroup.Disabled,
    QPalette.ColorRole.Highlight,
    disabled_color,
)
darkPalette.setColor(QPalette.ColorRole.HighlightedText, fg_color)
darkPalette.setColor(QPalette.ColorRole.PlaceholderText, fg_color)

# buttons
darkPalette.setColor(QPalette.ColorRole.Button, bg_color)
darkPalette.setColor(QPalette.ColorRole.ButtonText, fg_color)
darkPalette.setColor(
    QPalette.ColorGroup.Disabled,
    QPalette.ColorRole.ButtonText,
    disabled_color,
)

# special roles
darkPalette.setColor(QPalette.ColorRole.Link, ac_color1)
darkPalette.setColor(QPalette.ColorRole.Highlight, ac_color2)
darkPalette.setColor(QPalette.ColorRole.Dark, QColor(35, 35, 35, 35))
darkPalette.setColor(QPalette.ColorRole.Shadow, QColor(20, 20, 20, 20))


class LightModeStyle(QProxyStyle):
    pass


class DarkModeStyle(QProxyStyle):

    def generatedIconPixmap(self, iconMode, pixmap, opt):
        """ Drop in replacement for modal icon rendering """
        if iconMode == QIcon.Mode.Disabled:
            painter = QPainter(pixmap)
            painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
            painter.fillRect(pixmap.rect(), disabled_color)
            painter.end()
            return pixmap
        return super().generatedIconPixmap(iconMode, pixmap, opt)

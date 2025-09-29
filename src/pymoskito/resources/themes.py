from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QGuiApplication

# as light is the default, just remember that
lightPalette =  QPalette()

darkPalette = QPalette()
darkPalette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
darkPalette.setColor(QPalette.ColorRole.WindowText, QColor(Qt.GlobalColor.white))
darkPalette.setColor(
    QPalette.ColorGroup.Disabled,
    QPalette.ColorRole.WindowText,
    QColor(127, 127, 127),
)
darkPalette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
darkPalette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
darkPalette.setColor(QPalette.ColorRole.ToolTipBase, QColor(Qt.GlobalColor.white))
darkPalette.setColor(QPalette.ColorRole.ToolTipText, QColor(Qt.GlobalColor.white))
darkPalette.setColor(QPalette.ColorRole.Text, QColor(Qt.GlobalColor.white))
darkPalette.setColor(
    QPalette.ColorGroup.Disabled,
    QPalette.ColorRole.Text,
    QColor(127, 127, 127),
)
darkPalette.setColor(QPalette.ColorRole.Text, QColor(Qt.GlobalColor.white))
darkPalette.setColor(QPalette.ColorRole.Dark, QColor(35, 35, 35, 35))
darkPalette.setColor(QPalette.ColorRole.Shadow, QColor(20, 20, 20, 20))
darkPalette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
darkPalette.setColor(QPalette.ColorRole.ButtonText, QColor(Qt.GlobalColor.white))
darkPalette.setColor(QPalette.ColorRole.BrightText, QColor(Qt.GlobalColor.red))
darkPalette.setColor(
    QPalette.ColorGroup.Disabled,
    QPalette.ColorRole.ButtonText,
    QColor(127, 127, 127),
)
darkPalette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
darkPalette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
darkPalette.setColor(
    QPalette.ColorGroup.Disabled,
    QPalette.ColorRole.Highlight,
    QColor(80, 80, 80),
)
darkPalette.setColor(QPalette.ColorRole.HighlightedText, QColor(Qt.GlobalColor.white))
darkPalette.setColor(
    QPalette.ColorGroup.Disabled,
    QPalette.ColorRole.Highlight,
    QColor(127, 127, 127),
)
darkPalette.setColor(QPalette.ColorRole.PlaceholderText, QColor(Qt.GlobalColor.white))

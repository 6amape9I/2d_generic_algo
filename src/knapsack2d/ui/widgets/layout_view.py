from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QWheelEvent
from PySide6.QtWidgets import QGraphicsView


class LayoutView(QGraphicsView):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setAlignment(Qt.AlignCenter)
        self.set_pan_enabled(True)

    def set_pan_enabled(self, enabled: bool) -> None:
        self.setDragMode(QGraphicsView.ScrollHandDrag if enabled else QGraphicsView.NoDrag)

    def wheelEvent(self, event: QWheelEvent) -> None:
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor
        if event.angleDelta().y() > 0:
            self.scale(zoom_in_factor, zoom_in_factor)
        else:
            self.scale(zoom_out_factor, zoom_out_factor)
        event.accept()

    def reset_zoom(self) -> None:
        self.resetTransform()
        if self.scene() is not None:
            self.centerOn(self.scene().sceneRect().center())

    def fit_container(self) -> None:
        if self.scene() is None:
            return
        self.fitInView(self.scene().sceneRect(), Qt.KeepAspectRatio)
        self.centerOn(self.scene().sceneRect().center())
        self.setAlignment(Qt.AlignCenter)

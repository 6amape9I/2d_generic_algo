from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import QGraphicsView


class LayoutView(QGraphicsView):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setRenderHints(self.renderHints())
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
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

    def fit_container(self) -> None:
        if self.scene() is None:
            return
        self.fitInView(self.scene().sceneRect(), Qt.KeepAspectRatio)

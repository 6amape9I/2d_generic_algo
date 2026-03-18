from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QBrush, QFont, QImage, QPainter, QPen, QTransform
from PySide6.QtWidgets import QGraphicsItem, QGraphicsRectItem, QGraphicsScene

from knapsack2d.config import UiEnvConfig, load_ui_env_config
from knapsack2d.geometry import is_fully_inside_container
from knapsack2d.models import CandidatePoint, Container, DecodedLayout, Placement


class LayoutScene(QGraphicsScene):
    placement_clicked = Signal(int)
    empty_clicked = Signal()

    def __init__(self, env_config: UiEnvConfig | None = None, parent=None) -> None:
        super().__init__(parent)
        self._env_config = env_config or load_ui_env_config()
        self._placement_items: dict[int, QGraphicsRectItem] = {}
        self.setBackgroundBrush(QBrush(QColor("white")))

    def set_layout(
        self,
        layout: DecodedLayout,
        container: Container,
        *,
        show_virtual: bool = True,
        show_overflow: bool = True,
        show_labels: bool = True,
        candidate_points: list[CandidatePoint] | None = None,
        show_candidate_points: bool = False,
        selected_placement_index: int | None = None,
    ) -> None:
        self.clear()
        self._placement_items = {}

        container_item = self.addRect(
            0,
            0,
            container.width,
            container.height,
            self._pen(QColor("black"), 1.0),
            QBrush(QColor(0, 0, 0, 0)),
        )
        container_item.setData(0, "container")

        for index, placement in enumerate(layout.placements):
            inside = is_fully_inside_container(placement, container)
            if placement.is_virtual and not show_virtual:
                continue
            if not placement.is_virtual and not inside and not show_overflow:
                continue
            self._add_placement_item(
                index=index,
                placement=placement,
                inside=inside,
                show_labels=show_labels,
                is_selected=(selected_placement_index == index),
            )

        if show_candidate_points and candidate_points:
            for point in candidate_points:
                marker = self.addEllipse(
                    point.x - 0.10,
                    point.y - 0.10,
                    0.20,
                    0.20,
                    self._pen(QColor("#C26D00"), 1.0),
                    QBrush(QColor("#F5A623")),
                )
                marker.setData(0, "candidate")

        self.setSceneRect(-0.8, -0.8, container.width + 1.6, container.height + 1.6)

    def placement_items_count(self) -> int:
        return sum(
            1
            for item in self.items()
            if isinstance(item, QGraphicsRectItem) and item.data(0) == "placement"
        )

    def save_png(self, path: str | Path) -> None:
        scene_rect = self.sceneRect()
        width = max(1, int(scene_rect.width() * 40))
        height = max(1, int(scene_rect.height() * 40))
        image = QImage(width, height, QImage.Format_ARGB32)
        image.fill(Qt.white)

        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing)
        self.render(painter)
        painter.end()

        image.save(str(path), "PNG")

    def mousePressEvent(self, event) -> None:  # noqa: N802 - Qt API
        item = self.itemAt(event.scenePos(), QTransform())
        if item is not None and item.data(0) == "placement":
            index = item.data(2)
            if isinstance(index, int):
                self.placement_clicked.emit(index)
        else:
            self.empty_clicked.emit()
        super().mousePressEvent(event)

    def _add_placement_item(
        self,
        *,
        index: int,
        placement: Placement,
        inside: bool,
        show_labels: bool,
        is_selected: bool,
    ) -> None:
        if placement.is_virtual:
            pen = self._pen(QColor("#6B7280"), 0.9)
            brush = QBrush(QColor(130, 130, 130, 80))
        elif not inside:
            pen = self._pen(QColor("#B91C1C"), 1.0, Qt.DashLine)
            brush = QBrush(QColor(255, 0, 0, 85))
        else:
            pen = self._pen(QColor("#111827"), 0.85)
            brush = QBrush(QColor(55, 132, 214, 155))

        if is_selected:
            pen = self._pen(QColor("#F59E0B"), 1.6)

        rect_item = self.addRect(
            placement.x,
            placement.y,
            placement.width,
            placement.height,
            pen,
            brush,
        )
        rect_item.setData(0, "placement")
        rect_item.setData(1, placement.item_id)
        rect_item.setData(2, index)
        self._placement_items[index] = rect_item

        rect_item.setToolTip(
            "\n".join(
                [
                    f"item_id: {placement.item_id}",
                    f"x: {placement.x}",
                    f"y: {placement.y}",
                    f"w: {placement.width}",
                    f"h: {placement.height}",
                    f"rotated: {placement.rotated}",
                    f"value: {placement.value}",
                    f"is_virtual: {placement.is_virtual}",
                ]
            )
        )

        if show_labels and placement.item_id is not None:
            self._add_label(placement)

    def _add_label(self, placement: Placement) -> None:
        if min(placement.width, placement.height) < 1.7:
            return

        pixel_size = max(
            self._env_config.min_label_pixel_size,
            min(
                self._env_config.max_label_pixel_size,
                min(placement.width, placement.height) * 1.85,
            ),
        )

        text_item = self.addSimpleText(placement.item_id)
        font = QFont(self._env_config.font_family)
        font.setPixelSize(max(1, int(round(pixel_size))))
        text_item.setFont(font)
        text_item.setBrush(QBrush(QColor("#111827")))
        text_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations, True)
        text_item.setData(0, "label")
        text_item.setZValue(3)
        text_item.setPos(
            placement.x + self._env_config.label_padding,
            placement.y + self._env_config.label_padding,
        )

    def _pen(self, color: QColor, width: float, style: Qt.PenStyle = Qt.SolidLine) -> QPen:
        pen = QPen(color, width, style)
        pen.setCosmetic(True)
        return pen

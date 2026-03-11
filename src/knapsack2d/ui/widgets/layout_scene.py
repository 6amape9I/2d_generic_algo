from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QBrush, QImage, QPainter, QPen, QTransform
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsScene, QGraphicsSimpleTextItem

from knapsack2d.geometry import is_fully_inside_container
from knapsack2d.models import CandidatePoint, Container, DecodedLayout, Placement


class LayoutScene(QGraphicsScene):
    placement_clicked = Signal(int)
    empty_clicked = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._placement_items: dict[int, QGraphicsRectItem] = {}

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
            QPen(QColor("black"), 1.5),
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
                marker = self.addRect(
                    point.x - 0.08,
                    point.y - 0.08,
                    0.16,
                    0.16,
                    QPen(QColor("orange"), 1.2),
                    QBrush(QColor("orange")),
                )
                marker.setData(0, "candidate")

        self.setSceneRect(-1, -1, container.width + 2, container.height + 2)

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
            pen = QPen(QColor("gray"), 1)
            brush = QBrush(QColor(130, 130, 130, 90))
        elif not inside:
            pen = QPen(QColor("red"), 1.4, Qt.DashLine)
            brush = QBrush(QColor(255, 0, 0, 95))
        else:
            pen = QPen(QColor("black"), 1)
            brush = QBrush(QColor(100, 149, 237, 150))

        if is_selected:
            pen = QPen(QColor("yellow"), 2.4)

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
        rect_item.setData(
            3,
            {
                "item_id": placement.item_id,
                "x": placement.x,
                "y": placement.y,
                "w": placement.width,
                "h": placement.height,
                "rotated": placement.rotated,
                "value": placement.value,
                "is_virtual": placement.is_virtual,
                "inside_container": inside,
            },
        )
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
            text = self.addSimpleText(placement.item_id)
            text.setData(0, "label")
            text.setPos(placement.x + 0.1, placement.y + 0.1)
            if isinstance(text, QGraphicsSimpleTextItem):
                text.setBrush(QBrush(QColor("black")))

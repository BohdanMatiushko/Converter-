"""Graphical user interface for the Electric Units Converter."""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFileDialog,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
)

from converter import (
    ConversionError,
    DEFAULT_FROM_UNIT,
    DEFAULT_TO_UNIT,
    convert_raw_value,
    get_available_units,
)


VALUE_COLUMN = 0
FROM_COLUMN = 1
TO_COLUMN = 2
RESULT_COLUMN = 3
STATUS_COLUMN = 4

COLUMN_HEADERS = ["Значення", "Звідки", "Куди", "Результат", "Статус"]

DEFAULT_ROW_COUNT = 5


class ConverterMainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self._autoconvert_enabled = True
        self._available_units = get_available_units()

        self.setWindowTitle("Конвертер електричних величин")
        self.setMinimumSize(QSize(980, 520))
        self.resize(1080, 620)

        self.table = QTableWidget()
        self.status_bar = QStatusBar()
        self.info_label = QLabel("Введіть значення та виберіть одиниці")
        self.convert_button = QPushButton("Конвертувати")
        self.clear_button = QPushButton("Очистити")
        self.add_row_button = QPushButton("Додати рядок")
        self.remove_row_button = QPushButton("Видалити рядок")
        self.export_button = QPushButton("Експорт у Excel")

        self._build_ui()
        self._apply_styles()
        self._connect_signals()
        self._populate_initial_rows(DEFAULT_ROW_COUNT)

    def _build_ui(self) -> None:
        """Create and arrange widgets."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(16, 16, 16, 12)
        main_layout.setSpacing(12)
        central_widget.setLayout(main_layout)

        title_label = QLabel("Конвертер електричних величин")
        title_label.setObjectName("titleLabel")

        subtitle_label = QLabel(
            "Підтримка одиночної, масової та автоматичної конвертації з експортом у Excel"
        )
        subtitle_label.setObjectName("subtitleLabel")

        main_layout.addWidget(title_label)
        main_layout.addWidget(subtitle_label)

        self.table.setColumnCount(len(COLUMN_HEADERS))
        self.table.setHorizontalHeaderLabels(COLUMN_HEADERS)
        self.table.setAlternatingRowColors(False)
        self.table.setShowGrid(True)
        self.table.setGridStyle(Qt.PenStyle.SolidLine)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.AllEditTriggers)
        self.table.verticalHeader().setVisible(True)
        self.table.verticalHeader().setDefaultSectionSize(34)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(VALUE_COLUMN, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(FROM_COLUMN, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(TO_COLUMN, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        main_layout.addWidget(self.table)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        for button in (
            self.add_row_button,
            self.remove_row_button,
            self.clear_button,
            self.convert_button,
            self.export_button,
        ):
            button.setMinimumHeight(38)
            button_layout.addWidget(button)

        button_layout.addStretch(1)
        main_layout.addLayout(button_layout)

        self.info_label.setObjectName("infoLabel")
        main_layout.addWidget(self.info_label)

        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готово до роботи")

    def _apply_styles(self) -> None:
        """Apply a light theme and Excel-like table styling."""
        self.setStyleSheet(
            """
            QMainWindow {
                background: #f6f8fb;
            }

            QLabel#titleLabel {
                font-size: 22px;
                font-weight: 700;
                color: #1f2937;
            }

            QLabel#subtitleLabel {
                font-size: 12px;
                color: #6b7280;
                margin-bottom: 4px;
            }

            QLabel#infoLabel {
                font-size: 12px;
                color: #4b5563;
                padding: 2px 0;
            }

            QPushButton {
                background: #ffffff;
                border: 1px solid #cfd8e3;
                border-radius: 8px;
                padding: 8px 14px;
                font-size: 13px;
                color: #1f2937;
            }

            QPushButton:hover {
                background: #eef4fb;
                border-color: #93b4da;
            }

            QPushButton:pressed {
                background: #e3edf8;
            }

            QTableWidget {
                background: #ffffff;
                border: 1px solid #cfd8e3;
                border-radius: 8px;
                gridline-color: #d7dce3;
                font-size: 13px;
                color: #111827;
                selection-background-color: #dbeafe;
                selection-color: #111827;
            }

            QHeaderView::section {
                background: #eef3f9;
                color: #1f2937;
                padding: 8px;
                border: 1px solid #d7dce3;
                font-weight: 600;
            }

            QComboBox {
                 border: 1px solid #cfd8e3;
                 border-radius: 6px;
                 padding: 4px 8px;
                 background: #ffffff;
                 color: #111827;
                 min-height: 24px;
                 min-width: 90px;
            }

            QComboBox:hover {
                border-color: #93b4da;
            }

            QComboBox QAbstractItemView {
                background: #ffffff;
                color: #111827;
                selection-background-color: #dbeafe;
                selection-color: #111827;
            }
            """
        )

    def _connect_signals(self) -> None:
        """Connect widget signals."""
        self.add_row_button.clicked.connect(self.add_row)
        self.remove_row_button.clicked.connect(self.remove_selected_row)
        self.clear_button.clicked.connect(self.clear_rows)
        self.convert_button.clicked.connect(self.convert_all_rows)
        self.export_button.clicked.connect(self.export_rows)
        self.table.itemChanged.connect(self._on_item_changed)

    def _populate_initial_rows(self, count: int) -> None:
        """Create initial table rows."""
        for _ in range(count):
            self.add_row()

    def add_row(self) -> None:
        """Add a new row with default controls."""
        self._autoconvert_enabled = False

        row = self.table.rowCount()
        self.table.insertRow(row)

        value_item = QTableWidgetItem("")
        value_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.table.setItem(row, VALUE_COLUMN, value_item)

        from_combo = self._create_unit_combo(DEFAULT_FROM_UNIT)
        to_combo = self._create_unit_combo(DEFAULT_TO_UNIT)

        self.table.setCellWidget(row, FROM_COLUMN, from_combo)
        self.table.setCellWidget(row, TO_COLUMN, to_combo)

        result_item = QTableWidgetItem("")
        result_item.setFlags(result_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        result_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.table.setItem(row, RESULT_COLUMN, result_item)

        status_item = QTableWidgetItem("")
        status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        status_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.table.setItem(row, STATUS_COLUMN, status_item)

        self._set_row_state_default(row)

        self._autoconvert_enabled = True
        self.status_bar.showMessage(f"Додано рядок {row + 1}", 3000)

    def remove_selected_row(self) -> None:
        """Remove the selected row."""
        current_row = self.table.currentRow()
        if current_row < 0:
            self.status_bar.showMessage("Рядок не вибрано", 3000)
            return

        self.table.removeRow(current_row)
        self.status_bar.showMessage("Рядок видалено", 3000)

        if self.table.rowCount() == 0:
            self.add_row()

    def clear_rows(self) -> None:
        """Clear all row values and reset defaults."""
        self._autoconvert_enabled = False

        for row in range(self.table.rowCount()):
            value_item = self.table.item(row, VALUE_COLUMN)
            result_item = self.table.item(row, RESULT_COLUMN)
            status_item = self.table.item(row, STATUS_COLUMN)

            if value_item is not None:
                value_item.setText("")
            if result_item is not None:
                result_item.setText("")
            if status_item is not None:
                status_item.setText("")

            from_combo = self._get_combo(row, FROM_COLUMN)
            to_combo = self._get_combo(row, TO_COLUMN)

            if from_combo is not None:
                from_combo.setCurrentText(DEFAULT_FROM_UNIT)
            if to_combo is not None:
                to_combo.setCurrentText(DEFAULT_TO_UNIT)

            self._set_row_state_default(row)

        self._autoconvert_enabled = True
        self.info_label.setText("Таблицю очищено")
        self.status_bar.showMessage("Усі рядки очищено", 3000)

    def convert_all_rows(self) -> None:
        """Convert all rows manually."""
        success_count = 0

        for row in range(self.table.rowCount()):
            if self._convert_row(row):
                success_count += 1

        self.info_label.setText(f"Оброблено рядків: {self.table.rowCount()}, успішно: {success_count}")
        self.status_bar.showMessage("Конвертацію завершено", 4000)

    def export_rows(self) -> None:
        """Export table data to an Excel file."""
        rows = self._collect_rows_for_export()

        meaningful_rows = [row for row in rows if any(cell.strip() for cell in row)]
        if not meaningful_rows:
            self._show_warning("Немає даних для експорту")
            self.status_bar.showMessage("Експорт скасовано: немає даних", 4000)
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Зберегти Excel-файл",
            "electric_units_conversion.xlsx",
            "Excel Files (*.xlsx)",
        )

        if not file_path:
            self.status_bar.showMessage("Експорт скасовано", 3000)
            return

        if not file_path.lower().endswith(".xlsx"):
            file_path += ".xlsx"

        try:
            from excel_export import export_to_excel
            export_to_excel(file_path, meaningful_rows)
        except ValueError as exc:
            self._show_warning(str(exc))
            self.status_bar.showMessage(str(exc), 5000)
            return
        except Exception as exc:
            self._show_error(f"Не вдалося експортувати файл:\n{exc}")
            self.status_bar.showMessage("Помилка експорту", 5000)
            return

        self.status_bar.showMessage(f"Експорт виконано: {file_path}", 5000)
        self.info_label.setText("Експорт у Excel виконано успішно")

    def _collect_rows_for_export(self) -> list[list[str]]:
        """Collect row data from the table."""
        rows: list[list[str]] = []

        for row in range(self.table.rowCount()):
            value_text = self._get_item_text(row, VALUE_COLUMN)
            from_text = self._get_combo_text(row, FROM_COLUMN)
            to_text = self._get_combo_text(row, TO_COLUMN)
            result_text = self._get_item_text(row, RESULT_COLUMN)
            status_text = self._get_item_text(row, STATUS_COLUMN)

            rows.append([value_text, from_text, to_text, result_text, status_text])

        return rows

    def _create_unit_combo(self, current_unit: str) -> QComboBox:
        """Create a combo box for unit selection."""
        combo = QComboBox()
        combo.addItems(self._available_units)
        combo.setCurrentText(current_unit)
        combo.currentIndexChanged.connect(self._on_combo_changed)
        return combo

    def _on_item_changed(self, item: QTableWidgetItem) -> None:
        """Handle edits in editable cells."""
        if not self._autoconvert_enabled:
            return

        if item.column() == VALUE_COLUMN:
            self._convert_row(item.row())

    def _on_combo_changed(self) -> None:
        """Handle changes in unit combo boxes."""
        if not self._autoconvert_enabled:
            return

        sender = self.sender()
        if sender is None:
            return

        for row in range(self.table.rowCount()):
            if self.table.cellWidget(row, FROM_COLUMN) is sender or self.table.cellWidget(row, TO_COLUMN) is sender:
                self._convert_row(row)
                break

    def _convert_row(self, row: int) -> bool:
        """
        Convert a single row.

        Returns:
            True if conversion was successful, otherwise False.
        """
        value_text = self._get_item_text(row, VALUE_COLUMN)
        from_unit = self._get_combo_text(row, FROM_COLUMN)
        to_unit = self._get_combo_text(row, TO_COLUMN)

        result_item = self.table.item(row, RESULT_COLUMN)
        status_item = self.table.item(row, STATUS_COLUMN)

        if result_item is None or status_item is None:
            return False

        if not value_text.strip():
            result_item.setText("")
            status_item.setText("")
            self._set_row_state_default(row)
            return False

        try:
            result = convert_raw_value(value_text, from_unit, to_unit)
        except ConversionError as exc:
            result_item.setText("")
            status_item.setText(str(exc))
            self._set_row_state_error(row)
            self.status_bar.showMessage(str(exc), 4000)
            return False

        result_item.setText(result)
        status_item.setText("OK")
        self._set_row_state_ok(row)
        self.status_bar.showMessage(f"Рядок {row + 1} конвертовано", 2000)
        return True

    def _set_row_state_default(self, row: int) -> None:
        """Reset row colors to neutral."""
        neutral = QColor("#ffffff")
        self._paint_row(row, neutral)

    def _set_row_state_ok(self, row: int) -> None:
        """Color row as valid."""
        valid = QColor("#f8fbff")
        self._paint_row(row, valid)

    def _set_row_state_error(self, row: int) -> None:
        """Color row as invalid."""
        error = QColor("#fde8e8")
        self._paint_row(row, error)

    def _paint_row(self, row: int, color: QColor) -> None:
        """Apply background color to row items and combos."""
        for column in (VALUE_COLUMN, RESULT_COLUMN, STATUS_COLUMN):
            item = self.table.item(row, column)
            if item is not None:
                item.setBackground(color)

        for column in (FROM_COLUMN, TO_COLUMN):
            combo = self._get_combo(row, column)
            if combo is not None:
                combo.setStyleSheet(
                    f"""
                    QComboBox {{
                        background: {color.name()};
                        border: 1px solid #cfd8e3;
                        border-radius: 6px;
                        padding: 4px 8px;
                        min-height: 24px;
                    }}
                    """
                )

    def _get_item_text(self, row: int, column: int) -> str:
        """Return text from a table item."""
        item = self.table.item(row, column)
        return item.text().strip() if item is not None else ""

    def _get_combo(self, row: int, column: int) -> Optional[QComboBox]:
        """Return combo box from a cell."""
        widget = self.table.cellWidget(row, column)
        return widget if isinstance(widget, QComboBox) else None

    def _get_combo_text(self, row: int, column: int) -> str:
        """Return current text of combo box."""
        combo = self._get_combo(row, column)
        return combo.currentText().strip() if combo is not None else ""

    def _show_warning(self, message: str) -> None:
        """Show warning dialog."""
        QMessageBox.warning(self, "Попередження", message)

    def _show_error(self, message: str) -> None:
        """Show error dialog."""
        QMessageBox.critical(self, "Помилка", message)
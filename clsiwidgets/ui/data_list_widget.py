import json
from pathlib import Path

import ipywidgets

from clsiwidgets.ui.base_widget import BaseWidget


class DataListWidget(ipywidgets.VBox, BaseWidget):
    COLUMNS = ("#", "cfg name", "Label", "Default", "Range")
    HEADER_BG = "#e8eef4"
    ROW_BG = ("#ffffff", "#f7f9fb")
    CELL_BORDER = "1px solid #ccc"

    def __init__(self, data_path: Path):
        super().__init__()

        self.data = json.loads((data_path / "dataset.json").read_text(encoding="utf-8"))

        self.data_keys = list(self.data.keys())

        self._intro = ipywidgets.HTML(
            "<h3 style='margin:8px 0 4px 0;'>Parameter sweep</h3>"
            "<h5 style='margin:6px 0 4px 0;'>Choose Parameter and Values</h5>"
            "<p style='font-size:12px; margin:2px 0 6px 0;'>"
            "Select <b>one</b> parameter from the list below and define your values to sweep."
            "</p>"
        )
        self.data_grid = ipywidgets.GridBox(
            layout=ipywidgets.Layout(
                grid_template_columns=f"repeat({len(self.COLUMNS)}, auto)",
                border_top=self.CELL_BORDER,
                border_left=self.CELL_BORDER,
                margin="0 0 8px 0",
            )
        )
        self._render()

        self.output = ipywidgets.Output()
        self.children = [self._intro, self.data_grid, self.output]

    def _format_value(self, value, value_type: str):
        if value_type == "int":
            return str(int(value))
        return str(value)

    def _render(self):
        header = [self._get_cell(c, self.HEADER_BG, bold=True) for c in self.COLUMNS]

        cells = []
        for i, (name, info) in enumerate(self.data.items()):
            background = self.ROW_BG[i % 2]
            value_type = info.get("type", "float")
            cells += [
                self._get_cell(str(i + 1), background),
                self._get_cell(name, background, monospace=True),
                self._get_cell(info["label"], background),
                self._get_cell(self._format_value(info["default"], value_type), background),
                self._get_cell(
                    f"{self._format_value(info['min'], value_type)} – "
                    f"{self._format_value(info['max'], value_type)}",
                    background,
                ),
            ]

        self.data_grid.children = header + cells

    def _get_cell(
        self, value: str, background: str, bold: bool = False, monospace: bool = False
    ) -> ipywidgets.Label:
        style = {"background": background, "font_weight": "bold" if bold else "normal"}
        if monospace:
            style["font_family"] = "monospace"
        return ipywidgets.Label(
            value,
            style=style,
            layout=ipywidgets.Layout(
                margin="0",
                padding="2px 6px",
                border_right=self.CELL_BORDER,
                border_bottom=self.CELL_BORDER,
            ),
        )

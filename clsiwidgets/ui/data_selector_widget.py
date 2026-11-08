import json
from importlib import resources

import ipywidgets

from clsiwidgets.ui.base_widget import BaseWidget


class DataSelectorWidget(ipywidgets.VBox, BaseWidget):
    def __init__(
        self,
        data_path: dict,
        title: str = "Selected dataset",
    ):
        super().__init__()

        self.title = title

        with (
            resources.files("clsiwidgets.data")
            .joinpath("dataset.json")
            .open("r", encoding="utf-8") as f
        ):
            self.data = json.load(f)

        self.data_keys = list(self.data.keys())
        self.selected_key = self.data_keys[0]  # default option
        self.selected_data = self.data[self.selected_key]

        self.dropdown = ipywidgets.Dropdown(
            options=self.data_keys,
            description=self.title,
            style={"description_width": "initial"},
            value=self.selected_key,
        )
        self.dropdown.observe(self._on_dropdown_change, names="value")
        self.label_param_info = ipywidgets.HTML(value="")
        self._set_label_param_info()

        self.output = ipywidgets.Output()
        self.children = [self.dropdown, self.label_param_info, self.output]

    def _on_dropdown_change(self, change):
        self.selected_key = change["new"]
        self.selected_data = self.data[self.selected_key]
        self._set_label_param_info()

    def _set_label_param_info(self):
        self.label_param_info.value = (
            f"<div style='padding:6px 10px; background:#f0f4f8; "
            f"border-left:3px solid #4a7aa8; font-size:12px; margin:4px 0;'>"
            f"<b>{self.selected_data['label']}</b><br>"
            f"Default: <code>{self.selected_data['default']}</code> &nbsp;|&nbsp; "
            f"Range: <code>[{self.selected_data['min']}, {self.selected_data['max']}]</code> &nbsp;|&nbsp; "
            f"Type: <code>{self.selected_data['type']}</code><br>"
            f"<i>{self.selected_data['desc']}</i>"
            f"</div>"
        )

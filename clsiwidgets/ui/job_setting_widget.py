from datetime import datetime

import ipywidgets

from clsiwidgets.core.enums.job_enums import JobMode
from clsiwidgets.ui.base_widget import BaseWidget
from clsiwidgets.ui.cls_sa_widget import CLSSAWidget


class JobSettingWidget(ipywidgets.VBox, BaseWidget):
    def __init__(self, data_path, transfer_path, title: str = "Run simulation", default_value: str | None = None):
        super().__init__()

        self._data_path = data_path
        self._transfer_path = transfer_path
        self._widget_title = title

        self._header = ipywidgets.HTML(value=f"<h3>{self._widget_title}</h3>")

        self._mode_widget = ipywidgets.Dropdown(
            options=[m.value for m in JobMode],
            description="Select mode:",
            value=JobMode.OWN_USER.value,
        )
        self._mode_widget.observe(self._on_mode_change, names="value")

        self._cls_sa_widget = CLSSAWidget()
        self._cls_sa_widget.hide()  # hidden for default OWN_USER mode

        self._job_title_widget = ipywidgets.Text(
            value='',
            description="Job title:",
            placeholder=f"TGP_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        )

        self._input_values = ""
        self._input_widget = ipywidgets.Text(
            value=self._input_values,
            description="Values (comma-sep): ",
            placeholder=default_value or 'Put values',
            style={"description_width": "initial"},
        )

        self._input_widget.observe(self._on_value_change, names="value")

        self.output = ipywidgets.Output()
        self.children = [
            self._header,
            self._mode_widget,
            self._cls_sa_widget,
            self._job_title_widget,
            self._input_widget,
            self.output,
        ]

    def _on_mode_change(self, change):
        if JobMode(self._mode_widget.value) == JobMode.CLS_SA:
            self._cls_sa_widget.show()
        else:
            self._cls_sa_widget.hide()

    def _on_value_change(self, change):
        self._input_values = change["new"]

    def get_input_values(self) -> str:
        if not self._input_values:
            raise RuntimeError('Put values')
        return str(self._input_values)

    def get_title(self) -> str:
        return str(self._job_title_widget.value or self._job_title_widget.placeholder)

    def get_mode(self) -> JobMode:
        return JobMode(self._mode_widget.value) or JobMode.OWN_USER

    def get_sa_project(self) -> str:
        return self._cls_sa_widget.get_project()

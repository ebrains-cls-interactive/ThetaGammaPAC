import ipywidgets

from clsiwidgets.core.services.cls_sa import CLSSAService
from clsiwidgets.ui.base_widget import BaseWidget


class CLSSAWidget(ipywidgets.VBox, BaseWidget):
    def __init__(self):
        super().__init__()

        # self._hpc_list = CLSSAService.get_hpc()
        # self._hpc_selector_widget = ipywidgets.Dropdown(
        #     options=self._hpc_list,
        #     description='Select CLS-SA hpc:',
        #     style={"description_width": "initial"},
        # )

        self._project_list = CLSSAService.get_project()
        self._selected_project = self._project_list[0]
        self._project_selector_widget = ipywidgets.Dropdown(
            options=self._project_list,
            description="Select CLS-SA project:",
            style={"description_width": "initial"},
            value=self._selected_project
        )
        self._project_selector_widget.observe(self._on_project_change)

        self.output = ipywidgets.Output()
        # self.children = [self._hpc_selector_widget, self._project_selector_widget, self.output]
        self.children = [self._project_selector_widget, self.output]

    def show(self):
        self.layout.display = ""

    def hide(self):
        self.layout.display = "none"

    def _on_project_change(self, change):
        self._selected_project = change['new']

    def get_project(self):
        return self._selected_project

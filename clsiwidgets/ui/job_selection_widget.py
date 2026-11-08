
import ipywidgets

from clsiwidgets.core.models.job import Job
from clsiwidgets.ui.base_widget import BaseWidget


class JobSelectionWidget(ipywidgets.VBox, BaseWidget):

    def __init__(self, data: list[Job]):
        super().__init__()

        self.data = data
        self.selected_jobs: list[Job] = []

        # Dropdown with the available jobs: label shown, Job object as value
        self.dropdown = ipywidgets.Dropdown(
            options=self.data.copy(),
            description='Add job:',
            style={"description_width": "initial"},
        )

        self.add_button = ipywidgets.Button(
            description='Add',
            button_style='primary',
            icon='plus',
        )
        self.add_button.on_click(self._on_add_clicked)

        self.clear_button = ipywidgets.Button(
            description='Clear',
            button_style='danger',
            icon='trash',
        )
        self.clear_button.on_click(self._on_clear_clicked)

        self.output = ipywidgets.Output(layout=ipywidgets.Layout(margin='10px 0 0 0'))

        self.children = [
            ipywidgets.HBox([self.dropdown, self.add_button, self.clear_button]),
            # self.selected_list,
            self.output,
        ]
        self.layout = ipywidgets.Layout(margin='20px 0 20px 0')

        with self.output:
            print('Selected jobs: []')

    def _on_clear_clicked(self, _button):
        self.selected_jobs.clear()
        self.dropdown.options = self.data.copy()
        self.output.clear_output()

    def _on_add_clicked(self, _button):
        job = self.dropdown.value
        if job is None or job in self.selected_jobs:
            return
        self.selected_jobs.append(job)
        updated_job_list = list(self.dropdown.options)
        updated_job_list.remove(job)
        self.dropdown.options = updated_job_list
        self.output.clear_output()
        with self.output:
            print('Selected jobs: [')
            for job in self.selected_jobs:
                print(f"    {job.id} - {job.title} - {job.execution},")
            print(']')

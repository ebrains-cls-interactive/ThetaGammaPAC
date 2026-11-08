from __future__ import annotations

import ipywidgets

from clsiwidgets.core.models.job import Job
from clsiwidgets.ui.base_widget import BaseWidget


class JobListWidget(ipywidgets.VBox, BaseWidget):
    COLUMNS = ('ID', 'Title', 'Execution', 'Status', 'Submitted on', 'Service', 'HPC', 'Downloaded')
    HEADER_BG = "#e8eef4"
    ROW_BG = ("#ffffff", "#f7f9fb")
    CELL_BORDER = "1px solid #ccc"

    def __init__(self, data: list[Job] | None = None, title: str = 'Jobs list', empty_message: str = 'No jobs yet. Submit a job to see it listed here.'):
        super().__init__()

        self._title = ipywidgets.HTML(
            f"<h3>{title}</h3>"
        )

        self.data = data or []
        self._job_list = ipywidgets.GridBox(
            layout=ipywidgets.Layout(
                grid_template_columns=f"repeat({len(self.COLUMNS)}, auto)",
                border_top=self.CELL_BORDER,
                border_left=self.CELL_BORDER,
            )
        )
        self._empty_message = ipywidgets.HTML(
            f"<i>{empty_message}</i>"
        )
        self._render()

        self.output = ipywidgets.Output()
        self.children = [self._empty_message, self._title, self._job_list, self.output]

    def set_jobs(self, jobs: list[Job] | None):
        """Replace the jobs shown in the table."""
        self.data = list(jobs or [])
        self._render()

    def _render(self):
        if self.data:
            self._empty_message.layout.display = "none"
            self._title.layout.display = ""
        else:
            self._empty_message.layout.display = ""
            self._title.layout.display = "none"

        self._job_list.layout.display = "" if self.data else "none"
        header = [self._get_cell(c, self.HEADER_BG, bold=True) for c in self.COLUMNS]
        cells = [
            self._get_cell(v, self.ROW_BG[i % 2])
            for i, job in enumerate(self.data)
            for v in self._get_row(job)
        ]
        self._job_list.children = header + cells

    def _get_cell(self, value: str, background: str, bold: bool = False) -> ipywidgets.Label:
        return ipywidgets.Label(
            value,
            style={"background": background, "font_weight": "bold" if bold else "normal"},
            layout=ipywidgets.Layout(
                margin="0",
                padding="2px 6px",
                border_right=self.CELL_BORDER,
                border_bottom=self.CELL_BORDER,
            ),
        )

    def _get_row(self, job: Job) -> list[str]:

        return [
            str(job.id),
            job.title,
            job.execution,
            job.status,
            job.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            job.service,
            job.hpc,
            job.downloaded,
        ]

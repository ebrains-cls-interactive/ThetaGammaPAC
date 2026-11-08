


import json
import os
from collections import OrderedDict

import ipywidgets
from dotenv import load_dotenv

from clsiwidgets.core.job_manager import JobManager
from clsiwidgets.ui.base_widget import BaseWidget
from clsiwidgets.ui.data_list_widget import DataListWidget
from clsiwidgets.ui.data_selector_widget import DataSelectorWidget
from clsiwidgets.ui.job_list_widget import JobListWidget
from clsiwidgets.ui.job_selection_widget import JobSelectionWidget
from clsiwidgets.ui.job_setting_widget import JobSettingWidget
from clsiwidgets.ui.level_four_analysis_widget import LevelFourAnalysisWidget
from clsiwidgets.ui.level_one_analysis_widget import LevelOneAnalysisWidget
from clsiwidgets.ui.level_three_analysis_widget import LevelThreeAnalysisWidget
from clsiwidgets.ui.level_two_analysis_widget import LevelTwoAnalysisWidget
from clsiwidgets.ui.utils.print_func import print_error, print_msg, print_success


class TGPSimulation(ipywidgets.VBox, BaseWidget):

    def __init__(self, paths: dict, **kwargs):

        load_dotenv(paths["env_path"])

        data_path = paths["data_path"]
        results_path = paths["results_path"]

        self.job_manager = JobManager(data_path=data_path, results_path=results_path)

        title = ipywidgets.HTML(
            "<h1 style='margin-left: 0px;'>CA1 Microcircuit Simulation</h1>"
        )

        self.data_box = DataListWidget(data_path)
        self.data_selector = DataSelectorWidget(data_path)

        data_section = ipywidgets.VBox([self.data_box, self.data_selector])

        self.job_settings = JobSettingWidget(data_path)

        self.submit_sweep_button = ipywidgets.Button(
            description="Submit sweep",
            button_style="success",
            icon="check",
        )
        self.submit_sweep_button.on_click(self._submit_sweep_callback)

        self.check_jobs_button = ipywidgets.Button(
            description='Check jobs',
            button_style='info',
            icon='search'
        )
        self.check_jobs_button.on_click(self._check_jobs_callback)

        self.fetch_results_button = ipywidgets.Button(
            description="Fetch results",
            button_style='warning',
            icon="download",
            disabled=True
        )
        self.fetch_results_button.on_click(self._fetch_results_callback)

        if all(j.downloaded == 'Yes' for j in self.job_manager.jobs):
            self.fetch_results_button.disabled = True
        else:
            self.fetch_results_button.disabled = False

        job_buttons_row = ipywidgets.HBox([
            self.submit_sweep_button,
            self.check_jobs_button,
            self.fetch_results_button,
        ], layout=ipywidgets.Layout(margin='20px 0 0 0'))
        self.jobs_list = JobListWidget(data=self.job_manager.jobs)

        self.job_section_output = ipywidgets.Output()

        jobs_section = ipywidgets.VBox(
            [self.job_settings, job_buttons_row, self.job_section_output, self.jobs_list]
        )

        super().__init__(
            [title, data_section, jobs_section],
            layout=self.DEFAULT_BORDER,
        )       # type: ignore

    def _submit_sweep_callback(self, button):
        self.submit_sweep_button.disabled = True
        self.check_jobs_button.disabled = True
        job_title = self.job_settings.get_title()
        print_msg(self.job_section_output, f'Submitting job {job_title}')
        try:
            self.job_manager.submit_job(
                mode=self.job_settings.get_mode(),
                job_title=job_title,
                dataset_name=self.data_selector.selected_key,
                dataset=self.data_selector.selected_data,
                input_values=self.job_settings.get_input_values(),
                sa_project=self.job_settings.get_sa_project(),
            )
            print_success(self.job_section_output, 'Job submitted correctly')

            # update job list
            self.jobs_list.set_jobs(self.job_manager.jobs)

        except Exception as err:
            print_error(self.job_section_output, str(err))

        finally:
            self.submit_sweep_button.disabled = False
            self.check_jobs_button.disabled = False

    def _check_jobs_callback(self, button):
        button.disabled = True
        self.job_section_output.clear_output()
        print_msg(self.job_section_output, 'Fetching jobs...')
        try:
            jobs = self.job_manager.fetch_jobs()
            self.jobs_list.set_jobs(jobs)
            self.job_section_output.clear_output()

        except Exception as err:
            print_error(self.job_section_output, str(err))

        finally:
            button.disabled = False

    def _fetch_results_callback(self, button):
        try:
            button.disabled = True
            for job in self.job_manager.jobs:
                if job.status != 'SUCCESSFUL' or job.downloaded != 'No':
                    continue

                print_msg(self.job_section_output, f'Downloading {job.id} results...')
                self.job_manager.fetch_results(job)

                # update job list
                self.jobs_list.set_jobs(self.job_manager.jobs)

                self.job_section_output.clear_output()

        except Exception as err:
            print_error(self.job_section_output, str(err))
            button.disabled = False


class TGPAnalysis(ipywidgets.VBox, BaseWidget):

    def __init__(self, paths: dict, **kwargs):

        self.results_path = paths['results_path']
        self.data_path = paths['data_path']

        self.title_widget = ipywidgets.HTML(value="<h3>Theta Gamma PAC analysis</h3>")
        self.description_widget = ipywidgets.HTML(value="Select one or more jobs to analyse.")
        self.header_section = ipywidgets.VBox([self.title_widget, self.description_widget])

        self.run_analysis_button = ipywidgets.Button(
            description="Run analysis and show results",
            button_style="primary",
            icon="check",
        )
        self.run_analysis_button.on_click(self._run_analysis_button_callback)

        self.clear_analysis_button = ipywidgets.Button(
            description='Clear analysis plots',
            button_style='danger',
            icon='trash',
        )
        self.clear_analysis_button.on_click(self._clear_analysis_button_callback)

        button_section = ipywidgets.HBox([self.run_analysis_button, self.clear_analysis_button])

        self.job_manager = JobManager(self.data_path, self.results_path)
        self.job_list_widget = JobListWidget(data=self.job_manager.downloaded_jobs, empty_message='No job results found. Download job results to see it listed here.')
        self.job_selection_widget = JobSelectionWidget(data=self.job_manager.downloaded_jobs)

        self.settings_section_output = ipywidgets.Output()
        self.settings_section = ipywidgets.VBox([self.job_list_widget, self.job_selection_widget, button_section, self.settings_section_output])

        self.level_one_analysis_widget = LevelOneAnalysisWidget()
        self.level_two_analysis_widget = LevelTwoAnalysisWidget()
        self.level_three_analysis_widget = LevelThreeAnalysisWidget()
        self.level_four_analysis_widget = LevelFourAnalysisWidget()
        self.level_widgets = [
            self.level_one_analysis_widget,
            self.level_two_analysis_widget,
            self.level_three_analysis_widget,
            self.level_four_analysis_widget,
        ]

        self.analysis_section_output = ipywidgets.Output()
        self.analysis_section = ipywidgets.VBox([self.analysis_section_output, *self.level_widgets])

        super().__init__(
            [self.header_section, self.settings_section, self.analysis_section],
            layout=self.DEFAULT_BORDER,
        )       # type: ignore

    def _run_analysis_button_callback(self, button):
        self.analysis_section_output.clear_output()
        data = {}

        try:
            for job in self.job_selection_widget.selected_jobs:
                job_results_dir = os.path.join(self.results_path, job.id)
                json_files = sorted(f for f in os.listdir(job_results_dir) if f.endswith('_reduced.json'))
                if not json_files:
                    print_error(self.analysis_section_output, f'⚠️ No reduced.json file found in {job_results_dir}', True)
                    continue
                reduced_json = json_files[0]
                with open(os.path.join(job_results_dir, reduced_json)) as fd:
                    data[os.path.splitext(reduced_json)[0]] = json.load(fd)

            if not data:
                print_msg(self.analysis_section_output, 'No job selected: add at least one job and try again.')
                return

            runs = OrderedDict()

            for dataset in list(data.keys()):

                cfg = data[dataset]['simConfig']
                # Build a label from the filename
                runs[dataset] = data[dataset]

                stats = data[dataset]['spike_stats']
                print_msg(self.analysis_section_output, f"✅ {dataset}", True)
                print_msg(self.analysis_section_output, f"   duration={cfg['duration']}ms  starttime={cfg['starttime']}ms  seed={cfg['seedval']}", True)
                for pop, s in stats.items():
                    print_msg(self.analysis_section_output, f"   {pop}: {s['n_cells']} cells, {s['n_spikes']} spikes, {s['mean_rate_hz']} Hz", True)

                self.level_one_analysis_widget.plot(runs)
                self.level_two_analysis_widget.plot(runs)
                self.level_three_analysis_widget.plot(runs)
                self.level_four_analysis_widget.plot(runs, self.level_three_analysis_widget.pac_summary)

        except Exception as err:
            print_error(self.analysis_section_output, str(err))

    def _clear_analysis_button_callback(self, button):
        self.analysis_section_output.clear_output()
        for widget in self.level_widgets:
            widget.clear()
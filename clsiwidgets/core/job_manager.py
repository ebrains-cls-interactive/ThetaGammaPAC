import json
import os
import shutil
from pathlib import Path

from clsiwidgets.config import TAGS, UNICORE_HPC
from clsiwidgets.core.enums.job_enums import JobMode
from clsiwidgets.core.models.job import Job
from clsiwidgets.core.services.auth import retrieve_token
from clsiwidgets.core.services.cls_sa import CLSSAService
from clsiwidgets.core.services.unicore import UnicoreService

TYPE_MAPPING = {
    "float": float,
    "int": int,
}


class JobManager:
    def __init__(
        self,
        data_path: Path,
        results_path: Path,
    ):
        self._data_path = data_path
        self._results_path = results_path
        self._registry_path = self._data_path / "job_registry.json"

    @property
    def jobs(self) -> list[Job]:
        return self._load_job_registry() or []

    @property
    def completed_jobs(self) -> list[Job]:
        return [j for j in self.jobs if j.status.lower() == 'successful']

    @property
    def downloaded_jobs(self) -> list[Job]:
        return [j for j in self.jobs if j.downloaded == 'Yes']

    def _load_job_registry(self) -> list[Job]:
        if not self._registry_path.exists():
            return []
        with open(self._registry_path, 'r') as fd:
            data = json.load(fd)
        return [Job.model_validate(j) for j in data['jobs']]

    def _save_job_registry(self, jobs: list[Job]) -> None:
        data = {'jobs': [j.model_dump() for j in jobs]}
        with open(self._registry_path, 'w') as fd:
            json.dump(data, fd, indent=4)

    def _store_new_job(self, job: Job) -> None:
        jobs = self._load_job_registry()
        jobs.append(job)
        self._save_job_registry(jobs)

    def _update_job_registry(self, job: Job) -> None:
        jobs = self._load_job_registry()
        for j in jobs:
            if j.id == job.id:
                j.status = job.status
                j.downloaded = job.downloaded
                break
        self._save_job_registry(jobs)

    def validate_input_values(self, dataset: dict, input_values: str) -> list[float]:
        """Validate the input values for a sweep."""
        try:
            v_t = TYPE_MAPPING[dataset["type"]]
        except KeyError:
            raise ValueError(f"Dataset type {dataset['type']} not recognized.")

        values: list[float] = []

        for value in input_values.split(","):
            try:
                casted_value = v_t(value.strip())
            except Exception:
                raise ValueError(
                    f"Invalid value {casted_value}, {v_t}, {value.strip()}  found. Must be a {dataset['type']}."
                )

            if casted_value < dataset["min"] or casted_value > dataset["max"]:
                raise ValueError(f"Value {casted_value} is outside the range.")

            values.append(casted_value)

        return values

    def _submit_unicore_job(self, hpc_name: str, job_descriptor: dict, execution: str) -> Job:
        job_info = UnicoreService.submit_job(
            hpc=hpc_name,
            root_url=UNICORE_HPC[hpc_name]['root_url'],
            job_descriptor=job_descriptor,
            token=retrieve_token()
        )
        # UNICORE may report the job name as 'N/A' even if 'Name' was sent in the
        # descriptor: the submitted title is the source of truth.
        job_info['title'] = job_descriptor.get('Name') or job_info['title']
        return Job(**job_info, service='Unicore', hpc=hpc_name, execution=execution)

    def _submit_on_jusuf(self, job_title: str, dataset_name: str, input_value: str) -> Job:
        execution = f't42_{dataset_name}_{input_value}'
        job_descriptor = {
            'User precommand': '/p/project1/icei-hbp-2020-0013/ThetagammaPAC/prepare_job.sh',
            'Executable': './run_uni_ext.sh',
            'Name': job_title,
            'Environment': {
                f'SIM_PARAM_{dataset_name.upper()}': str(input_value),
                'SIM_RUNID': execution,
            },
            'Resources': {
                'Project': 'icei-hbp-2020-0013',
                'Nodes': 1,
                'TotalCPUs': 128,
                'CPUsPerNode': 128,
                'Runtime': '3h'
            },
            'Tags': TAGS
        }
        hpc_name = 'JUSUF'
        return self._submit_unicore_job(hpc_name, job_descriptor, execution)

    def _submit_on_sa(self, sa_hpc: str, sa_project: str, job_title: str, dataset_name: str, input_value: float) -> Job:
        PRE_COMMAND = "/p/project1/icei-hbp-2020-0013/ThetagammaPAC/prepare_job.sh"
        EXEC_COMMAND = "./run_uni_ext.sh"

        execution = f"t42_{dataset_name}_{input_value}"

        # CLS does not offer an Environment field, so we prepend `export` statements
        # to the command so run_uni_ext.sh sees the same SIM_PARAM_* env vars.
        env_prefix = (
            f"export SIM_PARAM_{dataset_name.upper()}={input_value}; "
            f"export SIM_RUNID={execution}; "
        )
        COMMAND = f"{env_prefix}{PRE_COMMAND} && {EXEC_COMMAND}"

        payload = {
            "command": COMMAND,
            "node_number": 2,
            "core_number": 256,
            "runtime": 6.5,
            "title": job_title,
        }

        job_info = CLSSAService.submit_job(hpc=sa_hpc, project=sa_project, payload=payload)
        return Job(**job_info, service='CLS-Service-Account', hpc=sa_hpc, execution=execution)

    def submit_job(self, *, mode: JobMode, job_title: str, dataset_name: str, dataset: dict, input_values: str, **kwargs) -> None:
        """Submit the job."""
        values = self.validate_input_values(dataset, input_values)
        for value in values:
            if mode == JobMode.OWN_USER:
                job = self._submit_on_jusuf(job_title, dataset_name, str(value))
            elif mode == JobMode.CLS_SA:
                job = self._submit_on_sa(
                    sa_hpc='JUSUF',
                    sa_project=kwargs['sa_project'],
                    job_title=job_title,
                    dataset_name=dataset_name,
                    input_value=value,
                )
            else:
                raise ValueError(f'Invalid mode: {mode}')
            if job is None:
                raise RuntimeError('Error on job submission: None type returned')
            self._store_new_job(job)

    def fetch_jobs(self) -> list[Job]:
        jobs = self._load_job_registry()
        for job in jobs:
            if job.status == 'SUCCESSFUL':
                continue
            if job.service == 'Unicore':
                job_info = UnicoreService.get_job(
                    job_id=job.id,
                    hpc=job.hpc,
                    root_url=UNICORE_HPC[job.hpc]['root_url'],
                    token=retrieve_token()
                )
            elif job.service == 'CLS-Service-Account':
                job_info = CLSSAService.get_job(id=job.id)
            else:
                raise ValueError(f'Job service {job.service} not valid')

            job.status = job_info['status']
            # keep the stored title if the service doesn't know it (e.g. UNICORE 'N/A')
            if job_info['title'] not in ('N/A', 'UNICORE_Job', '', None):
                job.title = job_info['title']

        self._save_job_registry(jobs=jobs)
        return jobs

    def _fetch_unicore_results(self, job_id: str):
        try:
            job_results_dir = self._results_path / job_id
            job_results_dir.mkdir(parents=True, exist_ok=True)
            hpc_name = 'JUSUF'
            hpc_root_url = UNICORE_HPC[hpc_name]['root_url']
            storage = UnicoreService.get_job_storage(
                job_id=job_id,
                hpc=hpc_name,
                root_url=hpc_root_url,
                token=retrieve_token(),
            )
            data_dir = storage.listdir('t42_data')
            reduced_files = [f for f in data_dir if f.endswith('_reduced.json')]
            if len(reduced_files) == 0:
                data_dir = storage.listdir()
                reduced_files = [f for f in data_dir if f.endswith('_reduced.json')]
                if len(reduced_files) == 0:
                    raise RuntimeError('No reduced files found!')

            for rf_file in reduced_files:
                try:
                    filename = rf_file.split('/')[-1]
                    dst = os.path.join(job_results_dir, filename)
                    data_dir[rf_file].download(dst)
                except Exception as err:
                    print(err)
                    continue

        except Exception as err:
            shutil.rmtree(job_results_dir, ignore_errors=True)
            raise RuntimeError(err)

    def _fetch_sa_results(self, job_id: str):
        pass

    def fetch_results(self, job: Job) -> None:
        if job.status != 'SUCCESSFUL' or job.downloaded != 'No':
            return
        try:
            job.downloaded = 'Downloading'
            self._update_job_registry(job)

            if job.service == 'Unicore':
                self._fetch_unicore_results(job.id)

            elif job.service == 'CLS-Service-Account':
                self._fetch_sa_results(job.id)

            else:
                raise ValueError(f'Job service {job.service} not valid')

            job.downloaded = 'Yes'

        except Exception as err:
            job.downloaded = 'No'
            raise RuntimeError(err)

        finally:
            self._update_job_registry(job)

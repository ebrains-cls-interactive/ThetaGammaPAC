import json
import os
from pathlib import Path

from clsiwidgets.api import prepare_workspace_environment
from clsiwidgets.core.enums.job_enums import JobMode
from clsiwidgets.core.job_manager import JobManager
from clsiwidgets.core.models.job import Job


def test_job_submission():
    paths = prepare_workspace_environment()

    dataset = None
    with open(os.path.join(paths['data_path'], 'dataset.json')) as fd:
        dataset = json.load(fd)
    assert isinstance(dataset, dict)

    data_key = 'olm_pc_gaba_tau'

    job_manager = JobManager(data_path=paths['data_path'], results_path=paths['results_path'])
    assert isinstance(job_manager, JobManager)

    assert isinstance(job_manager.jobs, list)
    cc_jobs = len(job_manager.jobs)

    job_manager.submit_job(mode=JobMode.OWN_USER,
                           job_title='TEST UNIT',
                           dataset_name=data_key,
                           dataset=dataset[data_key],
                           input_values='8.0',
                           sa_hpc='JUSUF',
                           sa_project='tgp-test-project')

    assert len(job_manager.jobs) == cc_jobs + 1


def test_update_jobs():
    paths = prepare_workspace_environment(str(Path(__file__).parent.parent.parent.absolute()))

    job_manager = JobManager(data_path=paths['data_path'], results_path=paths['results_path'])
    assert isinstance(job_manager, JobManager)
    assert isinstance(job_manager.jobs, list)

    jobs = job_manager.fetch_jobs()
    assert len(job_manager.jobs) == len(jobs)


def test_fetch_job_results():
    paths = prepare_workspace_environment(str(Path(__file__).parent.parent.parent.absolute()))

    job_manager = JobManager(data_path=paths['data_path'], results_path=paths['results_path'])
    assert isinstance(job_manager, JobManager)
    assert isinstance(job_manager.jobs, list)

    job_id = 'Au3clcrCy6v'
    jobs = job_manager.jobs
    job = None
    for j in jobs:
        if j.id == job_id:
            job = j
    assert isinstance(job, Job)

    job_manager.fetch_results(job)
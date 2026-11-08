
from datetime import datetime

from pyunicore.client import Client, Job, Storage, Transport
from pyunicore.credentials import OIDCToken


class UnicoreService:

    def __init__(self, hpc: str, root_url: str, token: str):
        self._hpc = hpc
        self._root_url = root_url
        self._transport = Transport(OIDCToken(token))
        self._client = Client(self._transport, self._root_url)

    def get_client(self):
        return self._client

    def get_transport(self):
        return self._client.transport

    def get_job_url(self, job_id: str) -> str:
        return f'{self._root_url}/jobs/{job_id}'

    def parse_job(self, job: Job) -> dict:
        props = job.properties
        parsed_props = {
            'id': job.job_id,
            'title': props['name'],                                             # type: ignore
            'status': props['status'],                                          # type: ignore
            'created_at': datetime.fromisoformat(props['submissionTime']),      # type: ignore
        }
        return parsed_props

    @classmethod
    def submit_job(cls, hpc: str, root_url: str, job_descriptor: dict, token: str) -> dict:
        c = cls(hpc, root_url, token)
        job = c.get_client().new_job(job_description=job_descriptor)
        return c.parse_job(job)

    @classmethod
    def get_job(cls, job_id: str, hpc: str, root_url: str, token: str) -> dict:
        c = cls(hpc, root_url, token)
        job = Job(c.get_transport(), c.get_job_url(job_id))
        return c.parse_job(job)

    @classmethod
    def get_job_storage(cls, job_id: str, hpc: str, root_url: str, token: str) -> Storage:
        c = cls(hpc, root_url, token)
        job = Job(c.get_transport(), c.get_job_url(job_id))
        return job.working_dir

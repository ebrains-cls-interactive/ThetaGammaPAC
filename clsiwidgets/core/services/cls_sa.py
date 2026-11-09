from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import requests

from clsiwidgets.config import CLS_SA_ROOT_URL, SERVICE_ACCOUNT_APP_KEY
from clsiwidgets.core.services.auth import retrieve_token


class CLSSAService:

    def _build_header(self, user_token: bool = False) -> dict:
        base_headers = {
            "appkey": SERVICE_ACCOUNT_APP_KEY,
            "content-type": "application/json",
        }
        if user_token:
            base_headers.update({"authorization": "Bearer " + retrieve_token()})
        return base_headers

    @classmethod
    def get_hpc(cls) -> list[str]:
        url = CLS_SA_ROOT_URL + "/hpc"
        r = requests.get(url, headers=cls()._build_header())
        return [h["name"] for h in r.json() if h['is_enabled']]

    @classmethod
    def get_project(cls, hpc: str | None = None) -> list[str]:
        url = CLS_SA_ROOT_URL + "/project"
        query_params = {}
        if hpc:
            query_params.update({'hpc': hpc})
        r = requests.get(url, headers=cls()._build_header(), params=query_params)
        return [p["name"] for p in r.json() if p['is_enabled']]

    @classmethod
    def submit_job(cls, hpc: str, project: str, payload: dict) -> dict:
        headers = cls()._build_header(user_token=True)
        payload.update({
            'hpc': hpc,
            'project': project,
        })

        r_1 = requests.post(
            url=f"{CLS_SA_ROOT_URL}/job/",
            headers=headers,
            data=json.dumps(payload),
        )

        if r_1.status_code != 201:
            raise RuntimeError(f"CLS-SA submit failed: HTTP {r_1.status_code} - {r_1.text}")

        job = r_1.json()

        placeholder_file = Path(__file__).parent / 'resources' / 'placeholder.txt'
        if not placeholder_file.exists():
            placeholder_file.write_text('Hello world!')
        placeholder_content = placeholder_file.read_bytes()

        headers.update({
            'Content-Disposition': 'attachment;filename=placeholder.txt',
            'Content-Type': 'text/plain'
        })
        r_2 = requests.patch(
            url=f'{CLS_SA_ROOT_URL}/job/{job["id"]}/upload-input-file/',
            headers=headers,
            data=placeholder_content
        )

        if r_2.status_code != 200:
            raise RuntimeError(f"CLS-SA upload failed: HTTP {r_2.status_code} - {r_2.text}")

        job = r_2.json()
        job_info = {
            'id': str(job['id']),
            'title': job['title'],
            'status': job['stage'],
            'created_at': datetime.fromisoformat(job['init_date']),
        }

        return job_info

    @classmethod
    def get_job(cls, job_id: str) -> dict:
        r = requests.get(url=f'{CLS_SA_ROOT_URL}/job/{job_id}',
                         headers=cls()._build_header(user_token=True))
        if r.status_code != 200:
            raise RuntimeError(f"CLS-SA get job failed: HTTP {r.status_code} - {r.text}")

        job = r.json()
        job_info = {
            'id': job['id'],
            'title': job['title'],
            'status': job['stage'],
            'created_at': datetime.fromisoformat(job['init_date']),
        }

        return job_info

    @classmethod
    def fetch_results(cls, id: str) -> None:
        pass
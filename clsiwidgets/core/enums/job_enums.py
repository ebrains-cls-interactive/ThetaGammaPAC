from enum import Enum


class JobMode(Enum):
    OWN_USER = "Own user"
    CLS_SA = "CLS-Service-Account"


class JobStatus(Enum):
    SUCCESSFUL = "SUCCESSFUL"
    FAILED = "FAILED"
    RUNNING = "RUNNING"
    QUEUE = "QUEUE"
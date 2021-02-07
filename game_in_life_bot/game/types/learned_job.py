from bson import ObjectId

from .job import Job


class LearnedJob:
    def __init__(self, job: ObjectId, xp: int):
        self.job = Job(id=job)
        self.xp = xp

    def to_db(self):
        return {"job": self.job.id,
                "xp": self.xp}

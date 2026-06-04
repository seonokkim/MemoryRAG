from app.models import FeedbackLog


class FeedbackRepository:
    def __init__(self, db) -> None:
        self.db = db

    def create(self, log: FeedbackLog) -> FeedbackLog:
        self.db.add(log)
        self.db.flush()
        return log

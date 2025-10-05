from Blueprint_app.extensions import db
from Blueprint_app.models import TestingFaceEncoding
from datetime import datetime, timedelta

def cleanup_testing_encodings():
    cutoff = datetime.utcnow() - timedelta(days=1)
    TestingFaceEncoding.query.filter(TestingFaceEncoding.created_at < cutoff).delete()
    db.session.commit()

# Example usage: call cleanup_testing_encodings() every 24 hours using a scheduler like APScheduler or Celery

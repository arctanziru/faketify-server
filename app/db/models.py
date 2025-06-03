from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy.orm import relationship

Base = declarative_base()


class DetectionModel(Base):
    __tablename__ = "detection"

    id = Column(String, primary_key=True)
    headline = Column(String)
    headline_date = Column(String, nullable=True)
    detection = Column(Boolean)
    probability = Column(Float)
    detection_duration = Column(Float, nullable=True)  # milliseconds
    created_at = Column(DateTime, default=datetime.utcnow)
    reviewer_verdict = Column(Boolean, nullable=True)
    reviewer_note = Column(String, nullable=True)
    reviewer_id = Column(String, nullable=True)  # Foreign key to UserModel
    reviewed_at = Column(DateTime, nullable=True)
    feedbacks = relationship("FeedbackModel")

    def to_dict(self):
        return {
            "id": self.id,
            "headline": self.headline,
            "headline_date": self.headline_date,
            "detection": self.detection,
            "probability": self.probability,
            "detection_duration": self.detection_duration,
            "created_at": self.created_at.isoformat(),
            "reviewer_verdict": self.reviewer_verdict,
            "reviewer_note": self.reviewer_note,
            "reviewer_id": self.reviewer_id,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "feedbacks": [feedback.to_dict() for feedback in self.feedbacks],
        }


class FeedbackModel(Base):
    __tablename__ = "feedback"

    id = Column(String, primary_key=True)
    full_name = Column(
        String, nullable=True
    )  # feedback fullname, anonymous if not provided
    email = Column(String, nullable=True)
    feedback = Column(String, nullable=False)
    detection_id = Column(String, nullable=False)  # Foreign key to DetectionModel
    created_at = Column(DateTime, default=datetime.utcnow)
    detection_id = Column(ForeignKey("detection.id"))
    detection = relationship("DetectionModel", back_populates="feedbacks")

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "feedback": self.feedback,
            "detection_id": self.detection_id,
            "created_at": self.created_at.isoformat(),
        }


class UserModel(Base):
    __tablename__ = "user"

    id = Column(String, primary_key=True)
    full_name = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(String, default="user")
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "role": self.role,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
        }

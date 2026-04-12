from app import db

class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.user_id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('drives.id'), nullable=False)
    application_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    status = db.Column(db.String(20), default='applied')  # applied, shortlisted, selected, rejected

    __table_args__ = (db.UniqueConstraint('student_id', 'drive_id', name='unique_application'),)

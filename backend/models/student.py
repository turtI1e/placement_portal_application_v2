from app import db

class Student(db.Model):
    __tablename__ = 'students'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(20))
    branch = db.Column(db.String(50))
    year = db.Column(db.Integer)
    cgpa = db.Column(db.Float)
    resume_path = db.Column(db.String(200))

    # Relationships
    applications = db.relationship('Application', backref='student', lazy='dynamic', cascade='all, delete-orphan')

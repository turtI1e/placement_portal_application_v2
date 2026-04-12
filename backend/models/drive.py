from app import db

class Drive(db.Model):
    __tablename__ = 'drives'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.user_id'), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    eligibility = db.Column(db.String(200))
    deadline = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, closed
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relationships
    applications = db.relationship('Application', backref='drive', lazy='dynamic', cascade='all, delete-orphan')

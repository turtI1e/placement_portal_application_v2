from app import db

class Company(db.Model):
    __tablename__ = 'companies'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    hr_contact = db.Column(db.String(100))
    website = db.Column(db.String(200))
    approved = db.Column(db.Boolean, default=False)

    # Relationships
    drives = db.relationship('Drive', backref='company', lazy='dynamic', cascade='all, delete-orphan')

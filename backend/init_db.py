from app import create_app, db
from models import User
from werkzeug.security import generate_password_hash

def init_db():
    app = create_app()
    with app.app_context():
        db.create_all()
        # Create admin if not exists
        admin = db.session.query(User).filter_by(role='admin').first()
        if not admin:
            admin = User(
                email='admin@placement.com',
                password_hash=generate_password_hash('admin123'),
                role='admin',
                is_active=True
            )
            db.session.add(admin)
            db.session.commit()
            print('Admin created: admin@placement.com / admin123')
        else:
            print('Admin already exists')

if __name__ == '__main__':
    init_db()

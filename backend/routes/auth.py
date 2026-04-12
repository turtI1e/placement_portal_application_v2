from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token
from datetime import timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    from models import User, Company
    db = current_app.db
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'msg': 'Email and password required'}), 400

    user = db.session.query(User).filter_by(email=email).first()
    if not user or not user.check_password(password) or not user.is_active:
        return jsonify({'msg': 'Invalid credentials or inactive account'}), 401

    if user.role == 'company' and not user.company_profile.approved:
        return jsonify({'msg': 'Company account pending approval'}), 403

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={'role': user.role},
        expires_delta=timedelta(hours=1)
    )

    print(f"Generated token (first 50 chars): {access_token[:50]}...")
    print(f"Token length: {len(access_token)}")

    # DEBUG: Print successful login
    print(f"DEBUG: Login successful for user {user.id}, token created")
    return jsonify({'token': access_token, 'role': user.role}), 200

@auth_bp.route('/register/student', methods=['POST'])
def register_student():
    from models import User, Student
    db = current_app.db
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    contact = data.get('contact')
    branch = data.get('branch')
    year = data.get('year')
    cgpa = data.get('cgpa')

    if not email or not password or not name:
        return jsonify({'msg': 'Missing required fields'}), 400

    if db.session.query(User).filter_by(email=email).first():
        return jsonify({'msg': 'Email already registered'}), 400

    user = User(email=email, role='student', is_active=True)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    student = Student(
        user_id=user.id,
        name=name,
        contact=contact,
        branch=branch,
        year=year,
        cgpa=cgpa
    )
    db.session.add(student)
    db.session.commit()

    # Invalidate admin dashboard and companies,students caches
    from extensions import cache
    cache.delete('admin_dashboard_stats')
    cache.delete('admin_companies_')   # empty search companies list
    cache.delete('admin_students_')    # empty search students list

    return jsonify({'msg': 'Student registration successful'}), 201

@auth_bp.route('/register/company', methods=['POST'])
def register_company():
    from models import User, Company
    db = current_app.db
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    company_name = data.get('company_name')
    hr_contact = data.get('hr_contact')
    website = data.get('website')

    if not email or not password or not company_name:
        return jsonify({'msg': 'Missing required fields'}), 400

    if db.session.query(User).filter_by(email=email).first():
        return jsonify({'msg': 'Email already registered'}), 400

    user = User(email=email, role='company', is_active=True)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()   # This creates the user.id

    company = Company(
        user_id=user.id,          # ← This was the main bug in some versions
        company_name=company_name,
        hr_contact=hr_contact,
        website=website,
        approved=False
    )
    db.session.add(company)
    db.session.commit()

    # Invalidate admin caches
    from extensions import cache
    cache.delete('admin_dashboard_stats')
    cache.delete('admin_companies_')
    cache.delete('admin_students_')

    return jsonify({'msg': 'Company registration successful, pending admin approval'}), 201

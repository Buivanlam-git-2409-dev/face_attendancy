# security.py
import jwt
import bcrypt
from functools import wraps
from datetime import datetime, timedelta
from flask import session, flash, redirect, url_for, request

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    if not password:
        raise ValueError("Password cannot be empty")
    
    # Generate salt and hash password
    salt = bcrypt.gensalt(rounds=12)  # 12 rounds is secure and fast enough
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a password against its hash
    
    Args:
        password: Plain text password to check
        hashed: Hashed password from database
        
    Returns:
        True if password matches, False otherwise
    """
    if not password or not hashed:
        return False
    
    if not hashed.startswith('$2'):
        return False

    try:
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hashed.encode('utf-8')
        )
    except ValueError:
        return False

def generate_token(user_id: int, role: str, is_admin: bool = False, expires_in_hours: int = 24, secret_key: str = None) -> str:
    """
    Generate a JWT token for authenticated user
    
    Args:
        user_id: User ID (rollno for students, f_id for faculty)
        role: User role ('student' or 'faculty')
        is_admin: Whether user is admin (faculty only)
        expires_in_hours: Token expiration time in hours
        secret_key: Secret key for signing (uses app config if not provided)
        
    Returns:
        JWT token string
    """
    if not secret_key:
        from flask import current_app
        secret_key = current_app.config.get('SECRET_KEY')
    
    payload = {
        'user_id': user_id,
        'role': role,
        'is_admin': is_admin,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(hours=expires_in_hours),
    }
    return jwt.encode(payload, secret_key, algorithm='HS256')

def generate_refresh_token(user_id: int, role: str, expires_in_days: int = 7, secret_key: str = None) -> str:
    """
    Generate a refresh token for getting new access tokens
    
    Args:
        user_id: User ID
        role: User role
        expires_in_days: Token expiration time in days
        secret_key: Secret key for signing (uses app config if not provided)
        
    Returns:
        Refresh token string
    """
    if not secret_key:
        from flask import current_app
        secret_key = current_app.config.get('SECRET_KEY')
    
    payload = {
        'user_id': user_id,
        'role': role,
        'type': 'refresh',
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(days=expires_in_days),
    }
    return jwt.encode(payload, secret_key, algorithm='HS256')

def verify_token(token: str, secret_key: str = None) -> dict:
    """
    Verify and decode a JWT token
    
    Args:
        token: JWT token string
        secret_key: Secret key for verification (uses app config if not provided)
        
    Returns:
        Token payload dict if valid, None if invalid
    """
    if not secret_key:
        from flask import current_app
        secret_key = current_app.config.get('SECRET_KEY')
    
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        if payload.get('type') == 'refresh':
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def verify_refresh_token(token: str, secret_key: str = None) -> dict:
    """
    Verify and decode a refresh token
    
    Args:
        token: Refresh token string
        secret_key: Secret key for verification (uses app config if not provided)
        
    Returns:
        Token payload dict if valid, None if invalid
    """
    if not secret_key:
        from flask import current_app
        secret_key = current_app.config.get('SECRET_KEY')
    
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        if payload.get('type') != 'refresh':
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def extract_token_from_request() -> str:
    """
    Extract JWT token from Authorization header
    
    Returns:
        Token string or None
    """
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    return auth_header[7:]  # Remove 'Bearer ' prefix

def require_jwt(f):
    """
    Decorator to require JWT token for routes
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = extract_token_from_request()
        if not token:
            return {'success': False, 'error': {'code': 'UNAUTHORIZED', 'message': 'Token required'}}, 401
        
        payload = verify_token(token)
        if not payload:
            return {'success': False, 'error': {'code': 'UNAUTHORIZED', 'message': 'Invalid or expired token'}}, 401
        
        request.user = payload
        return f(*args, **kwargs)
    return decorated_function

def require_student(f):
    """
    Decorator to require student role JWT token
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = extract_token_from_request()
        if not token:
            return {'success': False, 'error': {'code': 'UNAUTHORIZED', 'message': 'Token required'}}, 401
        
        payload = verify_token(token)
        if not payload or payload.get('role') != 'student':
            return {'success': False, 'error': {'code': 'UNAUTHORIZED', 'message': 'Student authentication required'}}, 401
        
        request.user = payload
        return f(*args, **kwargs)
    return decorated_function

def require_faculty(f):
    """
    Decorator to require faculty role JWT token
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = extract_token_from_request()
        if not token:
            return {'success': False, 'error': {'code': 'UNAUTHORIZED', 'message': 'Token required'}}, 401
        
        payload = verify_token(token)
        if not payload or payload.get('role') != 'faculty':
            return {'success': False, 'error': {'code': 'UNAUTHORIZED', 'message': 'Faculty authentication required'}}, 401
        
        request.user = payload
        return f(*args, **kwargs)
    return decorated_function

def require_admin(f):
    """
    Decorator to require admin role JWT token
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = extract_token_from_request()
        if not token:
            return {'success': False, 'error': {'code': 'UNAUTHORIZED', 'message': 'Token required'}}, 401
        
        payload = verify_token(token)
        if not payload or payload.get('role') != 'faculty' or not payload.get('is_admin'):
            return {'success': False, 'error': {'code': 'UNAUTHORIZED', 'message': 'Admin authentication required'}}, 401
        
        request.user = payload
        return f(*args, **kwargs)
    return decorated_function

def login_required(f):
    """
    Decorator to require login for routes
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

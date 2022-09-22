import sqlalchemy
from app.models import User
from app.app_utils import field_check, is_whitespace
from base64 import b64encode, b64decode
from binascii import Error
import logging as logger
from werkzeug.security import check_password_hash, generate_password_hash
import pyotp
from app import app, db, mail
import hashlib
from io import BytesIO
import pyqrcode
import re
from flask_login import login_user
import os, sys
from flask import request, make_response, render_template, Response, url_for
from functools import wraps
import jwt
import json
from flask_mail import Message

EMAIL_REGEX = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+', re.IGNORECASE)
sys.path.append(os.path.dirname(__file__))

def __gen_api_token(username: str, email: str) -> str:
    if field_check({'username': username, 'email': email}):
        hash_content = username + email + app.config['SECRET_KEY']
        return hashlib.sha256(hash_content.encode('utf-8')).hexdigest()
    else:
        logger.warn('Attempted to generate API token with missing information.')
        raise ValueError(
            'Attempted to generate API token with missing information.')


def insert_user(new_email: str, new_username: str, new_password: str) -> bool:
    '''
    Attempts to insert a new User record into the database. If the user already exists,
    a tuple is returned with the values False, False. If successful, True, Username is returned.

    '''

    if field_check({'new_email': new_email, 'new_username': new_username, 'new_password': new_password}):
        try:
            decode_pass = b64decode(new_password).decode('utf8')
        except Error as e:
            logger.warn('Unable to properly decode base-64 new_password.', e)

        # Query the database to see if the user already exists.
        user_email = User.query.filter_by(
            email=new_email).first()
        user_username = User.query.filter_by(
            username=new_username).first()

        if user_email is None and user_username is None:
            # Generate a new hash of the password using SHA-512
            new_hash = generate_password_hash(decode_pass, method='sha256')

            # Generate a base-32 secret key for TOTP.
            totp_secret = pyotp.random_base32()

            # Get an API Token.
            new_api_token = __gen_api_token(new_username, new_email)

            try:
                # Create the new User object and commit it to the db.
                user = User(username=new_username, email=new_email,
                            hash=new_hash, totp_key=totp_secret, api_token=new_api_token)
                db.session.add(user)
                db.session.commit()
            except sqlalchemy.exc.IntegrityError as e:
                logger.error('Unable to insert user into database', e)
                db.session.rollback()
                return False
            
            return True
        else:
            logger.warn('Attempted to create new account for user that was already existing.')
            return False
    else:
        logger.warn(
            'Attempted to insert user with missing or blank information.')
        raise ValueError(
            'Attempted to insert user with missing or blank information.')


def verify_user(cred: str, password: str) -> tuple:
    if EMAIL_REGEX.match(cred):
        if field_check({'email': cred, 'password': password}):
            password = b64decode(password).decode('utf-8')
            user = User.query.filter_by(email=cred).first()
            
            if user:
                if check_password_hash(user.hash, password):
                    login_user(user)
                    return True, user.username  
    else:
        if field_check({'username': cred, 'password': password}):
            password = b64decode(password).decode('utf-8')
            user = User.query.filter_by(username=cred).first()
            
            if user:
                if check_password_hash(user.hash, password):
                    login_user(user)
                    return True, user.username  
    return False, False


def get_qr_code(username: str) -> str:
    if is_whitespace(username) or username is None:
        logger.warn('Error creating QR code --- Username was empty or None')
        raise ValueError('Username was empty or None.')
    else:
        user = User.query.filter_by(username=username).first()
        
        if user:
            totp_key = user.totp_key
        else:
            return None

        if totp_key:    
            otp_auth = pyotp.totp.TOTP(totp_key).provisioning_uri(
                name=username, issuer_name='Jared Rathbun Portfolio'
            )
            qr = pyqrcode.create(otp_auth)
            buffer = BytesIO()
            qr.png(buffer, scale=6)
            html_ready_qr = 'data:image/png;base64,' + b64encode(buffer.getvalue()).decode('ascii')
            return html_ready_qr
        else:
            return None

def verify_qr_code(user: User, otp_code: str) -> bool:
    if field_check({'otp_code': otp_code}) and user is not None:
        totp_key = user.totp_key
        return pyotp.TOTP(totp_key).verify(int(otp_code)) if totp_key else False
    else:
        return False


def jwt_required(f):
    '''
    Wrapper function that makes a function/endpoint require a JWT token.
    '''
    @wraps(f)
    def decorated_func(*args, **kwargs):
        token = None
        if 'x-access-token' in request.cookies:
            token = request.cookies.get('x-access-token')
        
        if not token:
            return make_response(render_template('auth/login.html'), 401)   
       
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')
            user = data['public_id']
        except Exception as e:
            import logging
            logging.exception('Exception encountered while decoding JWT.', e)
            return make_response(render_template('auth/login.html'), 401)
        
        return f(user, *args, **kwargs)

    return decorated_func


def jsonResponseFactory(data: dict) -> Response:
    '''Return a callable in top of Response'''
    def callable(response=None, *args, **kwargs):
        '''Return a response with JSON data from factory context'''
        return Response(json.dumps(data), *args, **kwargs)
    return callable

def send_reset_email(email: str) -> bool:
    user = User.query.filter_by(email=email).first()
    
    if user is None:
        return False
    else:
        token = user.get_reset_token()
        msg = Message('Jared Rathbun Portfolio | Password Reset Request',
                sender=app.config['EMAIL_USERNAME'],
                recipients=[user.email])
        msg.body = f'''
            To reset your password, please visit the following link:
            {url_for('auth.reset', token=token, _external=True)}
            If you did not make this request please reset your password immediately.
            '''
        mail.send(msg)
        return True
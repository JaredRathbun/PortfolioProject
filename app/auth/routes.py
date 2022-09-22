from flask import Blueprint, render_template, redirect, request, session, make_response, url_for, Response
from datetime import datetime, timedelta
import jwt
from app import app, login_manager, db
from app.auth.util import insert_user, verify_qr_code, verify_user, get_qr_code, jwt_required, send_reset_email
from app.app_utils import field_check
import logging as logger
from app.models import User
from flask_login import login_user, logout_user

@login_manager.user_loader
def load_user(user_id):
    '''
    Loads a user into the login manager (AKA logs them in)
    '''
    return User.query.get(int(user_id))

# Set the appropriate login view and create the blueprint.
login_manager.login_view = "auth.login"
auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    '''
    Either renders the HTML page for logging in, or processes a login.
    
    For the POST request, the body should contain:
    {
        'username': <username>,
        'password': <password> <- Base64 Encoded
    }
    
    or 
    
    {
        'email': <email>,
        'password': <password> <- Base64 Encoded
    }
    '''
    if request.method == 'GET':
        return render_template('auth/login.html')
    else:
        body = request.get_json()   
        
        if field_check(body):
            if 'username' in body.keys():          
                auth_res, username = verify_user(body['username'], body['password'])

            if 'email' in body.keys():
                auth_res, username = verify_user(body['email'], body['password'])

            try:
                if auth_res:
                    token = jwt.encode({
                        'public_id': username,
                        'exp': datetime.utcnow() + timedelta(minutes = 60) 
                    }, app.config['SECRET_KEY'])

                    resp = redirect('/auth')
                    resp.headers.add('Access-Control-Allow-Origin', '*')
                    resp.set_cookie('x-access-token', token, httponly=True)
                    return resp
                else:
                    return make_response('Bad login.', 401, {'WWW-Authenticate': 'Basic = Bad Login'})
            except Exception as e:
                logger.warn('Exception encountered during login.', e)
                return make_response('Bad login.', 401, {'WWW-Authenticate': 'Basic = Bad Login'})
        else:
            return make_response('Bad request.', 400, {'WWW-Authenticate': 'Basic = Bad Request'})


@auth.route('/register', methods=['GET', 'POST'])
def register():
    '''
    Either renders the HTML page for registering or processing a request to register an account.
    
    If requesting to register, the POST body should contain:
    {
        'email': <email>,
        'username': <username>,
        'password': <password> <-- Base64 Encoded
    }
    '''
    if request.method == 'GET':
        return render_template('auth/register.html')
    else:
        body = request.get_json()   
        if field_check(body):
            try:
                username = body['username']
                res = insert_user(body['email'], body['username'], body['password'])
                
                if res:
                    # Get the OTP URI and create a QRCode from it.
                    qr_code = get_qr_code(username)
                    
                    # Generate a JWT token.
                    token = jwt.encode({
                        'public_id': username,
                        'exp': datetime.utcnow() + timedelta(minutes = 60) 
                    }, app.config['SECRET_KEY'])
                    
                    # Add the JWT token as a cookie and pass the QR Code to the templating engine.
                    resp = redirect(url_for('.qr', qr_code = qr_code))
                    resp.headers.add('Access-Control-Allow-Origin', '*')
                    resp.set_cookie('x-access-token', token, httponly=True)
                    return resp
                else:
                    return Response(status=409)
            except ValueError:
                Response(status=400) 
        else:
            Response(status=400) 


@auth.route('/reset', methods = ['GET', 'POST'])
def reset():
    '''
    Either renders the HTML page for resetting a user's password or processes a password reset.
    
    For the POST request, the body should contain:
    {
        'token': <token from email link>
        'password': <the new password> <- Base64 Encoded
    }
    '''
    from base64 import b64decode
    from werkzeug.security import generate_password_hash

    if request.method == 'GET':
        return render_template('auth/reset.html')
    else:
        token = request.get_json()['token']
        password = b64decode(request.get_json()['password']).decode('utf-8')
        user = User.verify_reset_token(token)
        if user is None:
            return Response(status=400)
        else:
            user.hash = generate_password_hash(password, method='sha256')
            db.session.commit()
            return redirect('/login')
    
@auth.route('/sendreset', methods = ['GET', 'POST'])
def send_reset():
    '''
    Either renders the HTML page for sending a reset password link to an email or processes a request
    for getting the link to reset a password.
    
    For the POST request, the body should be:
    
    {
        'email': <email>
    }
    '''
    if request.method == 'GET':
        return render_template('auth/sendreset.html')
    else:
        # Grab the email from the request. If it is valid and the email was sent, add the 
        # email to the session and return 200. Else, return 400.
        email = request.get_json()['email']
        if field_check({'email': email}):
            if send_reset_email(email):
                session['email'] = email
                return Response(status=200)
        return Response(status=400)


@auth.route('/qr', methods=['GET'])
@jwt_required
def qr(username):
    '''
    Renders the page for a user to scan a QR code.
    
    param: The username of the user. <- Fulfilled by Flask Request object (no need to specify)
    '''
    return render_template('auth/qr.html', qr_code=request.args.get('qr_code'))


@auth.route('/auth', methods=['GET', 'POST'])
@jwt_required
def auth_otp(username):
    '''
    Authenticates a user's OTP against what the server calculates the OTP to be.
    
    param: 
    '''
    if request.method == 'GET':
        return render_template('auth/auth.html')
    else:
        otp_code = request.get_json()['otp']
        user = User.query.filter_by(username=username).first()
        if user:    
            if verify_qr_code(user, otp_code):
                login_user(user)
                session['user'] = user
                return redirect('/classes')
            else:
                logger.info('User attempted to login with invalid OTP code.')
                return Response(status=401)
        else:
            logger.info('Unable to authenticate user when searching for User object.')
            return Response(status=401)

@auth.route('/auth/logout', methods=['GET'])
@jwt_required
def logout(username):
    logger.info(f'Logging out user: {username}')
    '''
    Logs the user out of their session and redirects them to the homepage.
    '''
    logout_user()
    del session['user']
    return redirect('/home')
from app import app
from flask import send_file, render_template, request, Blueprint
from flask_login import login_required
from app.app_utils import field_check   

base_endpoint = Blueprint('base', __name__)
    
@base_endpoint.route('/', methods = ['GET'])
@base_endpoint.route('/home', methods = ['GET'])
def home():
    '''
    Returns the home page. Default route for "/" or "/home"
    '''
    return render_template('/home/home.html')


@base_endpoint.route('/resume', methods = ['GET'])
def resume():
    '''
    Returns a .pdf version of my resume (located at /app/projects/Jared Rathbun - Resume.pdf).
    '''

    # Return a download of the .pdf version of the resume.
    resume_path = '../app/projects/Jared Rathbun - Resume.pdf'
    return send_file(resume_path, as_attachment=True)


@base_endpoint.route('/contact', methods = ['POST'])
def contact():
    '''
    Takes the information inputted on the home page contact form and emails to 
    rathbunj@merrimack.edu.
    '''
    NAME = request.json['name']
    EMAIL = request.json['email']
    SUBJECT = request.json['subject']
    MSG = request.json['message']

    # If the information entered is valid, send an email.
    if field_check({'name': NAME, 'email': EMAIL, 'subject': SUBJECT, 'msg': MSG}):
        import smtplib
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(app.config['EMAIL_USERNAME'], app.config['EMAIL_PASSWORD'])

        # Construct the message.
        EMAIL_MSG = f'''
            ----------------------------------------------------------------------------------------------------------------
            EMAIL FROM: {NAME}
            SENDER EMAIL ADDRESS: {EMAIL}
            SUBJECT: {SUBJECT}
            MESSAGE: {MSG}
            ----------------------------------------------------------------------------------------------------------------
        '''

        server.sendmail(EMAIL, 'rathbunj@merrimack.edu', EMAIL_MSG)
        return "success", 200
    else:
        return "error", 400
from flask import Blueprint, render_template

errors = Blueprint('errors', __name__)

@errors.app_errorhandler(404)

def error_404(error):
    '''
    Renders the 404.html page for 404 errors.
    '''
    return render_template('errors/404.html'), 404

@errors.app_errorhandler(500)
def error_500(error):
    '''
    Renders the 500.html page for 500 errors.
    '''
    return render_template('errors/500.html'), 500
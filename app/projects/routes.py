from flask import Blueprint, Response, render_template, session, request, make_response
from flask_login import login_required
from app.models import Project, ComputerScienceClass, Tag
from app import db
import uuid
from app.app_utils import field_check
from app.app_utils import admin_required

from app.projects.util import upload_icon_image, insert_project, \
    remove_class_from_db, remove_project_from_db, get_structure, create_class, \
    PROJECT_ICON_IMAGE_UPLOAD_FOLDER, CLASS_ICON_IMAGE_UPLOAD_FOLDER, get_code,\
    read_raw_code, get_download_response, verify_api_token, \
    get_project_download, insert_comment, insert_bug

projects = Blueprint('projects', __name__)

def get_header_data():
    user_data = session['user'].get_user_data()
    header_classes = ComputerScienceClass.get_class_endpoints()
    tags = Tag.get_all_tags()
    return header_classes, user_data, tags

@projects.route('/projects/test', methods = ['GET'])
def project_test():
    try:
        csc2620 = ComputerScienceClass(id='CSC2620', class_title='Object Oriented Programming', icon_path='../../static/projects/img/class-icons/oop.png', desc='A class based on how the Object Oriented Paradigm works.')
        csc3120 = ComputerScienceClass(id='CSC3120', class_title='Programming Languages', icon_path='../../static/projects/img/class-icons/prog_lang.jpg', desc='A class covering topics like how to design a language and how to learn them easier.')
        csc5055 = ComputerScienceClass(id='CSC5055', class_title='Network Security', icon_path='../../static/projects/img/class-icons/network_security.jpg', desc='A class covering topics related to securing a network and the data that passes through it.')
        csc3810 = ComputerScienceClass(id='CSC3810', class_title='Database Principles', icon_path='../../static/projects/img/class-icons/database.jpg', desc='A class based on storing data effecently in a database for quick access.')
        
        db.session.add(Project(id=str(uuid.uuid1()), path='./projects/csc2620/final', 
            name='OOP Final Project', cs_class=csc2620, desc='A database management software for guitar settings.', icon_path='../../static/projects/img/project-icons/database.png'))
        db.session.add(Project(id=str(uuid.uuid1()), path='./projects/csc2620/macbook', 
            name='MackBook', cs_class=csc2620, desc='A multithreaded social media project.', icon_path='../../static/projects/img/project-icons/database.png'))
        db.session.add(Project(id=str(uuid.uuid1()), path='./projects/csc5055/final', 
            name='ChatterBox (Final Project)', cs_class=csc5055, desc='Encrypted Chatting Client'))
        db.session.add(Project(id=str(uuid.uuid1()), path='./projects/csc3810/final', 
            name='Database Principles Final', cs_class=csc3810, desc='A project to cover databases?', icon_path='../../static/projects/img/project-icons/database.png'))
        
        db.session.add(csc2620)
        db.session.add(csc3120)
        db.session.add(csc5055)
        db.session.add(csc3810)

        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()

    return Response(status = 200)

@projects.route('/classes', methods = ['GET'])
@login_required
def classes():
    '''
    Default route for accessing the projects page.

    NOTE = JWT authentication is required to access this page.
    '''
    classes = ComputerScienceClass.get_all_class_data()
    
    header_classes, user_data, tags = get_header_data()

    return render_template('/projects/classes.html', class_endpoints = classes, 
        user_data = user_data, header_classes = header_classes, tags = tags)

@projects.route('/classes/<id>', methods = ['GET'])
@login_required
def get_class(id: str):
    if id is None or ComputerScienceClass.query.get(id) is None:
        return render_template('errors/404.html')
    
    projects = Project.get_projects(id)
    header_classes, user_data, tags = get_header_data()

    return render_template('projects/projects.html', projects = projects, 
        user_data = user_data, header_classes = header_classes, tags = tags)

@projects.route('/projects/upload', methods = ['GET', 'POST'])
def upload_project():
    if request.method == 'GET':
        return render_template('projects/upload.html')
    else:
        body = request.form.to_dict()
        
        if 'project_zip' in request.files.keys():
            zip_file = request.files.get('project_zip')
        else:
            return "Zip file missing.", 400

        if 'icon_image' in request.files.keys():
            icon_image_path = upload_icon_image(request.files.get('icon_image'), 
                PROJECT_ICON_IMAGE_UPLOAD_FOLDER)

        # If the body contains all valid info and the zip file is present, extract the info.
        if field_check(body) and zip_file is not None:
            try:
                project_name = body['project_name']
                project_desc = body['project_desc']
                parent_class = body['parent_class']
                tags = body['tags']

                return insert_project(zip_file, project_name, project_desc, 
                    parent_class, tags, icon_image_path)
            except KeyError as e:
                print(e)
                return 'Missing project information', 400
        else:
            return 'Invalid data entered.', 400


@projects.route('/projects/create-tag', methods = ['POST'])
def create_tag():
    body = request.get_json()
    keys = body.keys()
    if body and 'tag_name' in keys and 'bg_color' in keys and 'text_color' in keys:
        new_tag = Tag(id=body['tag_name'], bg_color=body['bg_color'], text_color=body['text_color'])

        try:
            db.session.add(new_tag)
            db.session.commit()
        except:
            return "Tag already exists", 409

        return "Tag Successfully Created", 200
    else:
        return 'Missing information', 400

@projects.route('/classes/create-class', methods = ['POST'])
# @admin_required
def create_new_class():
    if request.method == 'POST':
        
        body = request.form.to_dict()
        
        if 'icon_image' in request.files.keys():
            img_path = upload_icon_image(request.files.get('icon_image'), 
                CLASS_ICON_IMAGE_UPLOAD_FOLDER)
        else:
            return "Icon Image missing.", 400

        if field_check(body):
            return create_class(body, img_path)
        else:
            return "Missing data.", 400

@projects.route('/projects/remove/<project_id>', methods = ['POST'])
@admin_required
def remove_project(project_id):
    return remove_project_from_db(project_id)

@projects.route('/classes/remove/<class_id>', methods = ['POST'])
@admin_required
def remove_class(class_id):
    return remove_class_from_db(class_id)

@projects.route('/projects', methods = ['GET'])
@login_required
def all_projects():
    user_data = session['user'].get_user_data()

    projects = Project.get_all_projects()
    header_classes = ComputerScienceClass.get_class_endpoints()
    user_data = session['user'].get_user_data()
    tags = Tag.get_all_tags()

    return render_template('projects/projects.html', projects = projects, 
        user_data = user_data, header_classes = header_classes, tags = tags)
    
@projects.route('/projects/<class_id>/<project_id>', methods = ['GET'])
@login_required
def get_project_structure(class_id, project_id):
    header_classes, user_data, tags = get_header_data()
    structure = get_structure(class_id, project_id)
    location_info = Project.get_project_path(class_id, project_id)
    download_endpoint = f'/projects/downloadproject/{project_id}'
    project_tags = Project.get_project_tags(project_id)
    print('project_id is: ', project_id)
    return render_template('projects/code.html', structure = structure, 
        user_data = user_data, header_classes = header_classes, tags = tags,
        location_info=location_info, download_endpoint = download_endpoint, 
        api_token = session['user'].api_token, project_tags = project_tags, 
        project_id = project_id)
    
@projects.route('/projects/code/<class_id>/<project_id>/<path:pars>', methods = ['GET'])
@login_required
def get_class_code(class_id: str, project_id: str, pars: str):
    if class_id is None or pars is None:
        return 404
    else:
        code_present, code = get_code(class_id, project_id, pars, session['user'].api_token) 
        response = make_response({'code_present': code_present, 'code': code}, 200)
        return response

@projects.route('/projects/raw/<class_id>/<project_id>/<path:pars>', methods = ['GET'])
@login_required
def raw_code(class_id, project_id, pars: str):
    if class_id and project_id and pars:
        content_loaded, raw_code = read_raw_code(class_id, project_id, pars, session['user'].api_token)
        return make_response({'content_loaded': content_loaded, 'raw_code': raw_code}, 200)
    else:
        return "Error with file path.", 400


@projects.route('/projects/download/<class_id>/<project_id>/<path:p>', methods = ['GET'])
def download_file(class_id: str, project_id: str, p: str):
    if 'Authorization' in request.headers and verify_api_token(request.headers.get('Authorization'), session['user'].username):
        if class_id and project_id and p:
            return get_download_response(class_id, project_id, p)
        else:
            return 'Missing information.', 400
    else:
        return "Invalid API Token", 401

@projects.route('/projects/downloadproject/<project_id>', methods = ['GET'])
def download_zip(project_id: str):
    if 'Authorization' in request.headers and verify_api_token(request.headers.get('Authorization'), session['user'].username):
        if project_id:
            return get_project_download(project_id)
        else:
            return 'Missing Information', 400
    else:
        return "Invalid API Token", 401

@projects.route('/projects/comments/<project_id>', methods = ['GET'])
def get_comments(project_id: str):
    return Project.query.get(project_id).jsonify_comments()

@projects.route('/projects/comments/add/<project_id>', methods = ['POST'])
def add_comment(project_id: str):
    body = request.get_json()
    if project_id and 'comment' in body:
        return insert_comment(body['comment'], project_id, 
            session['user'].username) 
    else:
        return "Missing information.", 400

@projects.route('/projects/bugs/add/<project_id>', methods = ['POST'])
def add_bug(project_id: str):
    
    body = request.get_json()
    if body and 'bug_name' in body and 'bug_desc' in body and project_id:
        return insert_bug(body['bug_name'], body['bug_desc'], project_id, 
            session['user'].username)
    else:
        return "Missing either bug_name or bug_desc.", 400

@projects.route('/projects/bugs/<project_id>')
def get_bugs(project_id: str):
    if project_id:
        return Project.query.get(project_id).jsonify_bugs()

@projects.route('/admin', methods = ['GET'])
def get_admin_page():
    header_classes, user_data, tags = get_header_data()
    return render_template('projects/admin.html', user_data = user_data, 
        header_classes = header_classes, tags = tags)
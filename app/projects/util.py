from argparse import ArgumentError
import os
from os.path import join, exists, realpath, isdir, normpath, basename
from os import mkdir
import uuid
from flask import Response
from werkzeug.utils import secure_filename
from app.models import ComputerScienceClass, Project, Tag, User, Comment, Issue
import zipfile
from app import db
from app.app_utils import db_insert, field_check
import base64

PROJECT_ICON_IMAGE_UPLOAD_FOLDER = realpath(
    os.getcwd() + '../../app/static/projects/img/project-icons')
CLASS_ICON_IMAGE_UPLOAD_FOLDER = realpath(
    os.getcwd() + '../../app/static/projects/img/class-icons')

PROJECTS_UPLOAD_FOLDER = realpath(os.getcwd() + '../../app/project-files')
PROJECTS_TEMP_UPLOAD_FOLDER = realpath(
    os.getcwd() + '../../app/project-files/zip-files')

ALLOWED_ICON_IMAGE_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def upload_icon_image(icon_image, upload_directory):
    extension = icon_image.filename.split('.')[1]

    # Make sure the uploaded file is of a valid type.
    if extension in ALLOWED_ICON_IMAGE_EXTENSIONS:
        icon_image_filename = str(uuid.uuid1()) + '.' + extension

        # Generate a unique name for the file, creating a new UUID until a unique one is found.
        while exists(upload_directory + '/' + icon_image_filename):
            icon_image_filename = str(uuid.uuid1()) + '.' + extension

        # Save the file.
        path = realpath(join(upload_directory,
                        secure_filename(icon_image_filename)))
        icon_image.save(path)

        if upload_directory is PROJECT_ICON_IMAGE_UPLOAD_FOLDER:
            return f'../../static/projects/img/project-icons/{icon_image_filename}'
        else:
            return f'../../static/projects/img/class-icons/{icon_image_filename}'
    else:
        return Response('Invalid file type.', 400)


def insert_project(zip_file, project_name: str, project_desc: str, parent_class: str, tags: list, icon_image_path: str):
    id = str(uuid.uuid1())
    path = join(PROJECTS_UPLOAD_FOLDER, parent_class, id)

    # Check to make sure the parent class exists in the database.
    parent_class_object = ComputerScienceClass.query.get(parent_class)
    if ComputerScienceClass.query.get(parent_class) is None:
        return "Parent project does not exist", 400

    # Check to make sure the parent directory is sound.
    if check_parent(parent_class):
        try:
            # Attempt to the directory for the project. If it already exists, there is a conflict.
            mkdir(path)
        except:
            return "A project with that name already exists.", 409

        # Save the zip file to /temp, then unzip it to the path.
        # Create a new Project object, then commit it to the database.
        if icon_image_path:
            new_project = Project(id=id, desc=project_desc, name=project_name,
                                  path=path, cs_class=parent_class_object,
                                  icon_path=icon_image_path)
        else:
            new_project = Project(id=id, desc=project_desc, name=project_name,
                                  path=path, cs_class=parent_class_object)

        temp_file_path = join(PROJECTS_TEMP_UPLOAD_FOLDER, id + '.zip')
        zip_file.save(temp_file_path)
        with zipfile.ZipFile(temp_file_path) as zip:
            zip.extractall(path)

        # If the project has been successfully inserted, process the tags.
        if db_insert(new_project):
            # Parse the tags, then check to make sure each tag exists. If it does not, make a new tag.
            # Strip any unnecessary characters off the string and split into array.
            if len(tags) > 0:
                tags = tags.replace(' ', '').replace(
                    '[', '').replace(']', '').replace('\'', '').split(',')
                for tag in tags:
                    if not Tag.tag_exists(tag):
                        new_tag = Tag(id=tag)
                        if db_insert(new_tag):
                            new_project.tags.append(new_tag)

                            # Recommit the new project after every new tag attachment.
                            db.session.add(new_project)
                            db.session.commit()

            return 'Successfully uploaded', 200
        else:
            return "Error while uploading new project", 500

    else:
        return "Error while uploading new project", 500


def check_parent(parent_class_name: str, recursion_count=0) -> bool:
    '''
    Checks to see if the parent class directory exists. If it does not, a new directory is created.

    param: parent_class_name The name of the parent directory.
    param: recursion_count A counter for the number of recursive calls. Will not run if recursion_count exceeds 5.
    returns: A boolean representing whether or not the directory exists after attempting possible creation.
    '''

    # Check to stop infinite recursion.
    if recursion_count > 5:
        return False

    parent_class_dir = join(PROJECTS_UPLOAD_FOLDER, parent_class_name)
    if isdir(parent_class_dir):
        return True
    else:
        try:
            # Attempt to create the directory, then recall the function to check the existence.
            mkdir(parent_class_dir)
            return check_parent(parent_class_name, recursion_count + 1)
        except:
            return False


def remove_class_from_db(class_id: str) -> tuple:
    if class_id:
        # Get the class from the database.
        cs_class = ComputerScienceClass.query.get(class_id)

        if cs_class:
            all_projects = Project.query.all()
            class_projects = []

            # Loop over every project, checking to see if it is in this class.
            for project in all_projects:
                if project.cs_class.id == class_id:
                    class_projects.append(project)

            # Delete every project that lives in the class.
            for project in class_projects:
                db.session.delete(project)

            # Delete the class itself.
            db.session.delete(cs_class)
            db.session.commit()

            return 'Success', 200
        else:
            return 'Class does not exist.', 400
    else:
        return 'Unknown class ID.', 400


def remove_project_from_db(project_id: str) -> tuple:
    import shutil

    if project_id:
        project = Project.query.get(project_id)

        if project:
            shutil.rmtree(project.path, ignore_errors=True)
            os.remove(join(PROJECTS_TEMP_UPLOAD_FOLDER, project_id + '.zip'))
            db.session.delete(project)
            db.session.commit()
            return 'Success', 200
        else:
            return 'Unknown project.', 400
    else:
        return 'Unknown project ID.', 400


def get_structure(class_id: str, project_id: str):
    project_path = join(PROJECTS_UPLOAD_FOLDER, class_id, project_id)

    return_list = traverse_directory(
        f'/projects/code/{class_id}/{project_id}', [], os.scandir(project_path))

    # Courtesy of: https://stackoverflow.com/questions/71865481/custom-sorting-a-python-list-with-nested-dictionaries/
    def sort_list(lst):
        folders = list(filter(lambda o: len(o) == 1, lst))
        files = list(filter(lambda o: len(o) != 1, lst))
        for folder in folders:
            name, inner_lst = next(iter(folder.items()))
            folder[name] = sort_list(inner_lst)
        sorted_folders = sorted(folders, key=lambda e: next(iter(e.keys())))
        sorted_files = sorted(files, key=lambda e: e['file_name'])
        return sorted_folders + sorted_files

    return_list = sort_list(return_list)
    return return_list


def traverse_directory(endpoint_path, return_list, dir):
    for file in dir:
        if file.is_file():
            file_dict = {
                'file_name': file.name,
                'endpoint': f'{endpoint_path}/{file.name}'
            }
            return_list.append(file_dict)
        else:
            end_file_path = endpoint_path + '/' + file.name
            dir_dict = {
                f'{file.name}': traverse_directory(end_file_path, [], os.scandir(file.path))
            }
            return_list.append(dir_dict)
    return return_list


def create_class(class_data: dict, icon_path):
    if class_data and icon_path:
        try:
            id = class_data['id']
            class_title = class_data['class_title']
            desc = class_data['desc']
            db.session.add(ComputerScienceClass(
                id=id, class_title=class_title, icon_path=icon_path, desc=desc))
            db.session.commit()
            return "Success", 200
        except KeyError:
            return "Missing fields.", 400
        except Exception as e:
            print(e)
            return "Class already exists.", 409
    return "Server Error", 500


def get_code(class_id: str, project_id: str, path: str, api_token: str):
    from pygments import highlight
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import get_lexer_for_filename

    file_extension = path.split('.')[1]
    if file_extension in ALLOWED_ICON_IMAGE_EXTENSIONS:
        with open(normpath(join(PROJECTS_UPLOAD_FOLDER, class_id, project_id, path)), "rb") as img_file:
            return False, f'<img width="100%" src="data:image/{file_extension};base64,{base64.b64encode(img_file.read()).decode("utf-8")}"></img>'
    else:
        try:
            with open(normpath(join(PROJECTS_UPLOAD_FOLDER, class_id, project_id, path))) as file:
                contents = file.read()
                filename = basename(file.name)
                formatter = HtmlFormatter(style='emacs')
                formatter.noclasses = True
                return True, f'<div style="display: flex; justify-content: space-between; width: 100%">{highlight(contents, get_lexer_for_filename(filename), formatter)}<button class="btn mx-1" style="margin-top: 5px; margin-left: auto; max-height: 40px;" onclick="downloadFile(\'/projects/download/{class_id}/{project_id}/{path}\', \'{api_token}\')"><i class="fa fa-download" style="margin-right: 4px"></i>Download File</button></div>'
        except:
            raw_path = f'/projects/raw/{class_id}/{project_id}/{path}'
            btn = f'<button class="btn" type="button" onclick="getRawContent(\'{raw_path}\')">View Raw Content</button>'
            return False, f'<div style="display: block; justify-content: center; text-align: center;"><h4 style="margin: 10px">Unsupported file type :(</h4>{btn}</div>'


def read_raw_code(class_id, project_id, path: str, api_token: str):
    try:
        with open(normpath(join(PROJECTS_UPLOAD_FOLDER, class_id, project_id, path)), newline='') as file:
            return True, f'<div style="display: flex; justify-content: space-between; width: 100%">{file.read()}<button class="btn mx-1" style="margin-top: 5px; margin-left: auto; max-height: 40px;" onclick="downloadFile(\'/projects/download/{class_id}/{project_id}/{path}\', \'{api_token}\')"><i class="fa fa-download" style="margin-right: 4px"></i>Download File</button></div>'
    except:
        return False, f'<div style="display: flex; justify-content: space-between; width: 100%"><h4 style="margin: 10px">Unable to load file, please try downloading it.</h4><button class="btn mx-1" style="margin-top: 5px; margin-left: auto; max-height: 40px;" onclick="downloadFile(\'/projects/download/{class_id}/{project_id}/{path}\', \'{api_token}\')"><i class="fa fa-download" style="margin-right: 4px"></i>Download File</button></div>'


def verify_api_token(token, username) -> bool:
    if token and username:
        expected_token = User.query.filter_by(
            username=username).first().api_token
        return expected_token == token
    else:
        raise ArgumentError('Token or username was missing.')


def get_download_response(class_id, project_id, path):
    from requests_toolbelt import MultipartEncoder
    import magic
    mime = magic.Magic(mime=True)
    path = join(PROJECTS_UPLOAD_FOLDER, class_id, project_id, path)
    if exists(normpath(path)):
        split_path = normpath(path).split('\\')
        multipart = MultipartEncoder(
            fields={
                'filename': split_path[len(split_path) - 1],
                'file': ('filename', open(path, 'rb'), mime.from_file(path))
            }
        )

        return multipart.to_string(), 200, {
            'Content-Type': multipart.content_type
        }
    else:
        return "File not Found", 400


def get_project_download(project_id: str):
    from requests_toolbelt import MultipartEncoder
    import magic
    mime = magic.Magic(mime=True)
    path = join(PROJECTS_UPLOAD_FOLDER, f'zip-files/{project_id}.zip')

    if exists(normpath(path)):
        multipart = MultipartEncoder(
            fields={
                'filename': Project.query.get(project_id).name.replace(' ', '_'),
                'file': ('filename', open(path, 'rb'), mime.from_file(path))
            }
        )

        return multipart.to_string(), 200, {
            'Content-Type': multipart.content_type
        }
    else:
        return "File not Found", 400


def insert_comment(text: str, parent_project_id: str, username: str):
    if field_check({'text': text, 'parent_project': parent_project_id, 'username': username}):
        all_ids = Comment.get_all_ids()
        new_id = str(uuid.uuid1())

        while new_id in all_ids:
            new_id = str(uuid.uuid1())

        parent_project = Project.query.get(parent_project_id)

        if parent_project:
            new_comment = Comment(id=new_id, username=username, text=text,
                                  parent_project=parent_project.id)
            parent_project.comments.append(new_comment)

            # Add the new comment to the user's list of comments.
            user = User.query.filter_by(username=username).first()
            user.comments.append(new_comment)

            try:
                if db_insert(new_comment) and db_insert(parent_project) and db_insert(user):
                    return "Success", 200
                else:
                    return "Error while adding comment.", 500
            except:
                return "Error while adding comment.", 500
        else:
            return "Parent project does not exist.", 400


def insert_bug(bug_name: str, bug_desc: str, parent_project_id: str, username: str):
    if field_check({'bug_name': bug_name, 'bug_desc': bug_desc,
                    'project_id': parent_project_id, 'username': username}):
        all_ids = Issue.get_all_ids()
        new_id = str(uuid.uuid1())

        while new_id in all_ids:
            new_id = str(uuid.uuid1())

        parent_project = Project.query.get(parent_project_id)

        if parent_project:
            new_bug = Issue(id=new_id, username=username, bug_name=bug_name,
                            bug_desc=bug_desc, parent_project=parent_project.id)
            parent_project.issues.append(new_bug)

            # Add the new comment to the user's list of comments.
            user = User.query.filter_by(username=username).first()
            user.issues.append(new_bug)

            try:
                if db_insert(new_bug) and db_insert(parent_project) and db_insert(user):
                    return 'Success', 200
                else:
                    return 'Error while adding issue.', 500
            except:
                return 'Error while adding issue.', 500
        else:
            return 'Parent project does not exist.', 400

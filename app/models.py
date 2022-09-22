from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, jsonify
from app import db
from flask_login import UserMixin
from werkzeug.security import check_password_hash
import logging as logger
from app.app_utils import is_whitespace
from datetime import timezone

# Maps a user to their issues.
user_issues_mapper = db.Table('user_issues_mapper',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('issue_id', db.Integer, db.ForeignKey('issues.id'), primary_key=True)
)

# Maps a user to their comments.
user_comments_mapper = db.Table('user_comments_mapper',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('comments_id', db.Integer, db.ForeignKey('comments.id'), primary_key=True)
)

# Maps classes to projects.
class_project_mapper = db.Table('class_project_mapper',
    db.Column('class_id', db.Integer, db.ForeignKey('classes.id'), primary_key=True),
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True)
)

# Maps projects to comments.
project_comment_mapper = db.Table('project_comment_mapper',
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True),
    db.Column('comment_id', db.Integer, db.ForeignKey('comments.id'), primary_key=True)
)

# Maps projects to issues.
project_issue_mapper = db.Table('project_issue_mapper',
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True),
    db.Column('issue_id', db.Integer, db.ForeignKey('issues.id'), primary_key=True)
)

# Maps projects to tags.
project_tag_mapper = db.Table('project_tag_mapper',
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)

class ComputerScienceClass(db.Model):
    '''
    Holds all data for a specific computer science class.
    '''
    __tablename__ = 'classes'
    id = db.Column(db.String(7), primary_key=True)
    class_title = db.Column(db.String(120), unique=True, nullable=False)
    icon_path = db.Column(db.String(100), nullable=False, default ='../../static/projects/img/default.jpg')
    desc = db.Column(db.Text, nullable=True)

    def __repr__(self):
        '''
        Returns a representation of the CS class.
        '''
        return self.id + ' - ' + self.class_title

    def get_class_endpoints() -> list:
        '''
        Returns all classes and an endpoint associated with each of them.

        return: A list of dicts that follows the format: \n
        
        [
            {
                "class_name": "Intro to Computer Science",
                "endpoint": "/classes/CSC1610",
                "icon_path": "../../static/classes/img/class_icons/intro.jpg"
            }
        ]
        '''
        return_json = []
        all_classes = ComputerScienceClass.query.all()
        for clazz in all_classes:
            clazz_dict = {}
            clazz_dict['class_name'] = clazz.class_title
            clazz_dict['endpoint'] = f'/classes/{clazz.id}'
            clazz_dict['icon_path'] = clazz.icon_path
            clazz_dict['desc'] = clazz.desc
            clazz_dict['remove_endpoint'] = f'/classes/remove/{clazz.id}'
            clazz_dict['class_string'] = f'{clazz.id} - {clazz.class_title}'
            return_json.append(clazz_dict)
        return return_json

    def get_all_class_data() -> list:
        '''
        Returns all classes with their associated projects, with endpoints.
        '''
        project_map = {}
        return_json = []
        
        '''
        Loop over every project in the database, adding it a dictionary
        organized by class. If the class doesn't exist, create a list in the
        dict and add that class. 
        '''
        projects = Project.query.all()
        for project in projects:
            current_class = project.cs_class.id
            if current_class not in project_map:
                project_map[current_class] = []     
            project_map[current_class].append(project)

        for key in project_map:
            current_class = {}
            current_class['class_id'] = key
            current_class['class_title'] = ComputerScienceClass.query.get(key).class_title
            current_class['projects'] = []
            for project in project_map[key]:
                current_project = {}
                current_project['name'] = project.name
                current_project['endpoint'] = f'/projects/{key}/{project.id}'

                project_comments = project.comments
                project_issues = project.issues
                project_tags = project.tags

                if project_comments is None:
                    num_comments = 0
                else:
                    num_comments = len(project_comments)

                if project_issues is None:
                    num_issues = 0
                else:
                    num_issues = len(project_issues)

                if project_tags is None:
                    num_tags = 0
                else:
                    num_tags = len(project_tags)
                    
                current_project['num_comments'] = num_comments
                current_project['num_issues'] = num_issues
                current_project['num_tags'] = num_tags
                current_class['projects'].append(current_project)
            current_class['num_projects'] = len(current_class['projects'])
            return_json.append(current_class)

        return return_json
        

class User(UserMixin, db.Model):
    '''
    Implementation for a user. Holds all data necessary for authentication, API requests, and issues/comments 
    associated with the user.
    '''
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), nullable=False, unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    hash = db.Column(db.String(60), nullable=False)
    issues = db.relationship('Issue', secondary=user_issues_mapper, lazy='subquery',
        backref=db.backref('issues', lazy=True), uselist=True)
    comments = db.relationship('Comment', secondary=user_comments_mapper, lazy='subquery',
        backref=db.backref('comments', lazy=True), uselist=True)
    totp_key = db.Column(db.String(255), nullable=False)
    api_token = db.Column(db.String(60), nullable=False, unique=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)


    def get_user_data(self):
        '''
        Jsonifies the user's information.
        '''
        return_dict = {}
        return_dict['username'] = self.username
        return_dict['email'] = self.email
        return_dict['creation_date'] = self.creation_date.strftime("%Y-%m-%d %H:%M %p")
        return_dict['issues'] = self.issues
        return_dict['comments'] = self.comments
        return_dict['api_token'] = self.api_token
        return_dict['is_admin'] = self.is_admin
        return return_dict

    def get_reset_token(self, duration=1800) -> str:
        '''
        Gets a reset token for the given user.
        
        param: duration=1800 The amount of time the token is valid for.
        return: The token represented as a string.
        '''
        return Serializer(current_app.config['SECRET_KEY'], duration).dumps(
            {'username': self.username}).decode('utf-8')


    def verify_reset_token(token: str):
        '''
        Verifies if a reset token is valid or not. 
        
        param: The token to check.
        return: The user associated with the token.
        '''
        if not token or is_whitespace(token):
            logger.warn('Attempted to verify reset token with no username present.')

        try:
            username = Serializer(current_app.config['SECRET_KEY']).loads(token)[
                'username']
        except Exception as e:
            return None

        return User.query.filter_by(username=username).first()


    def verify_password(self, password: str) -> bool:
        '''
        Verifies a password against the hash stored in the database.
        
        param: The password to check.
        return: A boolean representing if the password matches the hash or not.
        '''
        return check_password_hash(self.hash, password)


    def is_active():
        '''
        Returns whether or not the user is active.
        '''
        return True


class Project(db.Model):
    '''
    Implementation for a project. Holds all the necessary data such as the class it belongs to, the issues
    it has, and the comments/tags associated with it.
    '''
    __tablename__ = 'projects'
    id = db.Column(db.String(255), primary_key=True)
    desc = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    path = db.Column(db.Text, unique=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    icon_path = db.Column(db.Text, nullable=False, default='../../static/projects/img/project-icons/default.jpeg')
    cs_class = db.relationship('ComputerScienceClass', secondary=class_project_mapper, lazy='subquery',
        backref=db.backref('cs_class', lazy=True), uselist=False)
    issues = db.relationship('Issue', secondary=project_issue_mapper, lazy='subquery',
        backref=db.backref('project_issues', lazy=True), uselist=True)
    comments = db.relationship('Comment', secondary=project_comment_mapper, lazy='subquery',
        backref=db.backref('project_comments', lazy=True), uselist=True)
    tags = db.relationship('Tag', secondary=project_tag_mapper, lazy='subquery',
        backref=db.backref('project_tags', lazy=True), uselist=True)

    def get_projects(class_id):
        return_dict = {}
        class_info = []

        parent_class = ComputerScienceClass.query.get(class_id)
        class_info.append({
            'name': 'Classes',
            'endpoint': '/classes'
        })
        class_info.append({
            'name': str(parent_class),
            'endpoint': f'/classes/{parent_class.id}'
        })
        return_dict['class_info'] = class_info
        
        class_projects = Project.query.all()
        projects_list = []
        for project in class_projects:
            if project.cs_class.id == class_id:
                project_dict = {}
                project_dict['project_name'] = project.name
                project_dict['desc'] = project.desc
                project_dict['endpoint'] = f'/projects/{class_id}/{project.id}'
                project_dict['icon_path'] = project.icon_path
                project_dict['remove_endpoint'] = f'/projects/remove/{project.id}'
                projects_list.append(project_dict)
        return_dict['projects'] = projects_list
        return return_dict

    def get_all_projects():
        all_projects = Project.query.all()
        projects_list = []
        return_dict = {}
        for project in all_projects:
            project_dict = {}
            project_dict['project_name'] = project.name
            project_dict['desc'] = project.desc
            project_dict['endpoint'] = f'/projects/{project.cs_class.id}/{project.id}'
            project_dict['icon_path'] = project.icon_path
            project_dict['remove_endpoint'] = f'/projects/remove/{project.id}'
            projects_list.append(project_dict)
        return_dict['projects'] = projects_list
        return return_dict

    def get_project_path(class_id, project_id):
        location_info = []
        project = Project.query.get(project_id)
        parent_class = project.cs_class
        location_info.append({
            'name': 'Classes',
            'endpoint': '/classes'
        })
        location_info.append({
            'name': str(parent_class),
            'endpoint': f'/classes/{parent_class.id}'
        })
        location_info.append({
            'name': project.name,
            'endpoint': f'/projects/{parent_class.id}/{project.id}'
        })
        return location_info

    def get_project_tags(project_id: str):
        project_tags = list(Project.query.get(project_id).tags)

        return list(map(lambda t: { 'name': t.id, 'endpoint': f'/tags/{t.id}', 
            'bg_color': t.bg_color, 'text_color': t.text_color}, project_tags))

    def jsonify_comments(self):
        return jsonify(list(map(lambda comment: {
            'likes': comment.likes, 
            'username': comment.username, 
            'date': (comment.date.isoformat()), 
            'text': comment.text
        }, self.comments))), 200

    def jsonify_bugs(self):
        return jsonify(list(map(lambda bug: {
            'date': (bug.date.isoformat()),
            'username': bug.username,
            'bug_name': bug.bug_name,
            'bug_desc': bug.bug_desc
        }, self.issues)))

class Comment(db.Model):
    '''
    Implementation for a Comment which can be put on projects or issues.
    '''
    __tablename__ = 'comments'
    id = db.Column(db.String(255), primary_key=True)
    likes = db.Column(db.Integer, nullable=False, default=0)
    username = db.Column(db.String(25), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    text = db.Column(db.Text, nullable=False)
    parent_project = db.Column(db.String(255), db.ForeignKey('projects.id'))


    def get_all_ids():
        return list(map(lambda comment: comment.id, Comment.query.all()))

class Issue(db.Model):
    '''
    Implementation for an issue which can be put on a project.
    '''
    __tablename__ = 'issues'
    id = db.Column(db.String(255), primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    username = db.Column(db.String(25), nullable=False)
    bug_name = db.Column(db.String(200), nullable=False)
    bug_desc = db.Column(db.Text, nullable=False)
    parent_project = db.Column(db.String(255), db.ForeignKey('projects.id'))

    def get_all_ids():
        return list(map(lambda issue: issue.id, Issue.query.all()))

class Tag(db.Model):
    '''
    ORM Implementation for a single tag on a comment/project.
    '''
    __tablename__ = 'tags'
    id = db.Column(db.String(120), primary_key=True)
    bg_color = db.Column(db.String(20), nullable=False, default='white')
    text_color = db.Column(db.String(20), nullable=False, default='black')
    
    def tag_exists(tag: str) -> bool:
        all_tags = [tag.id for tag in Tag.query.all()]
        return (tag in all_tags)

    def get_all_tags():
        '''
        Returns a list of all the tags in the database. The format is as follows:

        {
            'endpoint': '/tags/java',
            'tag_name': 'Java'
        }
        '''
        return_list = []
        tags = Tag.query.all()
        for tag in tags:
            tag_dict = {}
            tag_dict['endpoint'] = f'/tags/{tag.id}'
            tag_dict['tag_name'] = tag.id.title()
            tag_dict['bg_color'] = tag.bg_color
            tag_dict['text_color'] = tag.text_color
            return_list.append(tag_dict)
        return return_list

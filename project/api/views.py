# -*- coding:Utf8 -*-
# project/api/views.py


from functools import wraps
import datetime

# Api using flask_restful
from flask import flash, redirect, session, url_for
from flask_restful import Resource, reqparse, abort

# Api by hands using blueprint.
# from flask import flash, redirect, jsonify, session, url_for, Blueprint, make_response

from project import db, bcrypt
from project.models import Task, User


# Parseur
parser = reqparse.RequestParser()
parser.add_argument('name', type=str)
parser.add_argument('user_name', type=str)
parser.add_argument('password', type=str)
parser.add_argument('due_date', type=str)
parser.add_argument('priority', type=int)


# Tools
# def login_required(page):
#     """
#         Used as a decorator. It ensure that user is login before
#         let him access to the decorated route.
#     """
#     @wraps(page)
#     def wrapper(*args, **kwargs):
#         if 'logged_in' in session:
#             return page(*args, **kwargs)
#         else:
#             flash('You need to login first.')
#             return redirect(url_for('users.login'))
#     return wrapper


def open_tasks():
    return db.session.query(Task).filter_by(status='1').order_by(Task.due_date.asc())


def closed_tasks():
    return db.session.query(Task).filter_by(status='0').order_by(Task.due_date.asc())


def abort_if_task_doesnt_exist(task_id, result):
    """
        Abort api demand if task_id does not exist.
    """
    if not result or task_id != result.task_id:
        abort(404, message="error: Element does not exist")


def abort_if_user_doesnt_exist(user, password):
    """
        Abort api demand if user name does not exist.
    """
    if user is None or not bcrypt.check_password_hash(user.password, password):
        abort(401, message="error: User does not exist")


def abort_if_wrong_priority(priority):
    """
        Abort api demand if wrong priority number.
    """
    if type(priority) != int or priority > 10 or priority < 1:
        abort(400, message="error: priority must be between 1 and 10 included")


# Routes

class ApiTasks(Resource):
    """
        Overload Api base class Resource.
    """
    def get(self):
        results = db.session.query(Task).limit(10).offset(0).all()
        json_results = []
        for result in results:
            data = {'task_id': result.task_id,
                    'task name': result.name,
                    'due date': str(result.due_date),
                    'priority': result.priority,
                    'posted date': str(result.posted_date),
                    'status': result.status,
                    'user id': result.user_id
                    }
            json_results.append(data)
        # Call of jsonify() by flask_restful.
        return json_results, 200

    def post(self):
        """
            Add Rest operation: POST.
        """
        # Recup arguments.
        args = parser.parse_args()
        # Recup user and password.
        user = User.query.filter_by(name=args['user_name']).first()
        password = args['password']
        # Test if user and password match.
        abort_if_user_doesnt_exist(user, password)
        # Convert date to correct datetime.date type.
        date = datetime.datetime.strptime("22/4/3245", '%d/%m/%Y')
        # Check priority and avoid priority > 10 or smaller than 1.
        priority = args["priority"]
        abort_if_wrong_priority(priority)

        # Create dict of parameters for Task creator.
        dict_task = {'name': args["name"],
                     'due_date': date,
                     'posted_date': datetime.datetime.utcnow(),
                     'priority': priority,
                     'status': 1,
                     'user_id': user.user_id
                     }
        # Create new task.
        new_task = Task(**dict_task)
        db.session.add(new_task)
        db.session.commit()
        user_added_dict = {data: dict_task[data] if "date" not in data
                           else str(dict_task[data]) for data in dict_task}
        return user_added_dict, 201


class ApiTaskId(Resource):
    """
        Overload Api base class Resource.
        Api on direct task id.
        Support for GET, PUT, and DELETE.
        Only GET working for now, other support will be add in the future.
    """
    def get(self, task_id):
        result = db.session.query(Task).filter_by(task_id=task_id).first()
        abort_if_task_doesnt_exist(task_id, result)
        json_result = {'task_id': result.task_id,
                       'task name': result.name,
                       'due date': str(result.due_date),
                       'priority': result.priority,
                       'posted date': str(result.posted_date),
                       'status': result.status,
                       'user id': result.user_id
                       }
        # Call of jsonify by flask_restful.
        return json_result, 200

    def put(self):
        pass

    def delete(self):
        pass




################################################################################
# # Equivalent by hands

# # Config
# api_blueprint = Blueprint("api", __name__)

# @api_blueprint.route("/api/v1/tasks/")
# def api_tasks():
#     results = db.session.query(Task).limit(10).offset(0).all()
#     json_results = []
#     for result in results:
#         data = {'task_id': result.task_id,
#                 'task name': result.name,
#                 'due date': str(result.due_date),
#                 'priority': result.priority,
#                 'posted date': str(result.posted_date),
#                 'status': result.status,
#                 'user id': result.user_id
#                 }
#         json_results.append(data)
#     # jsonify allows beautiful code. Avoid code below.
#     # return json.dumps(json_results), 200, { "Content-Type" :"application/json"}
#     return jsonify(items=json_results)


# @api_blueprint.route("/api/v1/tasks/<int:task_id>")
# def task(task_id):
#     result = db.session.query(Task).filter_by(task_id=task_id).first()
#     if result:
#         json_result = {'task_id': result.task_id,
#                        'task name': result.name,
#                        'due date': str(result.due_date),
#                        'priority': result.priority,
#                        'posted date': str(result.posted_date),
#                        'status': result.status,
#                        'user id': result.user_id
#                        }
#         code = 200
#     else:
#         json_result = {"error": "Element does not exist"}
#         code = 404
#     return make_response(jsonify(json_result), code)

from flask import Blueprint, current_app, render_template, request, jsonify
from users import User
from mylogger import clog
import json
views = Blueprint('views', __name__)


@views.route("/", methods=['POST', 'GET'])
def dashboard():
    user: User = current_app.config["context"]
    if request.method == 'POST':
        clog.critical(f"Request")
        # if request.form.get('action1') == 'VALUE1':
        #     pass # do something
        # elif  request.form.get('action2') == 'VALUE2':
        #     pass # do something else
        # else:
        #     pass # unknown
    return render_template('dashboard.html', user=user)

@views.route("/request", methods=['POST'])
def request_resource():
    user: User = current_app.config["context"]
    data = json.loads(request.data)
    resource_id = str(data['resource_id'])
    user.requested_resources.update({resource_id})
    return jsonify({})
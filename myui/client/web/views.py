import json
from queue import Queue

from client.handlers.request_handler import (RequestHandlerThread,
                                             ResourceRelease, ResourceRequest)
from com import message
from com.header import Header
from flask import Blueprint, current_app, jsonify, render_template, request
from mylogger import clog
from users import User

views = Blueprint('views', __name__)


@views.route("/", methods=['POST', 'GET'])
def dashboard():
    user: User = current_app.config["context"]
    return render_template('dashboard.html', user=user)


@views.route("/requested-resources-update", methods=['POST'])
def requestedResourcesUpdate():
    user: User = current_app.config["context"]
    data = json.loads(request.data)
    clog.debug(data)
    resource_id = str(data['resource_id'])
    selected = data['selected']
    if selected:
        user.requested_resources.update({resource_id})
    else:
        try:
            user.requested_resources.remove(resource_id)
        except KeyError:
            # not requested
            pass
    clog.info(f"Requested resources: {user.requested_resources}")
    return jsonify({})


@views.route("/request-resources", methods=['POST'])
def requestResource():
    user: User = current_app.config["context"]
    request_thread: RequestHandlerThread = current_app.config["request_thread"]
    clog.info(f"Requesting resources: {user.requested_resources}")
    req = ResourceRequest(user, user.requested_resources)
    request_thread.handle_request(req)

    return jsonify({})


@views.route("/free-resources", methods=['POST'])
def freeResource():
    user: User = current_app.config["context"]
    request_thread: RequestHandlerThread = current_app.config["request_thread"]
    clog.info(f"Freeing resources: {user.requested_resources}")
    req = ResourceRelease(user)
    request_thread.handle_request(req)

    return jsonify({})

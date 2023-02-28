# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import render_template, redirect, request, url_for, session, current_app
from flask_login import (
    current_user,
    login_user,
    logout_user
)
from flask_dance.contrib.github import github

from apps import db, login_manager
from apps.msal import blueprint
# from apps.msal.forms import LoginForm, CreateAccountForm
# from apps.msal.models import Users

import identity, identity.web

import requests

auth = identity.web.Auth(
    session=session,
    authority=current_app.config.get("AUTHORITY"),
    client_id=current_app.config["CLIENT_ID"],
    client_credential=current_app.config["CLIENT_SECRET"],
)


@blueprint.route('/')
def route_default():
    return redirect(url_for('msal_blueprint.login_ms'))

@blueprint.route("/login_ms")
def login():
    return render_template("login.html", version=identity.__version__, **auth.log_in(
        scopes=current_app.config.SCOPE,  # Have user consent scopes during log-in
        redirect_uri=url_for("auth_response", _external=True),  # Optional. If present, this absolute URL must match your app's redirect_uri registered in Azure Portal
        ))

@blueprint.route(current_app.config["REDIRECT_PATH"])
def auth_response():
    result = auth.complete_log_in(request.args)
    return render_template("auth_error.html", result=result) if "error" in result else redirect(url_for("index"))

@blueprint.route("/logout_ms")
def logout():
    return redirect(auth.log_out(url_for("index", _external=True)))

@blueprint.route("/call_downstream_api")
def call_downstream_api():
    token = auth.get_token_for_user(current_app.config.SCOPE)
    if "error" in token:
        return redirect(url_for("login"))
    api_result = requests.get(  # Use token to call downstream api
        current_app.config.ENDPOINT,
        headers={'Authorization': 'Bearer ' + token['access_token']},
        ).json()
    return render_template('display.html', result=api_result)
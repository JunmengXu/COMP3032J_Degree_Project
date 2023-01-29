from flask import render_template, flash, redirect, session, url_for, request, jsonify, current_app

def not_found(e):
    return render_template('error/404.html'),404 #synchronization_update@2 (app/__init__.py)

def internal_server_error(e):
    return render_template('error/500.html'),500 #synchronization_update@3 (app/__init__.py)
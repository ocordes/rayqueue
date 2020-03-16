"""

app/social/flickr.py

written by: Oliver Cordes 2020-03-06
changed by: Oliver Cordes 2020-03-07

"""

import os
from datetime import datetime

from flask import request, render_template, url_for, flash,  \
                  redirect, send_from_directory, jsonify, session, g
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse, url_unparse


from app import db
from app.social import bp
from app.models import *

import flickr_api

flickr_auth_collection = {}


@bp.route('/social/flickr_upload', methods=['GET'])
@login_required
def flickr_upload():
    if ('flickr_caller' not in session) or (session['flickr_caller'] is None):
        session['flickr_caller'] = request.referrer


    flickr_avail = 'flickr_avail' in session

    flickr_retry = session.get('flickr_retry', 0)

    if flickr_retry >= 3:
        if 'flickr_retry' in session:
            session.pop('flickr_retry')
        flash('Max. retry for flickr authentication reached!')
        return redirect(url_for('main.index'))

    if not flickr_avail:
        current_app.logger.info('{}: no flickr token available! Starting Oauth process!'.format(current_user.username))
        print('No flickr token available! Starting Oauth process!')

        api_key = '0d648affadf9a0e7992dadbc63f49c3b'
        api_secret = '36122fdc7b26fda2'

        flickr_api.set_keys(api_key=api_key, api_secret=api_secret)


        up = url_parse(request.base_url)
        s = url_unparse((up.scheme,up.netloc,url_for('social.flickr_oauth'),'',''))

        a = flickr_api.auth.AuthHandler(callback=s)

        url = a.get_authorization_url('write')

        flickr_auth_collection[current_user.username] = a

        session['flickr_retry'] = flickr_retry + 1


        return redirect(url)
    else:
        with open('data/images/b6f5049d-dc2a-4406-8092-2cb4585bddcc_scene.png', 'rb') as f:
            print('File open')

            if current_user.username in flickr_auth_collection:
                flickr_api.auth.set_auth_handler(flickr_auth_collection[current_user.username])
                flickr_api.upload(photo_file = "some file name", title = "My title", photo_file_data=f)
                flickr_api.auth.set_auth_handler(None)
            else:
                if 'flickr_avail' in session:
                    session.pop('flickr_avail')


    # clean all cookies, and more of less, destroy the oauth
    # since we don't know how long the token is valid!
    if 'flickr_caller' in session:
        url = session.pop('flickr_caller')
    else:
        url = url_for('main.index')

    if 'flickr_avail' in session:
        session.pop('flickr_avail')

    if 'flickr_retry' in session:
        session.pop('flickr_retry')

    # destroy the old handler it available
    if flickr_api.auth.AUTH_HANDLER is not None:
        del flickr_api.auth.AUTH_HANDLER
        flickr_api.auth.AUTH_HANDLER = None

    if current_user.username in flickr_auth_collection:
        flickr_auth_collection.pop(current_user.username)

    return redirect(url)


@bp.route('/social/flickr_oauth', methods=['GET'])
@login_required
def flickr_oauth():
    data = request.args

    flickr_handler = flickr_auth_collection.get(current_user.username, None)

    if flickr_handler is not None:
        try:
            flickr_handler.set_verifier(data['oauth_verifier'])
            session['flickr_avail'] = 'True'
            #if current_user.username in flickr_auth_collection:
            #    flickr_auth_collection[current_user.username] = 0
            current_app.logger.info('{}: flickr token verified'.format(current_user.username))
        except:
            current_app.logger.info('{}: flickr token not verified'.format(current_user.username))

        #return render_template('facebook.html', title='Facebook-Test')
        return redirect(url_for('social.flickr_upload'))
    else:
        current_app.logger.info('{}: flickr handler not available'.format(current_user.username))
        return redirect(url_for('main.index'))

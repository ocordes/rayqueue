"""

app/social/piwigo.py

written by: Oliver Cordes 2020-03-28
changed by: Oliver Cordes 2020-03-29

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

from app.social.forms import UploadPiwigoForm, AuthPiwigoForm

# modules for piwigo
from piwigo import Piwigo
import requests


@bp.route('/social/piwigo_upload', methods=['GET', 'POST'])
@login_required
def piwigo_upload():

    uform = UploadPiwigoForm(prefix='Upload')


    # check if we are called from a POST request, then extract
    # the variables
    if uform.validate_on_submit():
        #print('POST request')
        #print('imageid:', uform.imageid.data)
        session['piwigo_imageid'] = uform.imageid.data
    #else:
    #    print('GET request')

    if ('piwigo_caller' not in session) or (session['piwigo_caller'] is None):
        session['piwigo_caller'] = request.referrer


    piwigo_avail = 'piwigo_avail' in session

    piwigo_retry = session.get('piwigo_retry', 0)

    if piwigo_retry >= 3:
        if 'piwigo_retry' in session:
            session.pop('piwigo_retry')
        flash('Max. retry for Piwigo authentication reached!')
        return redirect(url_for('main.index'))

    if not piwigo_avail:
        current_app.logger.info('{}: no piwigo token available! Starting Oauth process!'.format(current_user.username))

        session['piwigo_retry'] = piwigo_retry + 1


        url = url_for('social.piwigo_auth')

        return redirect(url)
    else:
        if 'piwigo_imageid' in session:
            imageid = session['piwigo_imageid']
            session.pop('piwigo_imageid')   # clean the cookie directly
            image = Image.query.get(imageid)
            image_file = File.query.get(image.render_image)
            if image_file is None:
                flash('Rendered file is not available!')
            else:
                if 'piwigo_token' in session:
                    print(session['piwigo_token'])

                    filename = image_file.full_filename()
                    project = Project.query.get(image.project_id)
                    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    title = '{} - {}'.format(project.name, date)

                    # upload image
                    try:
                        mysite = Piwigo(session['piwigo_url'])
                        mysite._cookies = session['piwigo_token']
                        mysite.pwg.images.addSimple(image=filename, category=1)
                        mysite.pwg.session.logout()
                        flash('Image uploaded to Piwigo!')
                    except:
                        flash('Failed to upload to Piwigo!')
                    session.pop('piwigo_token')


        if 'piwigo_avail' in session:
            session.pop('piwigo_avail')


    # clean all cookies, and more of less, destroy the oauth
    # since we don't know how long the token is valid!
    if 'piwigo_caller' in session:
        url = session.pop('piwigo_caller')
    else:
        url = url_for('main.index')

    if 'piwigo_avail' in session:
        session.pop('piwigo_avail')

    if 'piwigo_retry' in session:
        session.pop('piwigo_retry')

    # destroy the old handler it available
    #if flickr_api.auth.AUTH_HANDLER is not None:
    #    del flickr_api.auth.AUTH_HANDLER
    #    flickr_api.auth.AUTH_HANDLER = None

    #if current_user.username in flickr_auth_collection:
    #    flickr_auth_collection.pop(current_user.username)

    return redirect(url)


@bp.route('/social/piwigo_auth', methods=['GET', 'POST'])
def piwigo_auth():
    form = AuthPiwigoForm()

    if form.validate_on_submit():
        session['piwigo_url'] = form.host.data
        # remeber the username
        session['piwigo_user'] = form.username.data
        mysite = Piwigo(session['piwigo_url'])

        # login into piwigo
        mysite.pwg.session.login(username=form.username.data,
                                password=form.password.data)

        # extract login cookie
        session['piwigo_token'] = dict(mysite._cookies)
        session['piwigo_avail'] = True
        return redirect(url_for('social.piwigo_upload'))
    else:
        # if set use the names from last upload ...
        if 'piwigo_url' in session:
            form.host.data = session['piwigo_url']
        if 'piwigo_user' in session:
            form.username.data = session['piwigo_user']


    return render_template('social/piwigo_auth.html',
                            title='Authorize',
                            form=form)



@bp.route('/social/piwigo_oauth', methods=['GET'])
@login_required
def piwigo_oauth():
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

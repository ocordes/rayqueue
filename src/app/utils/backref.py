"""

app/utils/backref.py

written by: Oliver Cordes  2019-03-09
changed by: Oliver Cordes  2019-03-09


taken from: http://flask.pocoo.org/snippets/62/

"""


from urllib.parse import urlparse, urljoin
from flask import request, url_for


"""
is_safe_url

ensures that a redirect target will lead to the same server

:param target: target in flask name space
"""
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc



"""
get_redirect_target

looks at various hints to find the redirect target

"""
def get_redirect_target():
    for target in request.values.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target


"""
redirect_back

we don't want to redirect to the same page we have to make sure
that the actual back redirect is slightly different (only use the
submitted data, not the referrer). It will tried to use next and
the referrer first and fall back to a given endpoint.

"""
def redirect_back(endpoint, **values):
    target = request.form['next']
    if not target or not is_safe_url(target):
        target = url_for(endpoint, **values)
    return redirect(target)

"""

client/api.py

written by: Oliver Cordes 2019-02-12
changed by: Oliver Cordes 2019-03-04

"""

# header to make sure that all non-standard modules are available
import sys
import configparser
import json

try:
    import requests
except ImportError as e:
    print(e)
    print('Please install the latest requests module for python!')
    sys.exit(1)


# default Session class
class Session(object):

    def __init__(self, base_url='http://localhost',
                       username=None,
                       password=None,
                       config=None):

        if config is None:
            self._username = username
            self._password = password

            self._base_url = base_url
        else:
            self.read_config(config)

        self.set_base_url(self._base_url)
        self._token    = None


    """
    read_config

    reads a config file with all parameters
    """
    def read_config(self, configfile):
        config = configparser.ConfigParser()
        config.read(configfile)
        rayqueue = config['rayqueue']
        self._username = rayqueue.get('username')
        self._password = rayqueue.get('password')
        self._base_url = rayqueue.get('url')


    """
    set_base_url

    sets the base of each HTTP(S) request
    """
    def set_base_url(self, base_url):
        if base_url[-1] == '/':
            self._base_url = base_url[:-1]
        else:
            self._base_url = base_url


    """
    login

    login into the api with username and password,
    overwrites the given username and password, which
    will not be stored if given!
    """
    def login(self, username=None, password=None):
        if username is None:
            un = self._username
        else:
            us = username

        if password is None:
            pw = self._password
        else:
            pw = password

        data = { 'username:': un, 'password': pw }
        status, data = self.raw_request('/login', data=data,
                            request_type=requests.post)

        if status == 200:
            self._token = data['token']
            return True
        else:
            print(self._err_msg(data))


        return False



    """
    raw_request

    sends a data request with bearer auth to the server api
    """
    def raw_request(self, endpoint,
                        data=None,
                        bearer=False,
                        request_type=requests.get):
        path = self._url(endpoint)
        if bearer and (self._token is not None):
            headers = {'Authorization': 'Bearer %s' % self._token}
        else:
            headers = None
        try:
            ret = request_type(path, json=data, headers=headers)
            status_code = ret.status_code
            json_data = ret.json()
        except requests.exceptions.ConnectionError as e:
            status_code = 404
            json_data = { 'detail': 'Connectionn refused', 'status': '404'}
        return status_code, json_data


    # internal functions
    def _url(self, path):
        return self._base_url+path


    def _err_msg(self, data):
        print(data['status'])
        return 'ERROR({}): {}'.format(data['status'], data['detail'])

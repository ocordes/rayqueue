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

        self.rsession = requests.Session()


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

    login into the api
    """
    def login(self):
        data = { 'username:': self._username, 'password': self._password }
        status, data = self.raw_request('/login', data=data,
                            request_type=self.rsession.post)

        if status == 200:
            self._token = data['token']
            auth_header = {'Authorization': 'Bearer %s' % self._token}
            self.rsession.headers.update(auth_header)
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
                        request_type=None):
        if request_type is None:
            status_code = 404
            json_data = { 'detail': 'API error, no request type defined!',
                          'status': '404'}
        else:
            path = self._url(endpoint)
            try:
                ret = request_type(path, json=data)
                status_code = ret.status_code
                json_data = ret.json()
            except requests.exceptions.ConnectionError as e:
                status_code = 404
                json_data = { 'detail': 'Connection refused', 'status': '404'}
        return status_code, json_data



    def request(self, endpoint,
                    data=None,
                    request_type=None):
        tries = 0
        max_tries = 3

        while tries < max_tries:
            status_code, json_data = self.raw_request(endpoint, data=data,
                                                        reqest_type=request_type)
            if status_code == 401:
                print('WARNING: Maybe token error in API request! Retrying login!')
                if self.login() == False:
                    break
                print('INFORMATION: login successful! Retry the API request!')
                # if login successful, next try to send the request
                tries += 1

        if tries == max_tries:
            print('ERROR: Request cannot fullfilled after %i attempts!' % max_tries)
        return status_code, json_data


    def __get_filename(self, headers):
        name = headers.get('Content-Disposition', None)
        if name is None:
            return None
        s = name.split(';')
        filename = None
        for i in s:
            if i.find('=') != -1:
                r = i.split('=')
                if r[0].strip().lower() == 'filename':
                    filename = r[1].strip()
        return filename


    def file_request(self, endpoint ):
        path = self._url(endpoint)
        try:
            ret = self.rsession.get(path, stream=True)
            status_code = ret.status_code
            filename = self.__get_filename(ret.headers)
        except requests.exceptions.ConnectionError as e:
            status_code = 404
            filename = { 'detail': 'Connectionn refused', 'status': '404'}
        return status_code, filename, ret.raw


    # internal functions
    def _url(self, path):
        return self._base_url+path


    def _err_msg(self, data):
        print(data['status'])
        return 'ERROR({}): {}'.format(data['status'], data['detail'])

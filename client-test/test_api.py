#!/usr/bin/env python

import os, sys
import requests

# test the sending of a file to the flask server

filename = __file__

url = 'http://localhost:4555/api'
files = {'file': open(filename, 'rb')}

r = requests.post(url, files=files)
print(r.text)

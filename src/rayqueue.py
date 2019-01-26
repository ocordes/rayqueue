#!/usr/bin/env python

__author__  = 'Oliver Cordes'

__version__ = '0.0.1'

from app import app


# test this file
if __name__ == "__main__":
    app.run(port=4555, debug=True)

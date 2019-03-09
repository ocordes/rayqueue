"""

client/baseobjects.py

written by: Oliver Cordes 2019-03-09
changed by: Oliver Cordes 2019-03-09

"""


class BaseObject(object):
    def __init__(self,data=None):
        if data is not None:
            self._set_attributes(data)


    def _set_attributes( self, adict ):
        for name, value in adict.items():
            setattr( self, name, value )

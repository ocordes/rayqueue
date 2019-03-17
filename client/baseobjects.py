"""

client/baseobjects.py

written by: Oliver Cordes 2019-03-09
changed by: Oliver Cordes 2019-03-17

"""


class BaseObject(object):
    def __init__(self,data=None):
        if data is not None:
            self._set_attributes(data)


    """
    filtervalue

    gives the possibility to change the values from raw types e.g.
    in classes!

    this is the default implementation which does nothing!
    """
    def filtervalue(self, name, value):
        return value


    def _set_attributes( self, adict ):
        for name, value in adict.items():
            value = self.filtervalue(name, value)
            setattr( self, name, value )

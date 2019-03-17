"""

client/baseobjects.py

written by: Oliver Cordes 2019-03-09
changed by: Oliver Cordes 2019-03-17

"""


class BaseObject(object):
    """
    __init__

    is used only for taking a data dictonary which represents the
    variables of the instance

    :param data: dictonary with the variable data
    """
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


    """
    _set_attributes

    sets the variables from a dictonary

    :param adict: dictonary with the data values
    """
    def _set_attributes( self, adict ):
        for name, value in adict.items():
            value = self.filtervalue(name, value)
            setattr( self, name, value )

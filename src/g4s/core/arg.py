# -*- coding: utf-8 -*-

"""
Function argument verification utilities.
"""

__all__ = (
    'ArgumentNullError',
    'ArgumentTypeError',
)


class ArgumentNullError(ValueError):
    """
    An exception which is thrown by "argument-null" error.
    """

    def __init__(self, name):
        """
        Initializes an instance of :py:class:`ArgumentNullError` class.

        :param name: name of the argument
        :type name:  str
        """

        super(ArgumentNullError, self).__init__()
        self._name = name

    @property
    def message(self):
        return 'The value of the argument `{0}` must not be None.'.format(self._name)

    @property
    def name(self):
        """
        Gets name of the argument which caused an error.

        :rtype:  str
        :return: name of the argument which caused an error
        """

        return self._name


class ArgumentTypeError(TypeError):
    """
    An exception which is thrown by "argument-type" error.
    """

    def __init__(self, name, type):
        """
        Initializes an instance of :py:class:`ArgumentTypeError` class.

        :param name: name of the argument
        :param type: type of the argument
        """

        super(ArgumentTypeError, self).__init__()
        self._name = name
        self._type = type

    @property
    def message(self):
        return 'The type of the argument `{0}` must be {1}.'.format(self.name, self._type)

    @property
    def name(self):
        """
        Gets name of the argument.

        :rtype:  str
        :return: name of the argument
        """

        return self._name

    @property
    def type(self):
        """
        Gets type of the argument.

        :rtype:  str|type
        :return: type of the argument
        """

        return self._type

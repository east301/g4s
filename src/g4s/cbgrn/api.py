# -*- coding: utf-8 -*-

"""
Cybozu Garoon calendar API interface.
"""

__all__ = (
    'CybozuGaroonApi',
)

from ..core.api import CalendarApi
from ..core.arg import ArgumentNullError
from ..core.arg import ArgumentTypeError


class CybozuGaroonApi(CalendarApi):
    """
    An implementation of :py:class:`g4s.core.api.CalendarApi` which interacts with Cybozu Garoon
    server.
    """

    def __init__(self, params):
        """
        Initializes an instance of :py:class:`g4s.cbgrn.api.CybozuGaroonApi` class.
        The ``params`` must contains the following values.

        * ``url``: URL of Cybozu Garoon CGI, usually ends with ``grn.cgi`` or ``grn.exe``
        * ``user``: login name
        * ``password``: password
        * ``language``: language of SOAP response (``en`` or ``ja``), (optional)
        """

        #
        super(CybozuGaroonApi, self).__init__(params)

        #
        params = params.copy()
        if 'language' not in params:
            params['language'] = 'en'

        for key in ('url', 'user', 'password', 'language'):
            if key not in params:
                raise KeyError('The required key "{0}" is not in the `params`.'.format(key))

            value = params[key]
            if value is None:
                raise ArgumentNullError('params[{0}]'.format(key))
            if not isinstance(value, str):
                raise ArgumentTypeError('params[{0}]'.format(key), str)
            if (key == 'language' and value not in ('en', 'ja')):
                raise ValueError('`params[language]` must be "en" or "ja".')

        #
        self._url = params['url']
        self._user = params['user']
        self._password = params['password']
        self._language = params['language']

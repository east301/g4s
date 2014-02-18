# -*- coding: utf-8 -*-

"""
Cybozu Garoon calendar API interface.
"""

__all__ = (
    'CybozuGaroonApi',
)

import lxml.etree
import requests
from ..core.api import CalendarApi
from ..core.api import NetworkError
from ..core.api import ResponseParseError
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

    def get_soap_endpoints(self):
        """
        Gets mapping between SOAP service name and its endpoint URL.

        :rtype:  dict[str, str]
        :return: a dict which maps SOAP service name and its endpoint URL
        """

        #
        try:
            response = requests.get(self._url + '?WSDL')
            response.raise_for_status()
        except Exception as ex:
            raise NetworkError('Failed to get WSDL.') from ex

        try:
            wsdl = lxml.etree.fromstring(response.text.encode('UTF-8'))
        except Exception as ex:
            raise ResponseParseError('Failed to parse WSDL.') from ex

        #
        result = {}
        nss = {
            'ns': 'http://schemas.xmlsoap.org/wsdl/',
            'soap12': 'http://schemas.xmlsoap.org/wsdl/soap12/',
        }

        try:
            for service_node in wsdl.xpath('//ns:service', namespaces=nss):
                service_name = service_node.attrib['name']
                url = service_node.xpath('.//soap12:address', namespaces=nss)[0].attrib['location']
                result[service_name] = url
        except Exception as ex:
            raise ResponseParseError('Failed to parse WSDL.') from ex

        #
        return result

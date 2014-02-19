# -*- coding: utf-8 -*-

"""
Cybozu Garoon calendar API interface.
"""

__all__ = (
    'CybozuGaroonApi',
)

import datetime
import os
import jinja2
import lxml.etree
import requests
from ..core.api import CalendarApi
from ..core.api import NetworkError
from ..core.api import RequestError
from ..core.api import ResponseParseError
from ..core.arg import ArgumentNullError
from ..core.arg import ArgumentTypeError
from ..core.date import DateTime
from ..core.date import TimeZone
from ..core.debug import LogicError


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

        #
        self._endpoint_cache = None

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

    def execute_soap_request(self, service, action, action_params):
        """
        Executes SOAP request.

        :param service:       SOAP service name
        :param action:        SOAP action name
        :param action_params: SOAP action parameters
        :type  service:       str
        :type  action:        str
        :type  action_params: dict[str, str]

        :rtype:  :py:class:`lxml.etree._Element`
        :return: SOAP response
        """

        #
        if service is None:
            raise ArgumentNullError('service')
        if action is None:
            raise ArgumentNullError('action')
        if action_params is None:
            raise ArgumentNullError('action_params')

        if not isinstance(service, str):
            raise ArgumentTypeError('service', str)
        if not isinstance(action, str):
            raise ArgumentTypeError('action', str)
        if not isinstance(action_params, dict):
            raise ArgumentTypeError('action_params', dict)

        #
        request_text = self._render_request_body(service, action, action_params)
        response_text = self._send_soap_request(service, action, request_text)
        response = self._parse_soap_response(response_text)

        return response

    def _render_request_body(self, service, action, action_params):
        #
        created = DateTime.get_utc_now()
        expires = created + datetime.timedelta(days=1)
        params = dict(
            created=created, expires=expires,
            login_name=self._user, password=self._password, language=self._language)

        if action_params:
            params.update(action_params)

        #
        try:
            template = self._get_soap_request_template(service, action)
        except Exception as ex:  # pragma: no cover
            raise LogicError('Failed to get SOAP request template.') from ex

        try:
            return template.render(params)
        except jinja2.exceptions.UndefinedError as ex:  # pragma: no cover
            msg = 'Failed to render SOAP request body. Some required values are missing.'
            raise LogicError(msg) from ex
        except Exception as ex:  # pragma: no cover
            raise LogicError('Failed to render SOAP request body.') from ex

    def _get_soap_request_template(self, service, action):
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
        env.filters['utc_datetime'] = self._jinja2_filter_utc_datetime

        template = env.get_template('{0}.{1}.xml'.format(service, action))
        return template

    def _send_soap_request(self, service, action, request_text):
        # gets endpoint URL mapping if it is not already retrieved
        if self._endpoint_cache is None:
            self._endpoint_cache = self.get_soap_endpoints()

        # gets URL for the specified service
        endpoint_url = self._endpoint_cache.get(service)
        if endpoint_url is None:
            msg = 'Failed to find endpoint URL of the specified service: {0}'
            raise RequestError(msg.format(service))

        # performs HTTP POST
        headers = {'Content-Type': 'application/soap+xml'}
        data = request_text.encode('utf-8')

        try:
            response = requests.post(endpoint_url, data=data, headers=headers)
            response.raise_for_status()
        except Exception as ex:
            raise NetworkError('Failed to perform HTTP POST request.') from ex

        return response.text

    def _parse_soap_response(self, response_text):
        # parses response text as XML
        try:
            response = lxml.etree.fromstring(response_text.encode('utf-8'))
        except Exception as ex:
            raise ResponseParseError('Failed to parse SOAP response.') from ex

        # checks SOAP errors
        nss = dict(soap='http://www.w3.org/2003/05/soap-envelope')
        nodes = response.xpath('//soap:Fault', namespaces=nss)
        if not nodes:
            return response

        # raises an exception for SOAP error
        t = lambda ns: str(ns[0]) if ns and str(ns[0]) else 'unknown'

        fault_node = nodes[0]

        fault_reason = t(fault_node.xpath('./soap:Reason/soap:Text/text()', namespaces=nss))
        fault_cause = t(fault_node.xpath('./soap:Detail/cause/text()', namespaces=nss))
        fault_cm = t(fault_node.xpath('./soap:Detail/counter_measure/text()', namespaces=nss))

        #
        params = fault_reason, fault_cause, fault_cm
        msg = 'The remote server returned an error ({0} {1} {2})'.format(*params)
        raise RequestError(msg)

    def _jinja2_filter_utc_datetime(self, dt):
        dt = dt.astimezone(TimeZone.get('UTC'))
        return dt.strftime('%Y-%m-%dT%H:%M:%SZ')

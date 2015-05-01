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
from ..core.model import Event
from ..core.model import Participant


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

    def get_events(self, start, end):
        """
        DOCUMENT ME
        """

        #
        if start is None:
            raise ArgumentNullError('start')
        if end is None:
            raise ArgumentNullError('end')

        if not isinstance(start, DateTime):
            raise ArgumentTypeError('start', DateTime)
        if not isinstance(end, DateTime):
            raise ArgumentTypeError('end', DateTime)

        if start > end:
            raise ValueError('`start` must be same as `end`, or comes before `end`.')

        #
        params = dict(start=start, end=end)
        response = self.execute_soap_request('ScheduleService', 'ScheduleGetEvents', params)

        return tuple(self._create_event_parser(response))

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

    def _create_event_parser(self, response):
        for node in response.xpath('//schedule_event'):
            try:
                result = self._parse_single_event_node(node)
            except Exception:
                # TODO: add code to log the exception
                continue

            if result is None:  # pragma: no cover
                # when unsupported event type found
                # TODO: add tests after adding 'repeat event' support
                continue

            if isinstance(result, Event):
                yield result
            elif isinstance(result, _RepeatEventRule):
                for event in result.resolve():
                    yield event
            else:
                raise LogicError  # pragma: no cover

    def _parse_single_event_node(self, node):
        id = int(node.attrib['id'])
        type = node.attrib['event_type'].lower()

        if type in ('normal', 'banner'):
            type = Event.NORMAL if type == 'normal' else Event.BANNER
            return self._parse_normal_event(node, id, type)
        elif type == 'repeat':
            return self._parse_repeat_event(node, id)
        else:  # pragma: no cover
            # unsupported event types (e.g. repeat and temporary)
            # TODO: add tests after adding 'repeat event' support
            return None

    def _parse_normal_event(self, node, id, type):
        #
        (is_public, last_update, detail, description, start_tz_name, end_tz_name,
            all_day, start_only, members) = self._parse_common_event_information(node)

        #
        start_tz_name = node.attrib['timezone']
        is_allday = self._parse_bool(node.attrib['allday'])
        is_start_only = self._parse_bool(node.attrib['start_only'])
        nss = dict(s2008='http://schemas.cybozu.co.jp/schedule/2008')

        #
        if is_allday:
            dt_node = node.xpath('.//s2008:when/s2008:date', namespaces=nss)[0]
            start = DateTime.parse(dt_node.attrib['start'], start_tz_name)
            end = DateTime.parse(dt_node.attrib['end'], node.attrib['end_timezone'])

        else:
            dt_node = node.xpath('.//s2008:when/s2008:datetime', namespaces=nss)[0]
            start = DateTime.parse(dt_node.attrib['start'], start_tz_name)

            if is_start_only:
                end = None
            else:
                end = DateTime.parse(dt_node.attrib['end'], node.attrib['end_timezone'])

        return Event(
            id, type, detail, description, start, end, is_allday, members, is_public, last_update)

    def _parse_repeat_event(self, node, id):
        #
        (is_public, last_update, detail, description, start_tz_name, end_tz_name,
            all_day, start_only, members) = self._parse_common_event_information(node)

        if not end_tz_name:
            end_tz_name = start_tz_name

        #
        nss = dict(s2008='http://schemas.cybozu.co.jp/schedule/2008')

        repeat_info_node = node.xpath('.//s2008:repeat_info', namespaces=nss)[0]
        repeat_cond_node = repeat_info_node.xpath('.//s2008:condition', namespaces=nss)[0]

        repeat_type = repeat_cond_node.attrib['type']
        repeat_day = int(repeat_cond_node.attrib['day'])
        repeat_week = int(repeat_cond_node.attrib['week'])
        repeat_start_date = DateTime.parse(repeat_cond_node.attrib['start_date'], start_tz_name)
        repeat_end_date = DateTime.parse(repeat_cond_node.attrib['end_date'], end_tz_name)

        #
        exc_dt_nodes = repeat_info_node.xpath('.//s2008:exclusive_datetime', namespaces=nss)
        exc_dts = []
        if exc_dt_nodes:
            for exc_dt_node in exc_dt_nodes:
                start = DateTime.parse(exc_dt_node.attrib['start'], 'UTC')
                end = DateTime.parse(exc_dt_node.attrib['end'], 'UTC')
                exc_dts.append((start, end))

            exc_dts.sort(key=lambda r: r[0])

        yield _RepeatEventRule(
            id, detail, description, all_day, start_only, members, is_public, last_update,
            repeat_type, repeat_day, repeat_week, repeat_start_date, repeat_end_date, exc_dts)

    def _parse_common_event_information(self, node):
        #
        public_type = node.attrib['public_type'].lower()
        version = int(node.attrib['version'])

        detail = node.attrib['detail']
        description = node.attrib.get('description')

        start_tz_name = node.attrib['timezone']
        end_tz_name = node.attrib.get('end_timezone')
        all_day = self._parse_bool(node.attrib['allday'])
        start_only = self._parse_bool(node.attrib['start_only'])

        members = tuple(self._create_member_parser(node))

        #
        is_public = public_type == 'public'

        # TODO: remove hardcording of timezone name 'Asia/Tokyo'
        #   `version` should be interpreted as 'system(server) local' timestamp,
        #   however, there seems no way to get server's time zone configuration.
        vt = datetime.datetime.fromtimestamp(version).timetuple()[:6]
        last_update = DateTime.get(*vt, tzinfo='Asia/Tokyo')

        #
        return (
            is_public, last_update, detail, description,
            start_tz_name, end_tz_name, all_day, start_only, members
        )

    def _create_member_parser(self, node):
        nss = dict(s2008='http://schemas.cybozu.co.jp/schedule/2008')
        ordering = lambda m: int(m.get('order', 0))

        member_nodes = node.xpath('.//s2008:user', namespaces=nss)
        for member_node in sorted(member_nodes, key=ordering):
            id = int(member_node.attrib['id'])
            name = member_node.attrib['name']

            yield Participant(id, name)

    def _parse_bool(self, text):
        text = text.lower()
        if text == 'true':
            return True
        elif text == 'false':
            return False

        raise Exception  # pragma: no cover

    #
    # SOAP
    #

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


class _RepeatEventRule(object):
    def __init__(
            self, id, type, detail, description, all_day, start_only,
            members, is_public, last_update,
            repeat_type, repeat_day, repeat_week, repeat_start_date, repeat_end_date,
            exclusive_datetimes):

            self.id = id
            self.type = type.lower()
            self.detail = detail
            self.description = description
            self.is_all_day = all_day
            self.is_start_only = start_only
            self.repeat_type = repeat_type
            self.repeat_day = repeat_day
            self.repeat_week = repeat_week
            self.repeat_start_date = repeat_start_date
            self.repeat_end_date = repeat_end_date
            self.exclusive_datetimes = exclusive_datetimes

    def resolve(self):
        if self.type == 'day':
            return self._resolve_day_type()
        elif self.type == 'weekday':
            return self._resolve_weekday_type()
        elif self.type in ('1stweek', '2ndweek', '3rdweek', '4thweek'):
            return self._resolve_x_week_type()
        elif self.type == 'lastweek':
            return self._resolve_last_week_type()
        elif self.type == 'month':
            return self._resolve_month_type()
        else:
            raise LogicError

    def _resolve_day_type(self):
        current = self.start_date
        while current < self.end_date:
            yield current
            current += datetime.timedelta(days=1)

    def _resolve_weekday_type(self):
        pass

    def _resolve_x_week_type(self):
        pass

    def _resolve_last_week_type(self):
        pass

    def _resolve_month_type(self):
        pass

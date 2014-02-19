# -*- coding: utf-8 -*-

import mock
import lxml.etree
import pytest
import requests
from g4s.cbgrn.api import CybozuGaroonApi
from g4s.core.api import NetworkError
from g4s.core.api import ResponseParseError
from g4s.core.date import DateTime
from .util import check_if_current_datetime_is_correctly_fixed
from .util import fix_current_datetime
from .util import parse_xml
from .util import raises_argument_null_error
from .util import raises_argument_type_error
from .util import read
from .util import xml_compare


###
### constant values
###

GRN_SERVER_URL = 'http://example.com/cgi-bin/cbgrn/grn.cgi'
SOAP_WSDL_URL = GRN_SERVER_URL + '?WSDL'

VALID_API_PARAMS = {'url': GRN_SERVER_URL, 'user': 'foo', 'password': 'bar', 'language': 'en'}

VALID_SOAP_ENDPOINTS = {
    'AddressService': GRN_SERVER_URL + '/cbpapi/address/api?',
    'AdminService': GRN_SERVER_URL + '/sysapi/admin/api?',
    'BaseService': GRN_SERVER_URL + '/cbpapi/base/api?',
    'BulletinService': GRN_SERVER_URL + '/cbpapi/bulletin/api?',
    'CabinetService': GRN_SERVER_URL + '/cbpapi/cabinet/api?',
    'CybozuWebSrvService': GRN_SERVER_URL + '/cbpapi/cbwebsrv/api?',
    'MailService': GRN_SERVER_URL + '/cbpapi/mail/api?',
    'MessageService': GRN_SERVER_URL + '/cbpapi/message/api?',
    'NotificationService': GRN_SERVER_URL + '/cbpapi/notification/api?',
    'ReportService': GRN_SERVER_URL + '/cbpapi/report/api?',
    'ScheduleService': GRN_SERVER_URL + '/cbpapi/schedule/api?',
    'StarService': GRN_SERVER_URL + '/cbpapi/star/api?',
    'UtilService': GRN_SERVER_URL + '/util_api/util/api?',
    'WorkflowService': GRN_SERVER_URL + '/cbpapi/workflow/api?',
}

SOAP_REQUEST_RESPONSE_PAIRS = [
    ('get_events-001', 'ScheduleService', 'ScheduleGetEvents'),
]


###
### fixture
###

def patch_requests_to_cause_network_error(monkeypatch, target):
    def my_request_method(url, *args):
        response = mock.Mock(spec=requests.Response)
        response.raise_for_status.side_effect = requests.exceptions.HTTPError
        return response

    monkeypatch.setattr('requests.' + target, my_request_method)


def check_if_requests_cause_network_error(target):
    with pytest.raises(requests.exceptions.HTTPError):
        getattr(requests, target)('http://www.google.com').raise_for_status()


def patch_requests_get_to_return_specified_wsdl(monkeypatch, wsdl_path):
    def my_request_get(url, *args):
        # GET request is used only to get WSDL.
        if url != SOAP_WSDL_URL: raise Exception

        response_text = read(wsdl_path).decode('utf-8')

        response = mock.Mock(spec=requests.Response)
        type(response).text = mock.PropertyMock(return_value=response_text)

        return response

    monkeypatch.setattr('requests.get', my_request_get)


def check_if_requests_get_returns_correct_wsdl(wsdl_path):
    response = requests.get(SOAP_WSDL_URL)
    text = response.text
    expected_text = read(wsdl_path).decode('utf-8')

    assert response.text == expected_text


def patch_requests_post_to_return_correct_soap_response(monkeypatch):
    def my_request_post(url, data, *args, **kwargs):
        #
        request_xml = parse_xml(data)

        #
        response_prefix = None
        for prefix, service, action in SOAP_REQUEST_RESPONSE_PAIRS:
            canditate_url = VALID_SOAP_ENDPOINTS[service]
            canditate_xml = parse_xml(read('g4s.cbgrn', prefix + '-request.xml'))

            if url == canditate_url and xml_compare(request_xml, canditate_xml):
                response_prefix = prefix
                break

        #
        if response_prefix is None:
            raise Exception('Failed to find response for the SOAP request.')

        #
        response_text = read('g4s.cbgrn', response_prefix + '-response.xml').decode('utf-8')

        response = mock.Mock(spec=requests.Response)
        type(response).text = mock.PropertyMock(return_value=response_text)

        return response

    monkeypatch.setattr('requests.post', my_request_post)


def check_if_requests_post_returns_correct_response():
    request_data = read('g4s.cbgrn', 'get_events-001-request.xml')
    response = requests.post(VALID_SOAP_ENDPOINTS['ScheduleService'], data=request_data)
    response.raise_for_status()

    response_xml = parse_xml(response.text.encode('utf-8'))
    expected_response_xml = parse_xml(read('g4s.cbgrn', 'get_events-001-response.xml'))

    assert xml_compare(response_xml, expected_response_xml)


def patch_requests_post_to_invalid_xml_text(monkeypatch):
    def my_request_post(*args, **kwargs):
        response = mock.Mock(spec=requests.Response)
        type(response).text = mock.PropertyMock(return_value='foo')
        return response

    monkeypatch.setattr('requests.post', my_request_post)


def check_if_requests_post_returns_invalid_xml_text():
    response = requests.post('http://example.com', data='foo')
    response.raise_for_status()

    with pytest.raises(Exception):
        lxml.etree.fromstring(response.text.encode('utf-8'))


def patch_requests_post_to_return_soap_error(monkeypatch):
    def my_request_post(*args, **kwargs):
        response_text = read('g4s.cbgrn', 'soap_error.xml').decode('utf-8')

        response = mock.Mock(spec=requests.Response)
        type(response).text = mock.PropertyMock(return_value=response_text)
        return response

    monkeypatch.setattr('requests.post', my_request_post)


def check_if_requests_post_returns_soap_error():
    response = requests.post('http://example.com', data='foo')
    response.raise_for_status()

    assert 'Fault' in response.text


@pytest.fixture
def network_error(monkeypatch):
    patch_requests_to_cause_network_error(monkeypatch, 'get')
    patch_requests_to_cause_network_error(monkeypatch, 'post')


def test__network_error(network_error):
    check_if_requests_cause_network_error('get')
    check_if_requests_cause_network_error('post')


@pytest.fixture
def network_post_error(monkeypatch):
    patch_requests_to_cause_network_error(monkeypatch, 'post')


def test__network_post_error(network_post_error):
    check_if_requests_cause_network_error('post')


@pytest.fixture
def invalid_wsdl_001(monkeypatch):
    patch_requests_get_to_return_specified_wsdl(monkeypatch, 'g4s.cbgrn/invalid_wsdl_001.xml')


def test__invalid_wsdl_001(invalid_wsdl_001):
    check_if_requests_get_returns_correct_wsdl('g4s.cbgrn/invalid_wsdl_001.xml')


@pytest.fixture
def invalid_wsdl_002(monkeypatch):
    patch_requests_get_to_return_specified_wsdl(monkeypatch, 'g4s.cbgrn/invalid_wsdl_002.xml')


def test__invalid_wsdl_002(invalid_wsdl_002):
    check_if_requests_get_returns_correct_wsdl('g4s.cbgrn/invalid_wsdl_002.xml')


@pytest.fixture
def valid_wsdl_001(monkeypatch):
    patch_requests_get_to_return_specified_wsdl(monkeypatch, 'g4s.cbgrn/valid_wsdl_001.xml')


def test__valid_wsdl_001(valid_wsdl_001):
    check_if_requests_get_returns_correct_wsdl('g4s.cbgrn/valid_wsdl_001.xml')


@pytest.fixture
def valid_incompleted_wsdl_001(monkeypatch):
    patch_requests_get_to_return_specified_wsdl(monkeypatch, 'g4s.cbgrn/valid_incompleted_wsdl_001.xml')


def test__valid_incompleted_wsdl_001(valid_incompleted_wsdl_001):
    check_if_requests_get_returns_correct_wsdl('g4s.cbgrn/valid_incompleted_wsdl_001.xml')


@pytest.fixture
def valid_soap_response(monkeypatch):
    patch_requests_post_to_return_correct_soap_response(monkeypatch)


def test__valid_soap_response(valid_soap_response):
    check_if_requests_post_returns_correct_response()


@pytest.fixture
def invalid_soap_response(monkeypatch):
    patch_requests_post_to_invalid_xml_text(monkeypatch)


def test__invalid_soap_response(invalid_soap_response):
    check_if_requests_post_returns_invalid_xml_text()


@pytest.fixture
def valid_response(monkeypatch):
    fix_current_datetime(monkeypatch)
    valid_wsdl_001(monkeypatch)
    valid_soap_response(monkeypatch)


def test__valid_response(valid_response):
    check_if_current_datetime_is_correctly_fixed()
    test__valid_wsdl_001(None)
    test__valid_soap_response(None)


@pytest.fixture
def soap_error(monkeypatch):
    patch_requests_post_to_return_soap_error(monkeypatch)


def test__soap_error(soap_error):
    check_if_requests_post_returns_soap_error()


###
### g4s.cbgrn.api.CybozuGaroonApi.__init__
###

def test__CybozuGaroonApi__init__raises_KeyError_if_required_key_is_missing():
    required_keys = 'url', 'user', 'password'
    for x in range(len(required_keys)):
        keys = list(required_keys)
        keys.pop(x)

        params = dict((k, 'foo') for k in keys)

        with pytest.raises(KeyError) as excinfo:
            CybozuGaroonApi(params)

        assert required_keys[x] in str(excinfo.value)


def test__CybozuGaroonApi__init__raises_ArgumentNullError_if_None_is_specified_as_value():
    keys = 'url', 'user', 'password', 'language'
    for key in keys:
        params = dict((k, 'foo') for k in keys)
        params[key] = None

        with raises_argument_null_error('params[{0}]'.format(key)):
            CybozuGaroonApi(params)


@pytest.mark.parametrize('value', [1, 2.34, object()])
def test__CybozuGaroonApi__init__raises_ArgumentTypeError_if_object_except_str_is_specified_as_value(value):
    keys = 'url', 'user', 'password', 'language'
    for key in keys:
        params = dict((k, 'foo') for k in keys)
        params[key] = value

        with raises_argument_type_error('params[{0}]'.format(key)):
            CybozuGaroonApi(params)


def test__CybozuGaroonApi__init__raises_ValueError_if_invalid_language_is_specified():
    keys = 'url', 'user', 'password', 'language'
    params = dict((k, 'foo') for k in keys)

    with pytest.raises(ValueError) as excinfo:
        CybozuGaroonApi(params)

    assert 'params[language]' in str(excinfo.value)


@pytest.mark.parametrize('language', ['en', 'ja'])
def test__CybozuGaroonApi__init__works_correctly(language):
    params = dict(
        url='http://example.com/cgi-bin/grn.cgi',
        user='foo', password='bar', language=language)

    api = CybozuGaroonApi(params)
    assert api._url == params['url']
    assert api._user == params['user']
    assert api._password == params['password']
    assert api._language == params['language']



###
### g4s.cbgrn.api.CybozuGaroonApi.get_soap_endpoints
###

def test__CybozuGaroonApi__get_soap_endpoints__raises_NetworkError(network_error):
    api = CybozuGaroonApi(VALID_API_PARAMS)

    with pytest.raises(NetworkError):
        api.get_soap_endpoints()


def test__CybozuGaroonApi__get_soap_endpoints__raises_ResponseParseError__001(invalid_wsdl_001):
    api = CybozuGaroonApi(VALID_API_PARAMS)

    with pytest.raises(ResponseParseError):
        api.get_soap_endpoints()


def test__CybozuGaroonApi__get_soap_endpoints__raises_ResponseParseError__002(invalid_wsdl_002):
    api = CybozuGaroonApi(VALID_API_PARAMS)

    with pytest.raises(ResponseParseError):
        api.get_soap_endpoints()


def test__CybozuGaroonApi__get_soap_endpoints__returns_correct_results__001(valid_wsdl_001):
    api = CybozuGaroonApi(VALID_API_PARAMS)
    endpoint_map = api.get_soap_endpoints()

    assert len(endpoint_map) == len(VALID_SOAP_ENDPOINTS)
    for name in VALID_SOAP_ENDPOINTS:
        assert name in endpoint_map
        assert endpoint_map[name] == VALID_SOAP_ENDPOINTS[name]


###
### g4s.cbgrn.api.CybozuGaroonApi.execute_soap_request
###

@pytest.mark.parametrize('name', ['service', 'action', 'action_params'])
def test__CybouzGaroonApi__execute_soap_request__raises_ArgumentNullError_if_None_is_specified(name):
    kwargs = dict(service='foo', action='bar', action_params=dict())
    kwargs[name] = None

    api = CybozuGaroonApi(VALID_API_PARAMS)
    with raises_argument_null_error(name):
        api.execute_soap_request(**kwargs)


@pytest.mark.parametrize('name', ['service', 'action', 'action_params'])
def test__CybouzGaroonApi__execute_soap_request__raises_ArgumentTypeError_if_invalid_value_is_specified(name):

    for value in (1, 1.234, object()):
        kwargs = dict(service='foo', action='bar', action_params=dict())
        kwargs[name] = value

        api = CybozuGaroonApi(VALID_API_PARAMS)
        with raises_argument_type_error(name):
            api.execute_soap_request(**kwargs)


def test__CybouzGaroonApi__execute_soap_request__returns_valid_response(valid_response):
    api = CybozuGaroonApi(VALID_API_PARAMS)

    # get_events-001
    params = dict(start=DateTime.get(2014, 1, 1, tzinfo='UTC'), end=DateTime.get(2014, 1, 2, tzinfo='UTC'))
    response = api.execute_soap_request('ScheduleService', 'ScheduleGetEvents', params)

    expected_response = parse_xml(read('g4s.cbgrn', 'get_events-001-response.xml'))
    assert xml_compare(response, expected_response)


def test__CybouzGaroonApi__execute_soap_request__raises_Exception_if_invalid_service_is_specified(
        valid_incompleted_wsdl_001, valid_soap_response):

    api = CybozuGaroonApi(VALID_API_PARAMS)
    params = dict(start=DateTime.get_utc_now(), end=DateTime.get_utc_now())

    with pytest.raises(Exception):  # TODO
        api.execute_soap_request('ScheduleService', 'ScheduleGetEvents', params)


def test__CybouzGaroonApi__execute_soap_request__raises_Exception_if_invalid_service_or_action_name_is_specified(
        valid_response):

    api = CybozuGaroonApi(VALID_API_PARAMS)
    params = dict(start=DateTime.get_utc_now(), end=DateTime.get_utc_now())

    with pytest.raises(Exception):  # TODO
        api.execute_soap_request('FooService', 'ScheduleGetEvents', params)

    with pytest.raises(Exception):  # TODO
        api.execute_soap_request('ScheduleService', 'BarAction', params)



@pytest.mark.parametrize('name', ['start', 'end'])
def test__CybouzGaroonApi__execute_soap_request__raises_Exception_if_required_value_is_missing(
        valid_response, name):

    api = CybozuGaroonApi(VALID_API_PARAMS)
    params = dict(start=DateTime.get_utc_now(), end=DateTime.get_utc_now())
    params.pop(name)

    with pytest.raises(Exception):  # TODO
        api.execute_soap_request('ScheduleService', 'ScheduleGetEvents', params)


def test__CybouzGaroonApi__execute_soap_request__raises_Exception_if_required_value_is_missing(
        valid_wsdl_001, network_post_error):

    api = CybozuGaroonApi(VALID_API_PARAMS)
    params = dict(start=DateTime.get_utc_now(), end=DateTime.get_utc_now())

    with pytest.raises(Exception):  # TODO
        api.execute_soap_request('ScheduleService', 'ScheduleGetEvents', params)


def test__CybouzGaroonApi__execute_soap_request__raises_Exception_if_failed_to_parse_soap_response(
        valid_wsdl_001, invalid_soap_response):

    api = CybozuGaroonApi(VALID_API_PARAMS)
    params = dict(start=DateTime.get_utc_now(), end=DateTime.get_utc_now())

    with pytest.raises(Exception):  # TODO
        api.execute_soap_request('ScheduleService', 'ScheduleGetEvents', params)


def test__CybouzGaroonApi__execute_soap_request__raises_Exception_if_soap_error_is_happened(
        valid_wsdl_001, soap_error):

    api = CybozuGaroonApi(VALID_API_PARAMS)
    params = dict(start=DateTime.get_utc_now(), end=DateTime.get_utc_now())

    with pytest.raises(Exception):  # TODO
        api.execute_soap_request('ScheduleService', 'ScheduleGetEvents', params)

# -*- coding: utf-8 -*-

import mock
import pytest
import requests
from g4s.cbgrn.api import CybozuGaroonApi
from g4s.core.api import NetworkError
from g4s.core.api import ResponseParseError
from .util import raises_argument_null_error
from .util import raises_argument_type_error
from .util import read


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



@pytest.fixture
def network_error(monkeypatch):
    patch_requests_to_cause_network_error(monkeypatch, 'get')
    patch_requests_to_cause_network_error(monkeypatch, 'post')


def test__network_error(network_error):
    check_if_requests_cause_network_error('get')
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

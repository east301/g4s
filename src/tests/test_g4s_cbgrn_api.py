# -*- coding: utf-8 -*-

import pytest
from g4s.cbgrn.api import CybozuGaroonApi
from .util import raises_argument_null_error
from .util import raises_argument_type_error


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

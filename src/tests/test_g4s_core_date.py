# -*- coding: utf-8 -*-

import datetime
import dateutil.tz
import pytest
from g4s.core.arg import ArgumentNullError
from g4s.core.arg import ArgumentTypeError
from g4s.core.date import DateTime
from g4s.core.date import DateTimeParsingError
from g4s.core.date import TimeZone
from g4s.core.date import TimeZoneNotFoundError
from .util import fix_current_datetime
from .util import check_if_current_datetime_is_correctly_fixed
from .util import raises_argument_null_error
from .util import raises_argument_type_error


###
### fixture
###

@pytest.fixture(autouse=True)
def fixture(monkeypatch):
    fix_current_datetime(monkeypatch)


def test__fixture():
    check_if_current_datetime_is_correctly_fixed()


###
### g4s.core.date.DateTime.astimezone
###

def test__DateTime__astimezone__raises_ArgumentNullError_if_None_is_passed():
    dt = DateTime.get_utc_now()  # TODO

    with raises_argument_null_error('tzinfo'):
        dt.astimezone(None)


@pytest.mark.parametrize('tzinfo', [1, 2.34, 'foobar', object()])
def test__DateTime__astimezone__raises_ArgumentNullError_if_objects_except_TimeZone_are_passed(tzinfo):
    dt = DateTime.get_utc_now()  # TODO

    with raises_argument_type_error('tzinfo'):
        dt.astimezone(tzinfo)


def test__DateTime__astimezone__returns_correct_result():
    dt = DateTime.get_utc_now()
    tz = TimeZone.get('Asia/Tokyo')

    result = dt.astimezone(tz)
    expected_result = DateTime.get(2014, 1, 1, 9, 0, 0, tz)
    assert result == expected_result


###
### g4s.core.date.DateTime.__add__
###

def test__DateTime__add__raises_ArgumentNullError_if_None_is_passed():
    dt = DateTime.get_utc_now()  # TODO

    with raises_argument_null_error('delta'):
        dt.__add__(None)


@pytest.mark.parametrize('delta', [1, 2.34, 'foobar', object()])
def test__DateTime__add__raises_ArgumentTypeError_if_objects_except_timedelta_are_passed(delta):
    dt = DateTime.get_utc_now()  # TODO

    with raises_argument_type_error('delta'):
        dt.__add__(delta)


def test__DateTime__add__returns_correct_value():
    UTC = dateutil.tz.gettz('UTC')

    dt = DateTime.get_utc_now()  # TODO
    delta = datetime.timedelta(hours=3)
    result = dt + delta
    assert result == datetime.datetime(2014, 1, 1, 3, 0, 0, 0, tzinfo=UTC)

    dt = DateTime.get_utc_now()  # TODO
    delta = datetime.timedelta(hours=25)
    result = dt + delta
    assert result == datetime.datetime(2014, 1, 2, 1, 0, 0, 0, tzinfo=UTC)


###
### g4s.core.date.DateTime.get
###

def test__DateTime__get__raises_ArgumentNullError_if_None_is_passed_as_tzinfo():
    with pytest.raises(ArgumentNullError):
        DateTime.get(2014, 1, 1, 0, 0, 0, None)


@pytest.mark.parametrize('tzinfo', [1, 2.34, object(), dateutil.tz.gettz('Asia/Tokyo')])
def test__DateTime__get__raises_ArgumentTypeError_if_objects_except_TimeZone_and_str_are_passed_as_tzinfo(tzinfo):
    dt = DateTime.get_utc_now()  # TODO

    with raises_argument_type_error('tzinfo'):
        dt.get(2014, 1, 1, 0, 0, 0, tzinfo)


@pytest.mark.parametrize('tzinfo', [TimeZone.get('Asia/Tokyo'), 'Asia/Tokyo'])
def test__DateTime__get__returns_correct_result(tzinfo):
    result = DateTime.get(2014, 1, 1, 0, 0, 0, tzinfo)
    assert result.year == 2014
    assert result.month == 1
    assert result.day == 1
    assert result.hour == 0
    assert result.minute == 0
    assert result.second == 0
    assert result.tzinfo == TimeZone.get('Asia/Tokyo')


###
### g4s.core.date.DateTime.parse
###

@pytest.mark.parametrize('invalid_params', [
    dict(text=None), dict(tzinfo=None), dict(text=None, tzinfo=None)
])
def test__DateTime__parse__raises_ArgumentNullError_if_None_is_passed(invalid_params):
    params = dict(text='2014-01-01T00:00:00', tzinfo='Asia/Tokyo')
    params.update(invalid_params)
    with pytest.raises(ArgumentNullError):
        DateTime.parse(**params)

    params = dict(text='2014-01-01T00:00:00', tzinfo=TimeZone.get('Asia/Tokyo'))
    params.update(invalid_params)
    with pytest.raises(ArgumentNullError):
        DateTime.parse(**params)


@pytest.mark.parametrize('invalid_params', [
    dict(text=1), dict(text=2.34), dict(text=object()),
    dict(tzinfo=1), dict(text=2.34), dict(tzinfo=object()),
])
def test__DateTime__parse__raises_ArgumentTypeError_if_invalid_arguments_are_passed(invalid_params):
    params = dict(text='2014-01-01T00:00:00', tzinfo='Asia/Tokyo')
    params.update(invalid_params)
    with pytest.raises(ArgumentTypeError):
        DateTime.parse(**params)

    params = dict(text='2014-01-01T00:00:00', tzinfo=TimeZone.get('Asia/Tokyo'))
    params.update(invalid_params)
    with pytest.raises(ArgumentTypeError):
        DateTime.parse(**params)


@pytest.mark.parametrize('tzinfo', ['Asia/Tokyo', TimeZone.get('Asia/Tokyo')])
def test__DateTime__parse__accepts_str_and_TimeZone_as_tzinfo(tzinfo):
    DateTime.parse('2014-01-01T00:00:00', tzinfo)


@pytest.mark.parametrize('text', ['foo', 'foo-bar'])
def test__DateTime__parse__raises_DateTimeParsingError_if_invalid_text_is_specified(text):
    with pytest.raises(DateTimeParsingError):
        DateTime.parse(text, 'Asia/Tokyo')


@pytest.mark.parametrize('tzinfo', ['Asia/Tokyo', TimeZone.get('Asia/Tokyo')])
def test__DateTime__parse__returns_correct_result(tzinfo):
    result = DateTime.parse('2014-01-02T03:04:05', tzinfo)
    expected_result = DateTime.get(2014, 1, 2, 3, 4, 5, 'Asia/Tokyo')
    assert result == expected_result


###
### g4s.core.date.DateTime.get_utc_now
###

def test__DateTime__get_utc_now__returns_correct_result():
    result = DateTime.get_utc_now()
    expected_result = DateTime.get(2014, 1, 1, 0, 0, 0, 'UTC')
    assert result == expected_result


###
### g4s.core.date.DateTimeParsingError
###

def test__DateTimeParsingError__message__returns_correct_result():
    error = DateTimeParsingError('foo')
    assert isinstance(error.message, str)


def test__DateTimeParsingError__text__returns_correct_result():
    error = DateTimeParsingError('foo')
    assert error.text == 'foo'


###
### g4s.core.date.TimeZone.__init__
###

@pytest.mark.parametrize('invalid_params', [
    dict(instance=None), dict(g4s_name=None), dict(instance=None, g4s_name=None)
])
def test__TimeZone__init__raises_ArgumentNullError_if_None_is_specified(invalid_params):
    params = dict(instance=dateutil.tz.gettz('Asia/Tokyo'), g4s_name='Asia/Tokyo')
    params.update(invalid_params)

    with pytest.raises(ArgumentNullError):
        TimeZone(**params)


@pytest.mark.parametrize('invalid_params', [
    dict(instance=1), dict(instance=2.34), dict(instance='foo'), dict(instance=object()),
    dict(g4s_name=1), dict(g4s_name=2.34), dict(g4s_name=object()),
])
def test__TimeZone__init__raises_ArgumentTypeError_if_invalid_type_argument_is_specified(invalid_params):
    params = dict(instance=dateutil.tz.gettz('Asia/Tokyo'), g4s_name='Asia/Tokyo')
    params.update(invalid_params)

    with pytest.raises(ArgumentTypeError):
        TimeZone(**params)


###
### g4s.core.date.TimeZone.__eq__
###

def test__TimeZone__eq__returns_correct_result():
    #
    params = dict(instance=dateutil.tz.gettz('Asia/Tokyo'), g4s_name='Asia/Tokyo')

    tz1 = TimeZone(**params)
    tz2 = TimeZone(**params)

    #
    assert tz1.__eq__(tz2)
    assert tz2.__eq__(tz1)

    #
    assert not tz1.__eq__(None)
    assert not tz1.__eq__(1)
    assert not tz1.__eq__(2.34)
    assert not tz1.__eq__('Asia/Tokyo')
    assert not tz1.__eq__(object())


###
### g4s.core.date.TimeZone.__ne__
###

def test__TimeZone__ne__returns_correct_result():
    #
    params = dict(instance=dateutil.tz.gettz('Asia/Tokyo'), g4s_name='Asia/Tokyo')

    tz1 = TimeZone(**params)
    tz2 = TimeZone(**params)

    #
    assert not tz1.__ne__(tz2)
    assert not tz2.__ne__(tz1)

    #
    assert tz1.__ne__(None)
    assert tz1.__ne__(1)
    assert tz1.__ne__(2.34)
    assert tz1.__ne__('Asia/Tokyo')
    assert tz1.__ne__(object())


###
### g4s.core.date.TimeZone.get
###

def test__TimeZone__get__raises_ArgumentNullError_if_None_is_specified():
    with raises_argument_null_error('name'):
        TimeZone.get(None)


@pytest.mark.parametrize('obj', [1, 2.34, object()])
def test__TimeZone__get__raises_ArgumentTypeError_if_objects_except_str_are_passed(obj):
    with raises_argument_type_error('name'):
        TimeZone.get(obj)


@pytest.mark.parametrize('name', ['', 'foo', 'JST'])
def test__TimeZone__get__raises_TimeZoneNotFoundError_if_invalid_timezone_name_is_specified(name):
    with pytest.raises(TimeZoneNotFoundError):
        TimeZone.get(name)


@pytest.mark.parametrize('name', ['UTC', 'GMT', 'Asia/Tokyo'])
def test__TimeZone__get__returns_correct_result(name):
    tz = TimeZone.get(name)

    assert isinstance(tz, TimeZone)
    assert tz.g4s_name == name


###
### g4s.core.date.TimeZoneNotFoundError
###

def test__TimeZoneNotFoundError__message_returns_correct_result():
    error = TimeZoneNotFoundError('foo')
    assert isinstance(error.message, str)


def test__TimeZoneNotFoundError__name_returns_correct_result():
    error = TimeZoneNotFoundError('foo')
    assert error.name == 'foo'

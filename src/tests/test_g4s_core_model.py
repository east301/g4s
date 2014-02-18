# -*- coding: utf-8 -*-

import mock
import pytest
from g4s.core.arg import ArgumentNullError
from g4s.core.arg import ArgumentTypeError
from g4s.core.date import DateTime
from g4s.core.model import Event
from g4s.core.model import InvalidEventDateTimePairError
from g4s.core.model import Participant
from .util import raises_argument_null_error
from .util import raises_argument_type_error


###
### g4s.core.model.Participant
###

def test__Participant__init__raises_ArgumentNullError_if_None_is_passed_as_name():
    with raises_argument_null_error('name'):
        Participant(1, None)


@pytest.mark.parametrize('name', [1, 2.34, object()])
def test__Participant__init__raises_ArgumentTypeError_if_object_except_str_are_passed_as_name(name):
    with raises_argument_type_error('name'):
        Participant(1, name)


def test__Participant__id__returns_correct_result():
    p = Participant(1, 'foo')
    assert p.id == 1


def test__Participant__name__returns_correct_result():
    p = Participant(1, 'foo')
    assert p.name == 'foo'


###
### g4s.core.model.Event.__init__
###

DEFAULT_EVENT = dict(
    id=1,
    type=Event.NORMAL,
    title='title',
    description='description',
    start=DateTime.get(2014, 1, 1, 9, 0, 0, 'UTC'),
    end=DateTime.get(2014, 1, 1, 12, 0, 0, 'UTC'),
    is_allday=False,
    participants=[mock.Mock(spec=Participant)],
    is_public=True,
    last_update=DateTime.get(2014, 1, 1, 0, 0, 0, 'UTC'))


def test__Event__init__returns_correct_result():
    event = Event(**DEFAULT_EVENT)

    assert event.id == DEFAULT_EVENT['id']
    assert event.title == DEFAULT_EVENT['title']
    assert event.description == DEFAULT_EVENT['description']
    assert event.start == DEFAULT_EVENT['start']
    assert event.end == DEFAULT_EVENT['end']
    assert event.is_allday == DEFAULT_EVENT['is_allday']
    assert event.is_public == DEFAULT_EVENT['is_public']
    assert event.last_update == DEFAULT_EVENT['last_update']


###
### g4s.core.model.Event.is_same_event
###

def test__Event__is_same_event__raises_ArgumentNullError_if_None_is_specified():
    event = Event(**DEFAULT_EVENT)

    with raises_argument_null_error('other'):
        event.is_same_event(None)


@pytest.mark.parametrize('other', [1, 2.34, 'foo', object()])
def test__Event__is_same_event__raises_ArgumentTypeError_if_object_except_Event_is_specified(other):
    event = Event(**DEFAULT_EVENT)

    with raises_argument_type_error('other'):
        event.is_same_event(other)


@pytest.mark.parametrize('params', [
    dict(),
    dict(id=100),
    dict(last_update=mock.Mock(spec=DateTime)),
    dict(participants=[mock.Mock(spec=Participant), mock.Mock(spec=Participant)]),
])
def test__Event__is_same_event__returns_correct_result__001(params):
    event1 = Event(**DEFAULT_EVENT)
    event2 = Event(**dict(tuple(DEFAULT_EVENT.items()) + tuple(params.items())))

    assert event1.is_same_event(event2)
    assert event2.is_same_event(event1)


@pytest.mark.parametrize('params', [
    dict(title='foo'),
    dict(description='foo'),
    dict(start=DateTime.get(2014, 1, 1, 8, 0 ,0, 'UTC')),
    dict(end=None),
    dict(end=DateTime.get(2014, 1, 1, 13, 0, 0, 'UTC')),
    dict(is_allday=True),
])
def test__Event__is_same_event__returns_correct_result__002(params):
    event1 = Event(**DEFAULT_EVENT)
    event2 = Event(**dict(tuple(DEFAULT_EVENT.items()) + tuple(params.items())))

    assert not event1.is_same_event(event2)
    assert not event2.is_same_event(event1)


###
### g4s.core.model.Event.to_dict
###

def test__Event__to_dict__returns_correct_result():
    event = Event(**DEFAULT_EVENT)
    event_dict = event.to_dict()

    assert isinstance(event_dict, dict)
    assert len(event_dict) == len(DEFAULT_EVENT) - 1

    for key, expected_result in event_dict.items():
        if key == 'participants':
            continue

        assert key in event_dict
        assert event_dict[key] == expected_result


###
### g4s.core.model.Event.validate_type
###

def test__Event__validate_type__raises_ArgumentNullError_if_None_is_specified():
    with raises_argument_null_error('type'):
        Event.validate_type(None)


@pytest.mark.parametrize('value', [2.34, 'foo', object()])
def test__Event__validate_type__raises_ArgumentTypeError_if_objects_except_int_are_specified(value):
    with raises_argument_type_error('type'):
        Event.validate_type(value)


@pytest.mark.parametrize('value', [-2, -1, 2, 3])
def test__Event__validate_type__raises_ValueError_if_invalid_type_is_specified(value):
    with pytest.raises(ValueError):
        Event.validate_type(value)


@pytest.mark.parametrize('value', [Event.NORMAL, Event.BANNER])
def test__Event__validate_type__returns_correct_result(value):
    result = Event.validate_type(value)
    assert result == value


###
### g4s.core.model.Event.validate_text
###

def test__Event__validate_text__raises_ArgumentNullError_if_None_is_specified_as_title():
    with raises_argument_null_error('title'):
        Event.validate_text(None, None)


@pytest.mark.parametrize('text', [1, 2.34, object()])
def test__Event__validate_text__raises_ArgumentTypeError_if_object_except_str_is_specified_as_title_or_description(text):
    with raises_argument_type_error('title'):
        Event.validate_text(text, 'foo')

    with raises_argument_type_error('description'):
        Event.validate_text('foo', text)


@pytest.mark.parametrize(['title', 'description'], [
    ['title', 'description'], ['title', None]
])
def test__Event__validate_text__returns_correct_result(title, description):
    result_title, result_description = Event.validate_text(title, description)
    assert result_title == title
    assert result_description == description


###
### g4s.core.model.Event.validate_datetime
###

def test__Event__validate_datetime__raises_ArgumentNullError_if_None_is_specified_as_start():
    end = mock.Mock(spec=DateTime)
    with raises_argument_null_error('start'):
        Event.validate_datetime(None, end, False)


@pytest.mark.parametrize('value', [1, 2.34, 'foo', object()])
def test__Event__validate_datetime__raises_ArgumentTypeError_if_object_except_DateTime_is_specified_as_start_or_end(value):
    end = mock.Mock(spec=DateTime)
    with raises_argument_type_error('start'):
        Event.validate_datetime(value, end, False)

    start = mock.Mock(spec=DateTime)
    with raises_argument_type_error('end'):
        Event.validate_datetime(start, value, False)


@pytest.mark.parametrize(['start', 'end', 'is_allday'], [
    # end -> start
    # TODO: use mock
    [DateTime.get(2014, 1, 1, tzinfo='UTC'), DateTime.get(2013, 1, 1, tzinfo='UTC'), False],

    # is_allday=True, however, end is not specified
    [mock.Mock(spec=DateTime), None, True],
])
def test__Event__validate_datetime__raises_InvalidEventDateTimePair_if_invalid_arguments_are_specified(
        start, end, is_allday):
    with pytest.raises(InvalidEventDateTimePairError):
        Event.validate_datetime(start, end, is_allday)


@pytest.mark.parametrize(['start', 'end', 'is_allday'], [
    [DateTime.get(2014, 1, 1, tzinfo='UTC'), DateTime.get(2014, 1, 1, tzinfo='UTC'), False],
    [DateTime.get(2014, 1, 1, tzinfo='UTC'), DateTime.get(2014, 1, 2, tzinfo='UTC'), False],
    [DateTime.get(2014, 1, 1, tzinfo='UTC'), None, False],
    [DateTime.get(2014, 1, 1, tzinfo='UTC'), DateTime.get(2014, 1, 2, tzinfo='UTC'), True],
])
def test__Event__validate_datetime__returns_correct_result(start, end, is_allday):
    result_start, result_end, result_is_allday = Event.validate_datetime(start, end, is_allday)
    assert result_start == start
    assert result_end == end
    assert result_is_allday == is_allday


###
### g4s.core.model.Event.validate_participants
###

def test__Event__validate_participants__raises_ArgumentNullError_if_None_is_specified_as_participants():
    with raises_argument_null_error('participants'):
        Event.validate_participants(None, None)

    with raises_argument_null_error('participants'):
        Event.validate_participants(None, Participant)


@pytest.mark.parametrize('value', [1, 2.34, object()])
def test__Event__validate_participants__raises_ArgumentTypeError_if_participants_is_not_collection(value):
    with raises_argument_type_error('participants'):
        Event.validate_participants(value, None)

    with raises_argument_type_error('participants'):
        Event.validate_participants(value, Participant)


@pytest.mark.parametrize(['participants', 'expected_type'], [
    [[1, 2], Participant],
    [[mock.Mock(spec=Participant), 2], Participant],
])
def test__Event__validate_participants__raises_ArgumentTypeError_if_participants_contains_unexpected_type_of_elements(
        participants, expected_type):
    with raises_argument_type_error('participants[*]'):
        Event.validate_participants(participants, expected_type)


def test__Event__validate_participants__returns_correct_result():
    participants = mock.Mock(spec=Participant), mock.Mock(spec=Participant)
    result = Event.validate_participants(participants)

    assert len(participants) == len(result)
    for participant in participants:
        assert participant in result


###
### g4s.core.model.Event.from_dict
###

def test__Event__from_dict__raises_ArgumentNullError_if_None_is_specified():
    with raises_argument_null_error('instance'):
        Event.from_dict(None)


@pytest.mark.parametrize('obj', [1, 2.34, 'foo', object()])
def test__Event__from_dict__raises_ArgumentTypeError_if_object_except_dict_is_specified(obj):
    with raises_argument_type_error('instance'):
        Event.from_dict(obj)


def test__Event__from_dict__returns_correct_result():
    event = Event.from_dict(DEFAULT_EVENT)

    assert event.id == DEFAULT_EVENT['id']
    assert event.title == DEFAULT_EVENT['title']
    assert event.description == DEFAULT_EVENT['description']
    assert event.start == DEFAULT_EVENT['start']
    assert event.end == DEFAULT_EVENT['end']
    assert event.is_allday == DEFAULT_EVENT['is_allday']
    assert event.is_public == DEFAULT_EVENT['is_public']
    assert event.last_update == DEFAULT_EVENT['last_update']
    assert len(event.participants) == 0


###
### g4s.core.model.Event.get_difference
###

def test__Event__get_difference__raises_ArgumentNullError_if_None_is_specified():
    event = Event(**DEFAULT_EVENT)

    with raises_argument_null_error('other'):
        event.get_difference(None)


@pytest.mark.parametrize('obj', [1, 2.34, 'foo', object()])
def test__Event__get_difference__raises_ArgumentTypeError_if_object_except_Event_is_specified(obj):
    event = Event(**DEFAULT_EVENT)

    with raises_argument_type_error('other'):
        event.get_difference(obj)


@pytest.mark.parametrize('expected_result', [
    dict(), dict(title='a'), dict(title='foo', description='bar'),
])
def test__Event__get_difference__returns_correct_result__001(expected_result):
    event_params1 = DEFAULT_EVENT.copy()
    event_params2 = DEFAULT_EVENT.copy()
    event_params2.update(expected_result)

    event1 = Event(**event_params1)
    event2 = Event(**event_params2)

    result = event1.get_difference(event2)

    assert len(result) == len(expected_result)
    for key in expected_result.keys():
        assert key in result
        assert result[key][0] == event_params1[key]
        assert result[key][1] == event_params2[key]


###
### g4s.core.model.InvalidEventDateTimePairError
###

def test__InvalidEventDateTimePairError__message__returns_correct_result():
    start = mock.Mock(spec=DateTime)
    end = mock.Mock(spec=DateTime)
    error = InvalidEventDateTimePairError(start, end, False)

    assert isinstance(error.message, str)


def test__InvalidEventDateTimePairError__start__returns_correct_result():
    start = mock.Mock(spec=DateTime)
    end = mock.Mock(spec=DateTime)
    error = InvalidEventDateTimePairError(start, end, False)

    assert error.start == start


def test__InvalidEventDateTimePairError__end__returns_correct_result():
    start = mock.Mock(spec=DateTime)
    end = mock.Mock(spec=DateTime)
    error = InvalidEventDateTimePairError(start, end, False)

    assert error.end == end


def test__InvalidEventDateTimePairError__is_allday__returns_correct_result():
    start = mock.Mock(spec=DateTime)
    end = mock.Mock(spec=DateTime)
    error = InvalidEventDateTimePairError(start, end, False)

    assert not error.is_allday

# -*- coding: utf-8 -*-

import mock
import pytest
from g4s.core.arg import ArgumentNullError
from g4s.core.arg import ArgumentTypeError
from g4s.core.date import DateTime
from g4s.core.model import Event
from g4s.core.model import Participant
from g4s.core.sync import EventMappingError
from g4s.core.sync import perform_event_mapping
from .util import raises_argument_null_error


###
### g4s.core.sync.perform_event_mapping
###

# TODO: use mock objects
EVENT1 = Event(
    id=1,
    type=Event.NORMAL,
    title='title1',
    description='description1',
    start=DateTime.get(2014, 1, 1, 9, 0, 0, 'UTC'),
    end=DateTime.get(2014, 1, 1, 12, 0, 0, 'UTC'),
    is_allday=False,
    participants=[mock.Mock(spec=Participant)],
    is_public=True,
    last_update=DateTime.get(2014, 1, 1, 0, 0, 0, 'UTC'))

EVENT2 = Event(
    id=1,
    type=Event.NORMAL,
    title='title1',
    description='description1',
    start=DateTime.get(2014, 1, 1, 9, 0, 0, 'UTC'),
    end=DateTime.get(2014, 1, 1, 12, 0, 0, 'UTC'),
    is_allday=False,
    participants=[mock.Mock(spec=Participant)],
    is_public=True,
    last_update=DateTime.get(2014, 1, 1, 0, 0, 0, 'UTC'))

EVENT3 = Event(
    id=1,
    type=Event.NORMAL,
    title='title1',
    description='description1',
    start=DateTime.get(2014, 1, 1, 9, 0, 0, 'UTC'),
    end=DateTime.get(2014, 1, 1, 12, 0, 0, 'UTC'),
    is_allday=False,
    participants=[mock.Mock(spec=Participant)],
    is_public=True,
    last_update=DateTime.get(2014, 1, 1, 0, 0, 0, 'UTC'))

EVENT4 = Event(
    id=3,
    type=Event.NORMAL,
    title='title3',
    description='description3',
    start=DateTime.get(2014, 1, 3, 9, 0, 0, 'UTC'),
    end=DateTime.get(2014, 1, 3, 12, 0, 0, 'UTC'),
    is_allday=False,
    participants=[mock.Mock(spec=Participant)],
    is_public=True,
    last_update=DateTime.get(2014, 1, 1, 0, 0, 0, 'UTC'))

EVENT5 = Event(
    id=3,
    type=Event.NORMAL,
    title='title4',
    description='description4',
    start=DateTime.get(2014, 1, 4, 9, 0, 0, 'UTC'),
    end=DateTime.get(2014, 1, 4, 12, 0, 0, 'UTC'),
    is_allday=False,
    participants=[mock.Mock(spec=Participant)],
    is_public=True,
    last_update=DateTime.get(2014, 1, 1, 0, 0, 0, 'UTC'))


def test__perform_event_mapping__raises_ArgumentNullError_if_None_is_specified_as_events():
    with raises_argument_null_error('events1'):
        perform_event_mapping(None, tuple())

    with raises_argument_null_error('events2'):
        perform_event_mapping(tuple(), None)


def test__perform_event_mapping__raises_EventMappingError_if_failed_to_perform_mapping():
    #
    events1 = EVENT1,
    events2 = EVENT2, EVENT3, EVENT4

    with pytest.raises(EventMappingError) as excinfo:
        perform_event_mapping(events1, events2)

    assert excinfo.value.event == EVENT1
    assert len(excinfo.value.opponent_events)
    assert EVENT2 in excinfo.value.opponent_events
    assert EVENT3 in excinfo.value.opponent_events

    #
    events1 = EVENT2, EVENT3, EVENT4
    events2 = EVENT1,

    with pytest.raises(EventMappingError) as excinfo:
        perform_event_mapping(events1, events2)

    assert excinfo.value.event == EVENT1
    assert len(excinfo.value.opponent_events)
    assert EVENT2 in excinfo.value.opponent_events
    assert EVENT3 in excinfo.value.opponent_events


@pytest.mark.parametrize(['events1', 'events2', 'expected_common', 'expected_c1only', 'expected_c2only'], [
    [[EVENT1], [EVENT1], [(EVENT1, EVENT1)], [], []],
    [[EVENT1], [EVENT2], [(EVENT1, EVENT2)], [], []],
    [[EVENT1], [EVENT4], [], [EVENT1], [EVENT4]],
    [[EVENT1], [EVENT2, EVENT4], [(EVENT1, EVENT2)], [], [EVENT4]],
    [[EVENT1, EVENT5], [EVENT2, EVENT4], [(EVENT1, EVENT2)], [EVENT5], [EVENT4]],
])
def test__perform_event_mapping__returns_correct_result(
        events1, events2, expected_common, expected_c1only, expected_c2only):
    common, c1only, c2only = perform_event_mapping(events1, events2)

    assert common is not None
    assert c1only is not None
    assert c2only is not None

    assert len(common) == len(expected_common)
    assert len(c1only) == len(expected_c1only)
    assert len(c2only) == len(expected_c2only)

    for event1, event2 in expected_common:
        assert (event1, event2) in common

    for event in expected_c1only:
        assert event in c1only

    for event in expected_c2only:
        assert event in c2only


###
### g4s.core.sync.EventMappingError
###

def test__EventMappingError__event__returns_correct_result():
    event = mock.Mock(spec=Event)
    opponent_events = mock.Mock(spec=Event), mock.Mock(spec=Event)
    error = EventMappingError(event, opponent_events)

    assert error.event == event


def test__EventMappingError__opponent_events__returns_correct_result():
    event = mock.Mock(spec=Event)
    opponent_events = mock.Mock(spec=Event), mock.Mock(spec=Event)
    error = EventMappingError(event, opponent_events)

    result = error.opponent_events

    assert len(result) == len(opponent_events)
    for opponent_event in opponent_events:
        assert opponent_event in result

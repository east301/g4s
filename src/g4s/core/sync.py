# -*- coding: utf-8 -*-

"""
Calendar event synchronization.
"""

__all__ = (
    'perform_event_mapping',
    'EventMappingError',
)

from .arg import ArgumentNullError
from .debug import LogicError


def perform_event_mapping(events1, events2):
    """
    Peforms event mapping.

    :param events1: events in the first calendar
    :param events2: events in the second calendar
    :type  events1: list of :py:class:`g4s.core.model.Event`
    :type  events2: list of :py:class:`g4s.core.model.Event`

    :rtype:  list of :py:class:`g4s.core.model.Event`
    :return:
        a tuple which contains tuple of common events, tuple of events only in the first calendar,
        and tuple of events only in the second calendar

    :raises g4s.core.date.ArgumentNullError:
        if ``events1`` or ``events2`` is :py:const:`None`
    :raises g4s.core.date.EventMappingError:
        if failed to parform event mapping
    """

    # check arguments
    if events1 is None:
        raise ArgumentNullError('events1')
    if events2 is None:
        raise ArgumentNullError('events2')

    # event1 -> event2
    common_events = []
    calendar1_only_events = []

    for event1 in events1:
        matched_events = []
        for event2 in events2:
            if event1.is_same_event(event2):
                matched_events.append(event2)

        if len(matched_events) == 0:
            calendar1_only_events.append(event1)
        elif len(matched_events) == 1:
            common_events.append((event1, matched_events[0]))
        else:
            raise EventMappingError(event1, matched_events)

    # event2 -> event1
    calendar2_only_events = []

    for event2 in events2:
        matched_events = []
        for event1 in events1:
            if event2.is_same_event(event1):
                matched_events.append(event1)

        if len(matched_events) == 0:
            calendar2_only_events.append(event2)
        elif len(matched_events) == 1:
            if (matched_events[0], event2) not in common_events:  # pragma: no cover
                raise LogicError()
        else:
            raise EventMappingError(event2, matched_events)

    # validation
    events = frozenset(e1 for e1, e2 in common_events) | frozenset(calendar1_only_events)
    if events != frozenset(events1):  # pragma: no cover
        raise LogicError()

    events = frozenset(e2 for e1, e2 in common_events) | frozenset(calendar2_only_events)
    if events != frozenset(events2):  # pragma: no cover
        raise LogicError()

    return tuple(common_events), tuple(calendar1_only_events), tuple(calendar2_only_events)


class EventMappingError(Exception):
    """
    An exception which is thrown when failed to perform event mapping.
    """

    def __init__(self, event, opponent_events):
        """
        Initializes an instance of :py:class:`EventMappingError` class.

        :param event:           event
        :param opponent_events: matched events
        :type  event:           :py:class:`g4s.core.model.Event`
        :type  opponent_events: list of :py:class:`g4s.core.model.Event`
        """

        self._event = event
        self._opponent_events = tuple(opponent_events)

    @property
    def event(self):
        """
        Gets the event.

        :rtype:  :py:class:`g4s.core.model.Event`
        :return: the event
        """

        return self._event

    @property
    def opponent_events(self):
        """
        Gets the matched events.

        :rtype:  list of :py:class:`g4s.core.model.Event`
        :return: list of the matched events
        """

        return self._opponent_events

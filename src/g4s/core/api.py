# -*- coding: utf-8 -*-

"""
Calendar API interface.
"""

__all__ = (
    'CalendarApi',
    'NetworkError',
    'ResponseParseError',
)

from .arg import ArgumentNullError
from .arg import ArgumentTypeError


class CalendarApi(object):
    """
    Calendar API interface.

    :py:class:`g4s.core.api.CalendarApi` interacts external calendar server. It issues requests to
    manipulate calendar events on the server, and parses responses from the server. Typical usage
    is shown below:

    .. code-block:: python

        server_specific_params = dict(user='foo', password='bar')
        api = g4s.core.api.CalendarApi(server_specific_params)

        start = g4s.core.date.DateTime.get_utc_now()
        end = start + datetime.timedelta(days=30)
        retrieved_events = api.get_events(start, end)

        for event in retrieved_events:
            print(event)
    """

    def __init__(self, params):
        """
        Initializes an instance of :py:class:`CalendarApi` class.

        :param params: parameters
        :type  params: dict

        :raises g4s.core.arg.ArgumentNullError: if ``params`` is :py:const:`None`
        :raises g4s.core.arg.ArgumentTypeError: if ``params`` is not :py:class:`dict`
        """

        if params is None:
            raise ArgumentNullError('params')
        if not isinstance(params, dict):
            raise ArgumentTypeError('params', dict)

    def get_events(self, start, end):
        """
        Gets events in the specified range.
        This method must be implemented in derived class.

        :param start: start of retrieval
        :param end:   end of retrieval
        :type  start: :py:class:`g4s.core.date.DateTime`
        :type  end:   :py:class:`g4s.core.date.DateTime`

        :rtype:  list of :py:class:`g4s.core.model.Event`
        :return: a collection which contains retrieved events
        """

        raise NotImplementedError  # pragma: no cover

    def add_events(self, events):
        """
        Adds the specified events.
        This method must be implemented in derived class.

        :param events: a collection of events to be added
        :type  events: list of :py:class:`g4s.core.model.Event`

        :rtype:  list of :py:class:`g4s.core.model.Event`
        :return: a collection which contains added events
        """

        raise NotImplementedError  # pragma: no cover

    def modify_events(self, events):
        """
        Modifies the specified events.
        This method should be implemented in derived class.

        :param events:
            a :py:class:`dict` which maps old event to a dict which contains difference between old
            event and new event. The events included in ``events.keys()`` must have valid ID.
            to.
        :type events:  dict of (g4s.core.model.Event, dict)

        :rtype:  dict of (:py:class:`g4s.core.model.Event`, :py:class:`g4s.core.model.Event`)
        :return: a :py:class:`dict` which maps old event to new event.
        """

        raise NotImplementedError  # pragma: no cover

    def remove_events(self, events):
        """
        Removes the specified events.
        This method must be implemented in derived class.

        :param events: a collection of events to be removed
        :type  events: :py:class:`g4s.core.model.Event`

        :rtype:  list of :py:class:`g4s.core.model.Event`
        :return: a tuple which contains removed events
        """

        raise NotImplementedError  # pragma: no cover

    @property
    def is_event_modification_supported(self):
        """
        Returns boolean value which indicates whether the calendar api supports modification of
        properties of events in remote server. If this property returns :py:const:`True`,
        :py:meth:`g4s.core.api.CalendarApi.modify_events` must be implemented in derived class.

        :rtype: bool
        :return: :py:const:`True` if the calendar api supports modification of events, otherwise
                 :py:const:`False`
        """

        return False  # pragma: no cover


class NetworkError(IOError):
    """
    An exception which is raised when a network error is happened.
    """

    pass


class ResponseParseError(ValueError):
    """
    An exception which is raised when failed to parse response from remote server.
    """

    pass

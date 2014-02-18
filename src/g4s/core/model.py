# -*- coding: utf-8 -*-

"""
Calendar event representation.
"""

__all__ = (
    'Participant',
    'Event',
    'InvalidEventDateTimePairError',
)

from .arg import ArgumentNullError
from .arg import ArgumentTypeError
from .date import DateTime
from .debug import LogicError


class Participant(object):
    """
    Represents a participant of a event.
    """

    def __init__(self, id, name):
        """
        Initializes an instance of :py:class:`Participant` class.

        :param id:   ID of the participant
        :param name: name of the participant
        :type  name: str

        :raises g4s.core.arg.ArgumentNullError: if the ``name`` is :py:const:`None`
        :raises g4s.core.arg.ArgumentTypeError: if the ``name`` is not :py:class:`str`
        """

        if name is None:
            raise ArgumentNullError('name')
        if not isinstance(name, str):
            raise ArgumentTypeError('name', str)

        self.id = id
        self.name = name


class Event(object):
    """
    Represents an event.
    """

    NORMAL = 0
    BANNER = 1

    def __init__(
            self, id, type, title, description, start, end, is_allday, participants,
            is_public, last_update):
        """
        Initializes an instance of :py:class:`Event` class.

        :param id:           ID
        :param type:         event type
        :param title:        title text
        :param description:  description text, or :py:const:`None`
        :param start:        start date time
        :param end:          end date time, or :py:const:`None`
        :param is_allday:    all-day event flag
        :param participants: collection of participants
        :param last_update:  last-update date time
        :type type:          int
        :type title:         str
        :type description:   str
        :type start:         :py:class:`g4s.core.date.DateTime`
        :type end:           :py:class:`g4s.core.date.DateTime`
        :type is_allday:     bool
        :type participants:  list of :py:class:`g4s.core.model.Participant`
        :type last_update:   :py:class:`g4s.core.date.DateTime`
        """

        type = Event.validate_type(type)
        title, description = Event.validate_text(title, description)
        start, end, is_allday = Event.validate_datetime(start, end, is_allday)
        participants = Event.validate_participants(participants, Participant)

        self.id = id
        self.type = type
        self.title = title
        self.description = description
        self.start = start
        self.end = end
        self.is_allday = is_allday
        self.participants = participants
        self.is_public = is_public
        self.last_update = last_update

    def is_same_event(self, other):
        """
        Checks if the specified event is an equivalent to the event.

        :param other: check target event
        :type other:  :py:class:`g4s.core.model.Event`

        :rtype:  bool
        :result:
            :py:const:`True` if the specified event is the same event, otherwise :py:const:`False`

        :raises g4s.core.arg.ArgumentNullError:
            if the ``other`` argument is :py:const:`None`.
        :raises g4s.core.arg.ArgumentTypeError:
            if the ``other`` argument is not :py:const:`g4s.core.model.Event`.
        """

        if other is None:
            raise ArgumentNullError('other')
        if not isinstance(other, Event):
            raise ArgumentTypeError('other', Event)

        return (
            self.title == other.title and
            self.description == other.description and
            self.start == other.start and
            self.end == other.end and
            self.is_allday == other.is_allday
        )

    def to_dict(self):
        """
        Converts contents of the event to :py:class:`dict`.
        The dict created by this method can be converted back using
        :py:meth:`g4s.core.model.Event.from_dict`.

        :rtype:  dict
        :return: a dict which contains contents of the event

        .. note::

           The ``participants`` field cannot be serialized.
        """

        return dict(
            id=self.id,
            type=self.type,
            title=self.title,
            description=self.description,
            start=self.start,
            end=self.end,
            is_allday=self.is_allday,
            is_public=self.is_public,
            last_update=self.last_update
        )

    def get_difference(self, other):
        """
        Gets differences between the two events.

        :param other: an event to be compared
        :type other:  :py:class:`g4s.core.model.Event`

        :raises g4s.core.arg.ArgumentNullError:
            if ``other`` is :py:const:`None`
        :raises g4s.core.arg.ArgumentTypeError:
            if ``other`` is not :py:class:`g4s.core.model.Event`

        .. note::

            This method does not detect difference of ``participants`` field.
        """

        #
        if other is None:
            raise ArgumentNullError('other')
        if not isinstance(other, Event):
            raise ArgumentTypeError('other', Event)

        #
        ed1 = self.to_dict()
        ed2 = other.to_dict()

        keys = set(ed1).intersection(set(ed2))
        if (keys != set(ed1)) or (keys != set(ed2)):
            raise LogicError  # pragma: no cover

        return dict((k, (ed1[k], ed2[k])) for k in keys if ed1[k] != ed2[k])

    @classmethod
    def validate_type(cls, type):
        """
        Validates type of an event.

        :param type: event type
        :type type:  int

        :rtype:  int
        :return: event type

        :raises g4s.core.arg.ArgumentNullError: if ``type`` is :py:const:`None` or invalid value
        :raises g4s.core.arg.ArgumentTypeError: if ``type`` is not :py:class:`int`
        :raises ValueError:                     if invalid ``type`` is specified
        """

        if type is None:
            raise ArgumentNullError('type')
        if not isinstance(type, int):
            raise ArgumentTypeError('type', int)
        if type not in (Event.NORMAL, Event.BANNER):
            raise ValueError('The specified type is not valid.')

        return type

    @classmethod
    def validate_text(cls, title, description):
        """
        Validates title and description of an event.

        :param title:       event title text
        :param description: event description text, or :py:const:`None`
        :type title:        str
        :type description:  str

        :rtype:  (str, str)
        :return: a tuple which contains title and description of the event

        :raises g4s.core.arg.ArgumentNullError:
            if ``title`` is :py:const:`None`
        :raises g4s.core.arg.ArgumentTypeError:
            if ``title`` or ``description`` is not :py:class:`str`
        """

        if title is None:
            raise ArgumentNullError('title')
        if not isinstance(title, str):
            raise ArgumentTypeError('title', str)

        if description is not None:
            if not isinstance(description, str):
                raise ArgumentTypeError('description', str)

        return title, description

    @classmethod
    def validate_datetime(cls, start, end, is_allday):
        """
        Validates start/end datetime and all-day event flag of an event.

        :param start:     start date time
        :param end:       end date time, or :py:const:`None`
        :param is_allday: all-day event flag
        :type start:      :py:class:`g4s.core.date.DateTime`
        :type end:        :py:class:`g4s.core.date.DateTime`
        :type is_allday:  bool

        :rtype:  (:py:class:`g4s.core.date.DateTime`, :py:class:`g4s.core.date.DateTime`, bool)
        :return: a tuple which contains start/end datetime and all-day flag fo the event

        :raises g4s.core.arg.ArgumentNullError:
            if ``start`` is :py:const:`None`
        :raises g4s.core.arg.ArgumentTypeError:
            if ``start`` or ``end`` is not :py:class:`DateTime`
        :raises g4s.core.model.InvalidEventDateTimePairError:
            if invalid triplet of ``start``, ``end`` and ``is_allday`` is specified
        """

        if not start:
            raise ArgumentNullError('start')
        if not isinstance(start, DateTime):
            raise ArgumentTypeError('start', DateTime)

        if end:
            if not isinstance(end, DateTime):
                raise ArgumentTypeError('end', DateTime)
            if start > end:
                raise InvalidEventDateTimePairError(start, end, is_allday)

        else:
            if is_allday:
                raise InvalidEventDateTimePairError(start, end, is_allday)

        return start, end, is_allday

    @classmethod
    def validate_participants(cls, participants, expected_type=None):
        """
        Valdates ``participants`` value of an event.

        :param participants: list of participants
        :type participants:  list of :py:class:`g4s.core.model.Participant`

        :rtype:  list of :py:class:`g4s.core.model.Participant`
        :return: a tuple which contains participants

        :raises g4s.core.arg.ArgumentNullError:
            if ``participants`` is :py:const:`None`
        :raises g4s.core.arg.ArgumentTypeError:
            if ``participants`` is not a collection, or ``expected_type`` is specified and all of
            ``participants`` value is not the specified type
        """

        if participants is None:
            raise ArgumentNullError('participants')

        try:
            participants = tuple(participants)
        except:
            raise ArgumentTypeError('participants', (tuple, list))

        if expected_type:
            if not all(isinstance(p, expected_type) for p in participants):
                raise ArgumentTypeError('participants[*]', expected_type)

        return participants

    @classmethod
    def from_dict(cls, instance):
        """
        Converts the specified :py:class:`dict` to an instance of :py:class:`g4s.core.model.Event`.

        :param instance: a dict which contains event information
        :type instance: dict

        :rtype:  :py:class:`g4s.core.model.Event`
        :return: an instance of :py:class:`g4s.core.model.Event`

        :raises g4s.core.arg.ArgumentNullError: if ``instance`` is :py:const:`None`
        :raises g4s.core.arg.ArgumentTypeError: if ``instance`` is not :py:const:`dict`
        """

        if instance is None:
            raise ArgumentNullError('instance')
        if not isinstance(instance, dict):
            raise ArgumentTypeError('instance', dict)

        return cls(
            id=instance['id'],
            type=instance['type'],
            title=instance['title'],
            description=instance['description'],
            start=instance['start'],
            end=instance['end'],
            is_allday=instance['is_allday'],
            participants=tuple(),
            is_public=instance['is_public'],
            last_update=instance['last_update'])


class InvalidEventDateTimePairError(Exception):
    """
    An exception which is thrown when invalid event date time pair (stat and end date time) is
    specified.
    """

    def __init__(self, start, end, is_allday):
        """
        Initializes an instance of :py:class:`InvalidEventDateTimePairError` class.

        :param start:     start date time
        :param end:       end date time
        :param is_allday: allday flag
        :type start:      :py:class:`g4s.core.date.DateTime`
        :type end:        :py:class:`g4s.core.date.DateTime`
        :type is_allday:  bool
        """

        self._start = start
        self._end = end
        self._is_allday = is_allday

    @property
    def message(self):
        msg = 'Invalid event date time pair is specified. (start: {0}, end: {1}, is_allday: {2})'
        return msg.format(self._start, self._end, self._is_allday)

    @property
    def start(self):
        """
        Gets start date time.

        :rtype:  :py:class:`g4s.core.date.DateTime`
        :return: start date time
        """

        return self._start

    @property
    def end(self):
        """
        Gets end date time.

        :rtype:  :py:class:`g4s.core.date.DateTime`
        :return: end date time
        """

        return self._end

    @property
    def is_allday(self):
        """
        Gets is-allday flag.

        :rtype:  bool
        :return: is-allday flag
        """

        return self._is_allday

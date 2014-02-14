# -*- coding: utf-8 -*-

"""
Date time handling utilities.
"""

__all__ = (
    'DateTime',
    'DateTimeParsingError',
    'TimeZone',
    'TimeZoneNotFoundError',
)

import datetime
import dateutil.parser
import dateutil.tz
from .arg import ArgumentNullError
from .arg import ArgumentTypeError


class DateTime(datetime.datetime):
    """
    Represents date and time.

    .. code-block:: python

        # gets an instance of g4s.core.date.DateTime which represents 2014-01-01T09:00:00+09:00
        DateTime.get(2014, 1, 1, 9, 0, 0, 'Asia/Tokyo')

        # gets current date time
        DateTime.get_utc_now()

    .. note::

        Please use :py:meth:`g4s.core.date.DateTime.get` method instead of
        :py:meth:`g4s.core.date.DateTime.__init__` to create an instance of this class.
    """

    def astimezone(self, tzinfo):
        if tzinfo is None:
            raise ArgumentNullError('tzinfo')
        if not isinstance(tzinfo, TimeZone):
            raise ArgumentTypeError('tzinfo', TimeZone)

        dt = super(DateTime, self).astimezone(tzinfo)
        return DateTime.get(*dt.timetuple()[:6], tzinfo=tzinfo)

    def __add__(self, delta):
        if delta is None:
            raise ArgumentNullError('delta')
        if not isinstance(delta, datetime.timedelta):
            raise ArgumentTypeError('delta', datetime.timedelta)

        r = super(DateTime, self).__add__(delta)
        return DateTime.get(r.year, r.month, r.day, r.hour, r.minute, r.second, tzinfo=r.tzinfo)

    @classmethod
    def get(cls, year, month, day, hour=0, minute=0, second=0, tzinfo=None):
        """
        Gets an instance of :py:class:`g4s.core.date.DateTime` that represents the specified
        datetime.

        :param year:   year
        :param month:  month
        :param day:    day
        :param hour:   hour
        :param minute: minute
        :param second: second
        :param tzinfo: time zone, an instance of :py:class:`g4s.core.date.TimeZone` or string
        :type year:    int
        :type month:   int
        :type dat:     int
        :type hour:    int
        :type minute:  int
        :type second:  int
        :type tzinfo:  datetime.tzinfo or str

        :rtype:  :py:class:`g4s.core.date.DateTime`
        :return:
            an instance of :py:class:`g4s.core.date.DateTime` which represents the specified
            datetime

        :raises g4s.core.arg.ArgumentNullError:
            if ``tzinfo`` is :py:const:`None`
        :raises g4s.core.arg.ArgumentTypeError:
            if ``tzinfo`` is not :py:class:`g4s.core.date.TimeZone` or :py:class:`str`
        """

        # tzinfo null check
        if tzinfo is None:
            raise ArgumentNullError('tzinfo')

        # tzinfo value check
        if isinstance(tzinfo, datetime.tzinfo):
            if not isinstance(tzinfo, TimeZone):
                raise ArgumentTypeError('tzinfo', TimeZone)
        elif isinstance(tzinfo, str):
            tzinfo = TimeZone.get(tzinfo)
        else:
            raise ArgumentTypeError('tzinfo', (TimeZone, str))

        #
        return DateTime(year, month, day, hour, minute, second, tzinfo=tzinfo)

    @classmethod
    def parse(cls, text, tzinfo):
        """
        Parses the specified text as date time.

        :param text:   text to be parsed
        :param tzinfo: time zone
        :type  text:   str
        :type  tzinfo: str or :py:class:`g4s.core.date.TimeZone`

        :rtype:  :py:class:`g4s.core.date.DateTime`
        :return: parse result

        :raises g4s.core.arg.ArgumentNullError:
            if ``text`` or ``tzinfo`` is :py:const:`None`
        :raises g4s.core.arg.ArgumentTypeError:
            if ``text`` is not string, or ``tzinfo`` is not either string of
            :py:class:`g4s.core.date.TimeZone`
        :raises g4s.core.date.TimeZoneNotFoundError:
            if the specified time zone is not found
        :raises g4s.core.date.DateTimeParsingError:
            if failed to parse the specified text
        """

        #
        if (text is None) or (not text):
            raise ArgumentNullError('text')
        if not isinstance(text, str):
            raise ArgumentTypeError('text', str)

        #
        if tzinfo is None:
            raise ArgumentNullError('tzinfo')

        if isinstance(tzinfo, TimeZone):
            pass
        elif isinstance(tzinfo, str):
            tzinfo = TimeZone.get(tzinfo)
        else:
            raise ArgumentTypeError('tzinfo', (TimeZone, str))

        #
        try:
            dt = dateutil.parser.parse(text)
        except:
            raise DateTimeParsingError(text)

        return DateTime.get(*dt.timetuple()[:6], tzinfo=tzinfo)

    @classmethod
    def get_utc_now(cls):
        """
        Gets current date time as UTC date time.

        :rtype:  :py:class:`g4s.core.date.DateTime`
        :return: current date time
        """

        now = datetime.datetime.utcnow()
        return cls.get(now.year, now.month, now.day, now.hour, now.minute, now.second, 'UTC')


class DateTimeParsingError(Exception):
    """
    An exception which is raised when failed to parse date time text.
    """

    def __init__(self, text):
        """
        Initializes an instance of :py:class:`DateTimeParsingError` class.

        :param text: text which caused parsing error
        :type  text: str
        """

        super(DateTimeParsingError, self).__init__()
        self._text = text

    @property
    def message(self):
        return 'Failed to parse the text as date time: {0}'.format(self._text)

    @property
    def text(self):
        """
        Gets the text which caused parsing error.

        :rtype:  str
        :return: text which caused parsing error
        """

        return self._text


class TimeZone(datetime.tzinfo):
    """
    Represents a time zone.

    .. code-block:: python

        # gets an instance of g4s.core.date.TimeZone which represents 'UTC'
        TimeZone.get('UTC')

        # gets an instance of g4s.core.date.TimeZone which represents 'Asia/Tokyo'
        TimeZone.get('Asia/Tokyo')

        # three-letter time zone ID (for example, 'JST') except for 'UTC' and 'GMT' causes,
        # TimeZoneNotFoundError
        TimeZone.get('JST')  # => TimeZoneNotFoundError
    """

    def __init__(self, instance, g4s_name):
        """
        Initializes an instance of :py:class:`g4s.core.date.TimeZone` class.

        :param instance: time zone instance
        :param g4s_name: name of the time zone
        :type instance:  :py:class:`datetime.tzinfo`
        :type g4s_name:  str
        """

        if instance is None:
            raise ArgumentNullError('instance')
        if g4s_name is None:
            raise ArgumentNullError('g4s_name')

        if not isinstance(instance, datetime.tzinfo):
            raise ArgumentTypeError('instance', datetime.tzinfo)
        if not isinstance(g4s_name, str):
            raise ArgumentTypeError('g4s_name', str)

        self._instance = instance
        self._g4s_name = g4s_name

    def tzname(self, dt):  # pragma: no cover
        return self._instance.tzname(dt)

    def utcoffset(self, dt):  # pragma: no cover
        return self._instance.utcoffset(dt)

    def dst(self, dt):  # pragma: no cover
        return self._instance.dst(dt)

    def __eq__(self, other):
        if (other is None) or (not isinstance(other, TimeZone)):
            return False

        return self.g4s_name == other.g4s_name

    def __ne__(self, other):
        if (other is None) or (not isinstance(other, TimeZone)):
            return True

        return self.g4s_name != other.g4s_name

    def __repr__(self):  # pragma: no cover
        return '<g4s.core.date.TimeZone "{0}" at 0x{1:x}>'.format(self.g4s_name, id(self))

    @property
    def g4s_name(self):
        """
        Gets name of the time zone.

        :rtype:  str
        :return: name of the time zone
        """

        return self._g4s_name

    @classmethod
    def get(cls, name):
        """
        Gets an instance of :py:class:`TimeZone` which represents the specified time zone.
        The name of the time zone must be like "Asia/Tokyo", instead of "JST".

        :param name: name of time zone
        :type  name: str

        :rtype:  :py:class:`g4s.core.date.TimeZone`
        :return: time zone instance

        :raises g4s.core.arg.ArgumentNullError:
            if ``name`` is :py:const:`None`
        :raises g4s.core.arg.ArgumentTypeError:
            if ``name`` is not :py:const:`str`
        :raises g4s.core.date.TimeZoneNotFoundError:
            if the specified time zone is not found
        """

        if name is None:
            raise ArgumentNullError('name')
        if not isinstance(name, str):
            raise ArgumentTypeError('name', str)
        if len(name) == 3 and (name.upper() not in ('UTC', 'GMT')):
            raise TimeZoneNotFoundError(name)

        try:
            tz = dateutil.tz.gettz(name)
            if tz is None:
                raise TimeZoneNotFoundError(name)
        except:
            raise TimeZoneNotFoundError(name)

        return TimeZone(tz, name)


class TimeZoneNotFoundError(Exception):
    """
    An exception which is thrown when the specified time zone is not found.
    """

    def __init__(self, name):
        """
        Initializes an instance of :py:class:`g4s.core.exc.TimeZoneNotFoundError` class.

        :param name: name of time zone
        :type  name: str
        """

        self._name = name

    @property
    def message(self):
        return 'The specified time zone is not found: {0}'.format(self._name)

    @property
    def name(self):
        """
        Gets name of the time zone.

        :rtype:  str
        :return: name of the time zone
        """

        return self._name

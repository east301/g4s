# -*- coding: utf-8 -*-

import contextlib
import datetime
import lxml.etree
import os
import pytest
from g4s.core.arg import ArgumentNullError
from g4s.core.arg import ArgumentTypeError
from g4s.core.date import DateTime


###
### Fixture
###

def fix_current_datetime(monkeypatch):
    class MyDateTime(datetime.datetime):
        @classmethod
        def now(cls):
            return datetime.datetime(2014, 1, 1, 9, 0, 0, 0)

        @classmethod
        def utcnow(cls):
            return datetime.datetime(2014, 1, 1, 0, 0, 0, 0)

    monkeypatch.setattr('datetime.datetime', MyDateTime)


def check_if_current_datetime_is_correctly_fixed():
    now = datetime.datetime.now()
    expected = datetime.datetime(2014, 1, 1, 9, 0, 0, 0)
    assert now == expected

    now = datetime.datetime.utcnow()
    expected = datetime.datetime(2014, 1, 1, 0, 0, 0, 0)
    assert now == expected


###
### Exception handling
###

@contextlib.contextmanager
def raises_argument_null_error(name):
    with pytest.raises(ArgumentNullError) as excinfo:
        yield

    assert excinfo.value.name == name


@contextlib.contextmanager
def raises_argument_type_error(name):
    with pytest.raises(ArgumentTypeError) as excinfo:
        yield

    assert excinfo.value.name == name


###
### Data loading
###

def create_reader_for_module(module):
    def wrapper(*args):
        return read(module, *args)

    return wrapper


def read(*args):
    my_path = os.path.dirname(__file__)

    path = os.path.join(my_path, 'data')
    for arg in args:
        path = os.path.join(path, arg)

    with open(path, 'rb') as fin:
        return fin.read()


###
### XML handling
###

def parse_xml(data):
    parser = lxml.etree.XMLParser(remove_comments=True, remove_blank_text=True)
    return lxml.etree.fromstring(data, parser)


def xml_compare(x1, x2, reporter=None):
    """
    https://bitbucket.org/ianb/formencode/src/tip/formencode/doctest_xml_compare.py#cl-70
    """

    if x1.tag != x2.tag:
        if reporter:
            reporter('Tags do not match: %s and %s' % (x1.tag, x2.tag))
        return False
    for name, value in x1.attrib.items():
        if x2.attrib.get(name) != value:
            if reporter:
                reporter('Attributes do not match: %s=%r, %s=%r'
                         % (name, value, name, x2.attrib.get(name)))
            return False
    for name in x2.attrib.keys():
        if name not in x1.attrib:
            if reporter:
                reporter('x2 has an attribute x1 is missing: %s'
                         % name)
            return False
    if not text_compare(x1.text, x2.text):
        if reporter:
            reporter('text: %r != %r' % (x1.text, x2.text))
        return False
    if not text_compare(x1.tail, x2.tail):
        if reporter:
            reporter('tail: %r != %r' % (x1.tail, x2.tail))
        return False
    cl1 = x1.getchildren()
    cl2 = x2.getchildren()
    if len(cl1) != len(cl2):
        if reporter:
            reporter('children length differs, %i != %i'
                     % (len(cl1), len(cl2)))
        return False
    i = 0
    for c1, c2 in zip(cl1, cl2):
        i += 1
        if not xml_compare(c1, c2, reporter=reporter):
            if reporter:
                reporter('children %i do not match: %s'
                         % (i, c1.tag))
            return False
    return True


def text_compare(t1, t2):
    """
    https://bitbucket.org/ianb/formencode/src/tip/formencode/doctest_xml_compare.py#cl-70
    """

    if not t1 and not t2:
        return True
    if t1 == '*' or t2 == '*':
        return True
    return (t1 or '').strip() == (t2 or '').strip()

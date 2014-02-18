# -*- coding: utf-8 -*-

import contextlib
import datetime
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

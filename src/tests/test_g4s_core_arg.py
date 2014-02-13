# -*- coding: utf-8 -*-

import pytest
from g4s.core.arg import ArgumentNullError
from g4s.core.arg import ArgumentTypeError


###
### g4s.core.arg.ArgumentNullError
###

def test__ArgumentNullError__ArgumentNullError_inherits_ValueError():
    assert issubclass(ArgumentNullError, ValueError)


def test__ArgumentNullError__message_returns_correct_value():
    error = ArgumentNullError('foo')
    assert isinstance(error.message, str)


def test__ArgumentNullError__name_returns_correct_value():
    error = ArgumentNullError('foo')
    assert error.name == 'foo'


###
### g4s.core.arg.ArgumentTypeError
###

def test__ArgumentTypeError__ArgumentTypeError_inherits_TypeError():
    assert issubclass(ArgumentTypeError, TypeError)


def test__ArgumentTypeError__message_returns_correct_value():
    error = ArgumentTypeError('foo', int)
    assert isinstance(error.message, str)


def test__ArgumentTypeError__name_returns_correct_value():
    error = ArgumentTypeError('foo', int)
    assert error.name == 'foo'


def test__ArgumentTypeError__type_returns_correct_value():
    error = ArgumentTypeError('foo', int)
    assert error.type == int

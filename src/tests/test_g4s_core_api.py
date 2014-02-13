# -*- coding: utf-8 -*-

import pytest
from g4s.core.api import CalendarApi
from g4s.core.arg import ArgumentNullError
from g4s.core.arg import ArgumentTypeError
from .util import raises_argument_null_error
from .util import raises_argument_type_error


###
### g4s.core.api.CalendarApi.__init__
###

def test__CalendarApi__init__raises_ArgumentNullError_if_None_is_passed():
    with raises_argument_null_error('params'):
        CalendarApi(None)


@pytest.mark.parametrize('obj', [1, 2.34, 'foobar'])
def test__CalendarApi__init__raises_ArgumentTypeError_if_objects_except_dict_are_passed(obj):
    with raises_argument_type_error('params'):
        CalendarApi(obj)

# pylint: disable=missing-module-docstring, missing-class-docstring
# pylint: disable=missing-function-docstring

import unittest

from kellerclub_drinks.routers.form_parser import FormParser, Param, BooleanParam


class TestFormParser(unittest.TestCase):
    def test_parser__invalid_data__raises(self) -> None:
        query = '&='

        self.assertRaises(ValueError, lambda: FormParser().parse(query))

    def test_parser__not_enough_values_for_param__raises(self) -> None:
        query = 'key=v1&key=v2'

        parser = FormParser(Param('key', 3, 3))

        self.assertRaises(ValueError, lambda: parser.parse(query))

    def test_parser__too_many_values_for_param__raises(self) -> None:
        query = 'key=v1&key=v2'

        parser = FormParser(Param('key', 1, 1))

        self.assertRaises(ValueError, lambda: parser.parse(query))

    def test_parser__no_value_for_default_param__uses_default(self) -> None:
        query = ''

        parser = FormParser(Param('key', 1, 1, default=['default']))

        self.assertEqual({'key': ['default']}, parser.parse(query))

    def test_parser__max_values_omitted__query_can_have_any_number_of_values(self) -> None:
        query = 'k=v&k=v&k=v&k=v&k=v&k=v&k=v&k=v&k=v&k=v&k=v&k=v&k=v&k=v&k=v'

        parser = FormParser(Param('k', 1, default=['default']))

        self.assertEqual(15, len(parser.parse(query)['k']))

    def test_parser__min_values_omitted__query_can_have_any_number_of_values(self) -> None:
        query = ''

        parser = FormParser(Param('k', max_values=1))

        self.assertEqual(0, len(parser.parse(query)['k']))

    def test_parser__allowed_values_is_none__does_not_check_values(self) -> None:
        query = 'key=value'

        parser = FormParser(Param('key', 1, 1))

        self.assertEqual({'key': ['value']}, parser.parse(query))

    def test_parser__has_allowed_values__values_must_be_in_allowed_values(self) -> None:
        query = 'key=first'

        parser = FormParser(Param('key', 1, 1, allowed={'second'}))

        self.assertRaises(ValueError, lambda: parser.parse(query))

    def test_boolean_parser__value_true__is_converted_to_boolean(self) -> None:
        query = 'key=true'

        parser = FormParser(BooleanParam('key'))

        self.assertEqual({'key': [True]}, parser.parse(query))

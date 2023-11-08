from unittest import TestCase

from openai_auth import use_key
from _wrap_helpers import make_api_key_argument_mandatory


class TestApplyKey(TestCase):
    def test_apply_key(self):
        @use_key("test_key")
        def test_func(*, key: str):
            return key

        self.assertEqual(test_func(), "test_key")


class TestWrapHelpers(TestCase):
    def test_make_api_key_argument_mandatory(self):
        with self.assertRaises(TypeError):

            @make_api_key_argument_mandatory
            def test_func(*, api_key=None):
                return None

            test_func()

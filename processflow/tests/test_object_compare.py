import unittest

from ..runner.object_compare import deep_copy, get_difference, subtract_valid_changes


class ClassWithAttributes:
    def __init__(self, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def __eq__(self, other):
        if isinstance(other, dict):
            for key in other:
                if not hasattr(self, key):
                    return False
                if not getattr(self, key) == other[key]:
                    return False
            return True
        return False


class TestDeepCopy(unittest.TestCase):

    def test_deep_copy_standard_types(self):
        VALUES = [
            42,
            1.618,
            "str",
            True, False,
            None,
        ]
        for v in VALUES:
            self.assertEqual(v, deep_copy(v))
            self.assertEqual(id(v), id(deep_copy(v)))

    def test_deep_copy_list_standard_types(self):
        VALUES = [
            [42],
            [7, 8, 42],
            [1.618],
            [2., 3.],
            ["str"],
            ["1", "2"],
            [False],
            [True, False],
            [None],
        ]
        for v in VALUES:
            self.assertEqual(v, deep_copy(v))
            self.assertNotEqual(id(v), id(deep_copy(v)))

    def test_deep_copy_list_standard_types2(self):
        VALUES = [
            [42, 1.618, "str", False, True, None],
        ]
        for v in VALUES:
            self.assertEqual(v, deep_copy(v))
            self.assertNotEqual(id(v), id(deep_copy(v)))

    def test_deep_copy_nested_standard_types(self):
        VALUES = [
            [42, [3, 5]],
            [1.618, [.1, .9, [33.]]],
            [[[["str"]]], "bla"],
            [False, [True], [[False]]],
            {8, 9, 10},
            {(1, 2), ("x", "y"), (True, False, (True, "False"))}
        ]
        for v in VALUES:
            self.assertEqual(v, deep_copy(v))
            self.assertNotEqual(id(v), id(deep_copy(v)))

    def test_deep_copy_dict(self):
        VALUES = [
            {42: {"bla": "blub"}, 43: 44},
            {(12, 13): (14, 15), "x": ["y", "z"]},
            {("x", "y"): {"y", "z"}, None: {"a": "b", "c": True}},
        ]
        for v in VALUES:
            self.assertEqual(v, deep_copy(v))
            self.assertNotEqual(id(v), id(deep_copy(v)))

    def test_deep_classes(self):
        VALUES = [
            ClassWithAttributes(field1=1, field2=2),
            ClassWithAttributes(a=[1, 2, 3], b=ClassWithAttributes(c="d", e=["f", "g", "h"])),
        ]
        for v in VALUES:
            self.assertEqual(v, deep_copy(v))
            self.assertNotEqual(id(v), id(deep_copy(v)))


class TestDifference(unittest.TestCase):

    def test_level1(self):
        self.assertEqual(
            {
                "a": [1, 2],
            },
            get_difference(
                {"a": 1, "b": 3},
                {"a": 2, "b": 3},
            )
        )
        self.assertEqual(
            {
                "a": [1, 2],
                "b": [3, "4"],
            },
            get_difference(
                {"a": 1, "b": 3},
                {"a": 2, "b": "4"},
            )
        )
        self.assertEqual(
            {
                "a": [[1], [2]],
                "b": [[3, 4], [3, "4"]],
            },
            get_difference(
                {"a": [1], "b": [3, 4]},
                {"a": [2], "b": [3, "4"]},
            )
        )

    def test_levelx(self):
        self.assertEqual(
            {
                "a.c": [2, 3],
            },
            get_difference(
                {"a": {"b": 1, "c": 2}},
                {"a": {"b": 1, "c": 3}},
            )
        )
        self.assertEqual(
            {
                "a.b.c.d": [1, 2],
            },
            get_difference(
                {"a": {"b": {"c": {"d": 1}}}},
                {"a": {"b": {"c": {"d": 2}}}},
            )
        )
        self.assertEqual(
            {
                "a.b.c": [{"d": 1}, None],
                "a.b.d": [None, {"d": 1}],
            },
            get_difference(
                {"a": {"b": {"c": {"d": 1}}}},
                {"a": {"b": {"d": {"d": 1}}}},
            )
        )


class TestValidChanges(unittest.TestCase):

    def _test_valid_changes(self, valid_changes, changes_made, expected):
        diff = {key: None for key in changes_made}
        expected_changes = {key: None for key in expected}
        invalid_changes = subtract_valid_changes(diff, valid_changes)
        self.assertEqual(expected_changes, invalid_changes)

    def test_level1_complete(self):
        valid_changes = []
        changes_made  = []
        self._test_valid_changes(valid_changes, changes_made, [])

        valid_changes = ["a"]
        changes_made  = ["a"]
        self._test_valid_changes(valid_changes, changes_made, [])

        valid_changes = ["a", "b", "c"]
        changes_made  = ["a", "b", "c"]
        self._test_valid_changes(valid_changes, changes_made, [])

    def test_level1_sub(self):
        valid_changes = ["a", "b", "c"]
        changes_made  = ["a"]
        self._test_valid_changes(valid_changes, changes_made, [])
        changes_made  = ["a", "b"]
        self._test_valid_changes(valid_changes, changes_made, [])

    def test_level1_wildcard(self):
        valid_changes = ["*"]
        changes_made  = ["a", "b", "c", "xyz"]
        self._test_valid_changes(valid_changes, changes_made, [])

    def test_level1_not(self):
        valid_changes = []
        changes_made  = ["a"]
        self._test_valid_changes(valid_changes, changes_made, ["a"])

        valid_changes = ["a", "b", "c"]
        changes_made  = ["a", "b", "c", "d"]
        self._test_valid_changes(valid_changes, changes_made, ["d"])

    def x_test_level2_complete(self):
        valid_changes = ["x.a", "x.b", "x.c"]
        changes_made  = ["x.a", "x.b", "x.c"]
        self._test_valid_changes(valid_changes, changes_made, [])

    def x_test_level2_sub(self):
        valid_changes = ["x.a", "x.b", "x.c"]
        changes_made  = ["x.a"]
        self._test_valid_changes(valid_changes, changes_made, [])

    def x_test_level2_wildcard(self):
        valid_changes = ["x.*"]
        changes_made  = ["x.a", "x.b", "x.c"]
        self._test_valid_changes(valid_changes, changes_made, [])

        valid_changes = ["*.a"]
        changes_made  = ["x.a", "y.a", "z.a"]
        self._test_valid_changes(valid_changes, changes_made, [])

    def x_test_level2_wildcard_not(self):
        valid_changes = ["x.*"]
        changes_made  = ["x.a", "x.b", "x.c", "y", "y.a"]
        self._test_valid_changes(valid_changes, changes_made, ["y", "y.a"])

        valid_changes = ["*.a"]
        changes_made  = ["x.a", "y.a", "z.a", "x", "x.b"]
        self._test_valid_changes(valid_changes, changes_made, ["x", "x.b"])

    def test_level3(self):
        valid_changes = ["x.y.z"]
        changes_made  = []
        self._test_valid_changes(valid_changes, changes_made, [])

        valid_changes = ["x.y.z"]
        changes_made  = ["x.y"]
        self._test_valid_changes(valid_changes, changes_made, ["x.y"])

        valid_changes = ["x.y.z"]
        changes_made  = ["x.y.z"]
        self._test_valid_changes(valid_changes, changes_made, [])

        valid_changes = ["x.y.z"]
        changes_made  = ["x.y.z.w"]
        self._test_valid_changes(valid_changes, changes_made, [])

    def test_level3_wildcard(self):
        valid_changes = ["*.y.*"]
        changes_made  = ["x.y.z"]
        self._test_valid_changes(valid_changes, changes_made, [])

        valid_changes = ["*.y.*"]
        changes_made  = ["x.y"]
        self._test_valid_changes(valid_changes, changes_made, [])

        valid_changes = ["*.y.*"]
        changes_made  = ["x"]
        self._test_valid_changes(valid_changes, changes_made, ["x"])

        valid_changes = ["*.y.*"]
        changes_made  = ["y"]
        self._test_valid_changes(valid_changes, changes_made, ["y"])

        valid_changes = ["*.*.z"]
        changes_made  = ["x.y.z", "a.z"]
        self._test_valid_changes(valid_changes, changes_made, ["a.z"])

        valid_changes = ["x.*.*"]
        changes_made  = ["x.y.z", "x.y"]
        self._test_valid_changes(valid_changes, changes_made, [])

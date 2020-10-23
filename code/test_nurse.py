from unittest import TestCase
import inspect
from nurse import Nurse


class TestNurse(TestCase):
    """ Unit tests for the Nurse class """

    def setUp(self):
        """ creates a test fixture before each test method has run """
        self.nurse = Nurse(12, "Jane", "Doe", "A", 7, 5, 0, False, False, False, True)

# TDD is going greeeaaaaaattt
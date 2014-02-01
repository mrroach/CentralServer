"""Find and run all unit tests."""

import unittest


def main():
  """Run all tests."""
  all_tests = unittest.TestLoader().discover('csrv', pattern='*_test.py')
  unittest.TextTestRunner().run(all_tests)


if __name__ == "__main__":
  main()

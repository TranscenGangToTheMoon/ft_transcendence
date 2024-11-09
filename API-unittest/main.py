import unittest

SERVICES = [
    'chat',
    # 'game',
    # 'matchmaking',
    # 'users',
    'lobby',
    'tournament',
    # 'auth',
    # 'friends',
    # 'block',
    'play',
]


def load_tests_from_directory():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    for service in SERVICES:
        module = __import__(f"tests.{service}", fromlist=[''])
        suite.addTests(loader.loadTestsFromModule(module))

    return suite


if __name__ == '__main__':
    tests = load_tests_from_directory()

    runner = unittest.TextTestRunner()
    runner.run(tests)

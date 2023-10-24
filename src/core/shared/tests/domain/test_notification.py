

from core.shared.domain.notification import Notification


class TestNotification:

    def test_add_error(self):
        notification = Notification()
        notification.add_error('Error message')
        assert notification.errors == {'Error message': 'Error message'}
        notification.add_error('Another error message')
        assert notification.errors == {'Error message': 'Error message', 'Another error message': 'Another error message'}
        notification.add_error('Error message')
        assert notification.errors == {'Error message': 'Error message', 'Another error message': 'Another error message'}

        notification = Notification()
        notification.add_error('Error message', 'field')
        assert notification.errors == {'field': ['Error message']}
        notification.add_error('Another error message', 'field')
        assert notification.errors == {'field': ['Error message', 'Another error message']}
        notification.add_error('Error message', 'field')
        assert notification.errors == {'field': ['Error message', 'Another error message']}


    def test_copy_errors(self):
        notification1 = Notification()
        notification1.add_error('Error message', 'field1')
        notification1.add_error('Another error message', 'field2')
        notification1.add_error('Yet another error message', 'field2')

        notification2 = Notification()
        notification2.copy_errors(notification1)
        assert notification2.errors == {'field1': ['Error message'], 'field2': ['Another error message', 'Yet another error message']}


    def test_set_error(self):
        notification = Notification()
        notification.set_error('Error message')
        assert notification.errors == {'Error message': 'Error message'}
        notification.set_error('Another error message')
        assert notification.errors == {'Error message': 'Error message', 'Another error message': 'Another error message'}
        notification.set_error('Error message')
        assert notification.errors == {'Error message': 'Error message', 'Another error message': 'Another error message'}

        notification = Notification()
        notification.set_error('Error message', 'field')
        assert notification.errors == {'field': ['Error message']}
        notification.set_error('Another error message', 'field')
        assert notification.errors == {'field': ['Another error message']}
        notification.set_error('Error message', 'field')
        assert notification.errors == {'field': ['Error message']}

        notification = Notification()
        notification.set_error(['Error message', 'Another error message'], 'field')
        assert notification.errors == {'field': ['Error message', 'Another error message']}
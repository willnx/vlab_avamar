# -*- coding: UTF-8 -*-
"""
A suite of tests for the avamar object
"""
import unittest
from unittest.mock import patch, MagicMock

import ujson
from flask import Flask
from vlab_api_common import flask_common
from vlab_api_common.http_auth import generate_v2_test_token


from vlab_avamar_api.lib.views import avamar


class TestAvamarView(unittest.TestCase):
    """A set of test cases for the AvamarView object"""
    @classmethod
    def setUpClass(cls):
        """Runs once for the whole test suite"""
        cls.token = generate_v2_test_token(username='bob')
        cls.ip_config = {'static-ip': '1.2.3.4',
                         'default-gateway': '1.2.3.1',
                         'netmask': '255.255.255.0',
                         'dns': ['1.2.3.2'],
                         'domain': 'vlab.local'}

    @classmethod
    def setUp(cls):
        """Runs before every test case"""
        app = Flask(__name__)
        avamar.AvamarView.register(app)
        app.config['TESTING'] = True
        cls.app = app.test_client()
        # Mock Celery
        app.celery_app = MagicMock()
        cls.fake_task = MagicMock()
        cls.fake_task.id = 'asdf-asdf-asdf'
        app.celery_app.send_task.return_value = cls.fake_task

    def test_v1_deprecated(self):
        """AvamarView - GET on /api/1/inf/avamar/server returns an HTTP 404"""
        resp = self.app.get('/api/1/inf/avamar/server',
                            headers={'X-Auth': self.token})

        status = resp.status_code
        expected = 404

        self.assertEqual(status, expected)

    def test_get_task(self):
        """AvamarView - GET on /api/2/inf/avamar/server returns a task-id"""
        resp = self.app.get('/api/2/inf/avamar/server',
                            headers={'X-Auth': self.token})

        task_id = resp.json['content']['task-id']
        expected = 'asdf-asdf-asdf'

        self.assertEqual(task_id, expected)

    def test_get_task_link(self):
        """AvamarView - GET on /api/2/inf/avamar/server sets the Link header"""
        resp = self.app.get('/api/2/inf/avamar/server',
                            headers={'X-Auth': self.token})

        task_id = resp.headers['Link']
        expected = '<https://localhost/api/2/inf/avamar/server/task/asdf-asdf-asdf>; rel=status'

        self.assertEqual(task_id, expected)

    def test_post_task(self):
        """AvamarView - POST on /api/2/inf/avamar/server returns a task-id"""
        resp = self.app.post('/api/2/inf/avamar/server',
                             headers={'X-Auth': self.token},
                             json={'network': "someLAN",
                                   'name': "myAvamarBox",
                                   'image': "someVersion",
                                   'ip-config': self.ip_config})

        task_id = resp.json['content']['task-id']
        expected = 'asdf-asdf-asdf'

        self.assertEqual(task_id, expected)

    def test_post_task_link(self):
        """AvamarView - POST on /api/2/inf/avamar/server sets the Link header"""
        resp = self.app.post('/api/2/inf/avamar/server',
                             headers={'X-Auth': self.token},
                             json={'network': "someLAN",
                                   'name': "myAvamarBox",
                                   'image': "someVersion",
                                   'ip-config': self.ip_config})

        task_id = resp.headers['Link']
        expected = '<https://localhost/api/2/inf/avamar/server/task/asdf-asdf-asdf>; rel=status'

        self.assertEqual(task_id, expected)

    def test_delete_task(self):
        """AvamarView - DELETE on /api/2/inf/avamar/server returns a task-id"""
        resp = self.app.delete('/api/2/inf/avamar/server',
                               headers={'X-Auth': self.token},
                               json={'name' : 'myAvamarBox'})

        task_id = resp.json['content']['task-id']
        expected = 'asdf-asdf-asdf'

        self.assertEqual(task_id, expected)

    def test_delete_task_link(self):
        """AvamarView - DELETE on /api/2/inf/avamar/server sets the Link header"""
        resp = self.app.delete('/api/2/inf/avamar/server',
                               headers={'X-Auth': self.token},
                               json={'name' : 'myAvamarBox'})

        task_id = resp.headers['Link']
        expected = '<https://localhost/api/2/inf/avamar/server/task/asdf-asdf-asdf>; rel=status'

        self.assertEqual(task_id, expected)

    def test_image(self):
        """AvamarView - GET on the ./image end point returns the a task-id"""
        resp = self.app.get('/api/2/inf/avamar/server/image',
                            headers={'X-Auth': self.token})

        task_id = resp.json['content']['task-id']
        expected = 'asdf-asdf-asdf'

        self.assertEqual(task_id, expected)

    def test_image(self):
        """AvamarView - GET on the ./image end point sets the Link header"""
        resp = self.app.get('/api/2/inf/avamar/server/image',
                            headers={'X-Auth': self.token})

        task_id = resp.headers['Link']
        expected = '<https://localhost/api/2/inf/avamar/server/task/asdf-asdf-asdf>; rel=status'

        self.assertEqual(task_id, expected)


if __name__ == '__main__':
    unittest.main()

import argparse

import nose.tools

from arlo import Arlo


class TestArlo:
    username = None
    password = None
    arlo = None
    devices = None

    def _get_base_station(self):
        for device in self.devices:
            if device['deviceType'] == 'basestation':
                return device

    @classmethod
    def setup_class(cls):
        with open('auth.cfg') as cfg:
            cls.username = cfg.readline().strip()
            cls.password = cfg.readline().strip()
        cls.arlo = Arlo(cls.username, cls.password)
        cls.arlo.login()

    @classmethod
    def teardown_class(cls):
        cls.arlo.logout()

    def setup(self):
        pass

    def teardown(self):
        pass

    def test_01_logout(self):
        data = self.arlo.logout()
        assert data['success']
        self.arlo.login()  # we have to login again to maintain assumed state

    def test_02_login(self):
        self.arlo.logout()  # we are already logged in
        data = self.arlo.login()
        assert data['success']

    def test_03_get_devices(self):
        data = self.arlo.get_devices()
        assert data['success']
        self.__class__.devices = data['data']

    def test_04_arm(self):
        base = self._get_base_station()
        data = self.arlo.arm(base['deviceId'], base['xCloudId'])
        assert data['success']

    def test_05_disarm(self):
        base = self._get_base_station()
        data = self.arlo.disarm(base['deviceId'], base['xCloudId'])
        assert data['success']


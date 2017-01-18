import argparse
import datetime

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

    def test_06_custom_mode(self):
        pass

    def test_07_delete_mode(self):
        pass

    def test_08_toggle_camera(self):
        pass

    def test_09_reset(self):
        pass

    def test_10_get_service_level(self):
        d = self.arlo.get_service_level()
        assert d['success']
        assert 'display' in d['data'][0]

    def test_11_get_payment_offers(self):
        d = self.arlo.get_payment_offers()
        assert d['success']
        assert 'planDescription' in d['data'][0]

    def test_12_get_profile(self):
        d = self.arlo.get_profile()
        assert d['success']
        assert 'lastName' in d['data']

    def test_13_get_friends(self):
        d = self.arlo.get_friends()
        assert d['success']

    def test_14_get_locations(self):
        d = self.arlo.get_locations()
        assert d['success']

    # we dont want to assume there are recordings in the time frame
    def test_15_get_library_metadata(self):
        today = datetime.datetime.now()
        yest = today - datetime.timedelta(days=1)
        d = self.arlo.get_library_metadata(yest.strftime('%Y%m%d'), today.strftime('%Y%m%d'))
        assert d['success']

    # we dont want to assume there are recordings in the time frame
    def test_16_get_library(self):
        today = datetime.datetime.now()
        yest = today - datetime.timedelta(days=1)
        d = self.arlo.get_library(yest.strftime('%Y%m%d'), today.strftime('%Y%m%d'))
        assert d['success']

    def test_17_update_profile(self):
        p = self.arlo.get_profile()
        d = self.arlo.update_profile('stan', 'darsh')
        assert d['success']
        d = self.arlo.get_profile()
        assert d['data']['lastName'] == 'darsh'
        assert d['data']['firstName'] == 'stan'
        self.arlo.update_profile(p['data']['firstName'], p['data']['lastName'])

    def test_18_update_password(self):
        p = self.password
        d = self.arlo.update_password('Oogabooga1')
        assert d['success']
        d = self.arlo.update_password(p)
        assert d['success']

    def test_19_update_friends(self):
        pass

    def test_20_update_device_name(self):
        dev = self.devices[1]
        name = dev['deviceName']
        d = self.arlo.update_device_name(dev['parentId'], dev['deviceId'], 'Darsh')
        assert d['success']
        d = self.arlo.update_device_name(dev['parentId'], dev['deviceId'], name)
        assert d['success']

    def test_21_update_display_order(self):
        pass

    def test_22_delete_recordings(self):
        pass

    def test_23_get_recording(self):
        pass

    def test_24_stream_recording(self):
        pass

    def test_25_get_modes(self):
        pass


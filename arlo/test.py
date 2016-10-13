import argparse
from datetime import datetime
from pprint import pprint

from arlo import Arlo


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', required=True)
    parser.add_argument('-p', '--password', required=True)
    args = parser.parse_args()

    a = Arlo(args.username, args.password)
    a.login()
    # print('-'*20)
    # print('profile\n-------')
    # print(a.get_profile())
    # print('-'*20)
    # print('friends\n-------')
    # print(a.get_friends())
    # print('-'*20)
    # print('service level\n-------------')
    # print(a.get_service_level())
    # print('-'*20)
    # print('payment offers\n--------------')
    # print(a.get_payment_offers())
    # print('-'*20)
    # print('locations\n---------')
    # print(a.get_locations())
    # print('-'*20)
    # print('devices\n-------')
    devices = a.get_devices()
    # from pprint import pprint
    # pprint(devices)
    device = devices['data'][0]
    # print(device['xCloudId'])
    # print(device['deviceId'])
    # print(device['deviceName'])

    # TODO
    #print(a.get_modes(device['deviceId'], device['xCloudId']))

    # a.arm(device['deviceId'], device['xCloudId'])
    # a.custom_mode(device['deviceId'], device['xCloudId'], 'baby')
    # a.disarm(device['deviceId'], device['xCloudId'])
    # print('-'*20)
    pprint(a.get_library('20161004', '20161007'))
    a.logout()


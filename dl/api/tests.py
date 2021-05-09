import os
from django.test import SimpleTestCase
from api.services import TransformService


class ApiTestCase(SimpleTestCase):
    def setUp(self):
        pass

    def test_dcm2mhd(self):
        data_pth = os.path.abspath(os.path.join(os.getcwd(), '..', 'data'))
        path = os.path.join(data_pth, '数据样例/0000361202')
        sv_path = os.path.join(data_pth, 'tmp/sv')
        sv_raw_path = os.path.join(data_pth, 'tmp/raw')
        success, filename = TransformService.dcm2mhd(path, sv_path,
                                                     sv_raw_path)
        self.assertEqual(True, success)

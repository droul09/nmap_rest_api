import unittest
from unittest.mock import patch, MagicMock
from app import app

class TestNmapScan(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    @patch('app.PortScanner')
    @patch('app.db.nmap_scan_results')
    def test_nmap_scan(self, mock_db, mock_scanner):

        with patch('app.check_host', return_value=True):

            mock_scan_results = MagicMock()
            mock_db.insert_one.return_value = mock_scan_results

            mock_data = {
                'scan': {
                    '1.1.1.1': {
                        'hostnames': [{'name': 'example.com'}],
                        'status': {'state': 'up'},
                        'tcp': {
                            80: {'state': 'open'},
                            443: {'state': 'closed'}
                        }
                    }
                },
                'nmap': {
                    'scanstats': {
                        'timestr': '2023-03-21 12:00:00'
                    }
                }
            }

            mock_scanner.return_value.scan.return_value = mock_data

            expected_response = {
                'hosts': [{
                    'host': 'example.com',
                    'ip': '1.1.1.1',
                    'status': 'up',
                    'protocol': 'tcp',
                    'ports': [{'80': 'open'}, {'443': 'closed'}],
                    'timestamp': '2023-03-21 12:00:00'
                }],
                'scanstats': {
                    'timestr': '2023-03-21 12:00:00'
                }
            }

            response = self.app.post('/scan', data={'host': 'scanme.nmap.org'})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, expected_response)
            mock_db.insert_one.assert_called_once_with(expected_response['hosts'][0])

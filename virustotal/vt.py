import requests
import os.path

class VirusTotal():

    def __init__(self, apikey):
        self.apikey = apikey

    def scan(self, path):
        with open(path, 'rb') as f:
            params = {'apikey': self.apikey}
            files = {'file': (os.path.basename(path), f)}
            url = 'https://www.virustotal.com/vtapi/v2/file/scan'
            res = requests.post(url, files=files, params=params)
        return res.json()['resource']

    def get_report(self, resource):
        params = {'apikey': apikey, 'resource': resource}
        url = 'https://www.virustotal.com/vtapi/v2/file/report'
        return requests.get(url, params=params).json()

    def get_num_detected(self, resource):
        report = self.get_report(resource)
        return sum(scan['detected'] for av, scan in report['scans'].items())


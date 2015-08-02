from threading import Semaphore
from os.path import basename
from rate import ratelimiter
import requests


class VirusTotal():
    """This class is used to communicate to VirusTotal through its APIs."""

    def __init__(self, apikey, limit=4, every=61):
        """Initialize the VirusTotal API limiting the reqs per timeframe."""
        self.semaphore = Semaphore(limit)
        self.apikey = apikey
        self.every = every

    def __del__(self):
        del self.limiter

    def scan(self, path):
        """Upload a file for scanning. It returns the resource ID."""
        with ratelimiter(self.semaphore, self.every):
            with open(path, 'rb') as f:
                params = {'apikey': self.apikey}
                files = {'file': (basename(path), f)}
                url = 'https://www.virustotal.com/vtapi/v2/file/scan'
                res = requests.post(url, files=files, params=params)
            return res.json()['resource']

    def get_report(self, resource):
        """Get the report for a specific resource."""
        with ratelimiter(self.semaphore, self.every):
            params = {'apikey': self.apikey, 'resource': resource}
            url = 'https://www.virustotal.com/vtapi/v2/file/report'
            return requests.get(url, params=params).json()

    def get_num_detected(self, resource):
        """Get the number of engines that reported a threat."""
        report = self.get_report(resource)
        return sum(scan['detected'] for av, scan in report['scans'].items())

    def get_percent_detected(self, resource):
        """Get the percentage of engines that reported a threat."""
        report = self.get_report(resource)
        return (sum(scan['detected'] for av, scan in report['scans'].items()) /
                float(len(report['scans'])))


import requests


class Req:
    def __init__(self, log):
        self.log = log
        self.sess = requests.Session()

    def req(self, url, method="GET", **kwargs):
        rsp = self.sess.request(url=url, method=method, **kwargs)

        if rsp.status_code > 400:
            self.log.error(f"Status Code: {rsp.status_code}, url: {rsp.url}")

        return rsp



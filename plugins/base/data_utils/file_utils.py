from requests import get
import os
from uuid import uuid4
import logging


class File:
    def __init__(self, url):
        self.url = url
        self.filename = url.split("/")[-1]
        self.path = ""

    def read(self):
        if not self.path:
            self.path = os.path.join(os.environ.get("TASKS_UPLOAD_FOLDER", "/tmp/tasks"), str(uuid4()))
            logging.info(self.path)
            logging.info(self.url)
            r = get(self.url, allow_redirects=True)
            with open(self.path, 'wb') as f:
                f.write(r.content)
                return r.content

    def seek(self, offset, whence=0):
        with open(self.path, 'rb') as f:
            return f.seek(offset, whence)

    def tell(self):
        with open(self.path, 'rb') as f:
            f.seek(0, 2)
            return f.tell()

    def remove(self):
        os.remove(self.path)

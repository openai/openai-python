from __future__ import absolute_import, division, print_function

import random
import io

import openai
import re


class MultipartDataGenerator(object):
    def __init__(self, chunk_size=1028):
        self.data = io.BytesIO()
        self.line_break = "\r\n"
        self.boundary = self._initialize_boundary()
        self.chunk_size = chunk_size

    def _remove_array_element(self, input_string):
        match = re.match(r"^(.*)\[.*\]$", input_string)
        return match[1] if match else input_string

    def add_params(self, params):
        # Flatten parameters first
        params = dict(openai.api_requestor._api_encode(params))

        for key, value in params.items():

            # strip array elements if present from key
            key = self._remove_array_element(key)

            if value is None:
                continue

            self._write(self.param_header())
            self._write(self.line_break)
            if hasattr(value, "read"):
                filename = "blob"
                if hasattr(value, "name"):
                    # Convert the filename to string, just in case it's not
                    # already one. E.g. `tempfile.TemporaryFile` has a `name`
                    # attribute but it's an `int`.
                    filename = str(value.name)

                self._write('Content-Disposition: form-data; name="')
                self._write(key)
                self._write('"; filename="')
                self._write(filename)
                self._write('"')
                self._write(self.line_break)
                self._write("Content-Type: application/octet-stream")
                self._write(self.line_break)
                self._write(self.line_break)

                self._write_file(value)
            else:
                self._write('Content-Disposition: form-data; name="')
                self._write(key)
                self._write('"')
                self._write(self.line_break)
                self._write(self.line_break)
                self._write(str(value))

            self._write(self.line_break)

    def param_header(self):
        return "--%s" % self.boundary

    def get_post_data(self):
        self._write("--%s--" % (self.boundary,))
        self._write(self.line_break)
        return self.data.getvalue()

    def _write(self, value):
        if isinstance(value, bytes):
            array = bytearray(value)
        elif isinstance(value, str):
            array = bytearray(value, encoding="utf-8")
        else:
            raise TypeError(
                "unexpected type: {value_type}".format(value_type=type(value))
            )

        self.data.write(array)

    def _write_file(self, f):
        while True:
            file_contents = f.read(self.chunk_size)
            if not file_contents:
                break
            self._write(file_contents)

    def _initialize_boundary(self):
        return random.randint(0, 2 ** 63)

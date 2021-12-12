#pylint: disable=too-many-function-args invalid-name raise-missing-from missing-function-docstring
from .middleware import replace_context_var, form_endpoint


class Rectifier:
    "task of this class is to rectify request payloads"
    def __init__(self, **payloads):
        self.exception = None
        self.endpoint = payloads.get('request').get('body').get('endpoint')
        self.request_body = payloads.get('request').get('body').get('body')
        self.request_headers = payloads.get('request').get('body').get('headers')
        self.expected_body = payloads.get('expected').get('body').get('body')
        self.expected_headers = payloads.get('expected').get('body').get('headers')


    def rectify(self):
        self.rectify_endpoint()
        self.rectify_request_body()
        self.rectify_request_headers()
        self.rectify_expected_body()
        self.rectify_expected_headers()

    def rectify_request_body(self):
        try:
            self.request_body.pop('test_id')
            self.request_body.pop('priority')
            self.request_body.pop('wait')
            self.request_body.pop('reset_env')
            self.request_body.pop('comment')
        except Exception as e:
            self.exception = e
            raise Exception('Rectifier:: Error:: ', e)
        replace_context_var(self.request_body)

    def rectify_request_headers(self):
        replace_context_var(self.request_headers)

    def rectify_expected_body(self):
        replace_context_var(self.expected_body)

    def rectify_expected_headers(self):
        replace_context_var(self.expected_headers)

    def rectify_endpoint(self):
        self.endpoint = form_endpoint(self.endpoint, self.request_body)

    def get_rectified(self):
        return {
            'endpoint': self.endpoint,
            'request': {
                'body': self.request_body,
                'headers': self.request_headers
                },
            'expected': {
                'body': self.expected_body,
                'headers': self.expected_headers
            }
        }
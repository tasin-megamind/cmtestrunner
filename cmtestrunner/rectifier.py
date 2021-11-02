# task of this class is to rectify endpoints, request body, request headers, response body, response headers
form .middleware import replace_context_var, form_endpoint


class Rectifier:
    def __init__(self, **kwargs):
        self.exception = None
        self.endpoint = kwargs.get('endpoint')
        self.request_body = kwargs.get('request_body')
        self.request_headers = kwargs.get('request_headers')
        self.expected_body = kwargs.get('expected_body')
        self.expected_headers = kwargs.get('expected_headers')


    def rectify(self):
        self.rectify_endpoint()
        self.rectify_body()
        self.rectify_headers()
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

    def rectify_response_body(self):
        replace_context_var(self.expected_body)

    def rectify_response_headers(self):
        replace_context_var(self.expected_headers)

    def rectify_endpoint(self):
        self.endpoint = form_endpoint(self.endpoint, self.request_body)

    def get_rectified(self):
        return {
            'endpoint': self.endpoint,
            'request_body': self.request_body,
            'request_headers': self.request_headers,
            'response_body': self.expected_body,
            'response_headers': self.expected_headers
        }
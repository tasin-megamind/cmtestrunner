
#pylint: disable=too-many-function-args invalid-name raise-missing-from missing-function-docstring
class Runner:
    "this is supposed to run each test and return response"
    def __init__(self, **kwargs):
        self.exception = None
        self.client = kwargs.get('client')
        self.test_method = kwargs.get('test_method')
        self.endpoint = kwargs.get('endpoint')
        self.body = kwargs.get('body')
        self.headers = kwargs.get('headers')
        self.response = None
        

    def run(self):
        try:
            self.response = self.test_method(
                                client=self.client,
                                endpoint=self.endpoint,
                                request_body=self.body,
                                headers=self.headers
                            )
        except Exception as e:
            self.exception = e
            raise Exception('Runner:: Error:: ', e)

    def get_response(self):
        return self.response
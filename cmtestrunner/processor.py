class Processor:
    def __init__(self, **kwargs):
        self.not_null_fields = [
            'client', 'test_executor', 
            'request_body', 'request_headers'
            ]
        self.do_sanity(**kwargs)
        self.test_executor = kwargs.get('test_executor')
        self.client = kwargs.get('client')
        self.request_body = kwargs.get('request_body')
        self.request_headers = kwargs.get('request_headers')
        self.response = None
        self.exception = None

    def do_sanity(self, **kwargs):
        for field in self.not_null_fields:
            if kwargs.get(field) is None:
                raise Exception(
                    'Error::Processor:: Null found in Non Empty field: ' + field + '\nSanity Failed'
                    )


    def process(self):
        try:
            self.response = self.test_executor(
                        client=self.client,
                        request_body=self.request_body,
                        headers=self.request_headers
                        )
        except Exception as e:
            self.exception = e

    def get_response(self):
        return self.response

    def get_exception(self):
        return self.exception

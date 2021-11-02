from .rectifier import Rectifier

class Environment:
    def __init__(self, behaviors):
        self.behaviors = behaviors
        self.reproduce_steps = []
        self.exception = None

    def set_behavior(self):
        try:
            for behavior in behaviors:
                self.reproduce_steps.append(behavior.__doc__)
                behavior()
        except Exception as e:
            self.exception = e
            raise Exception('Environment:: ', env.__doc__ + ':: ' + str(e))


    def set_test_props(self, props):
        self.request_body = props.get('req')
        self.request_headers = props.get('headers')
        self.expected_body = props.get('resp')
        self.expected_headers = props.get('resp_headers')
        self.metadata = {
            'priority': request_body.get('priority', '5'),
            'purpose': request_body.get('comment', ''),
            'test_id': request_body.get('test_id', ''),
            'wait': request_body.get('wait', 0),
            'reset_env': request_body.get('reset_env')
        }
        self.rectify_test_props()
        
    def rectify_test_props(self):
        rectifier = Rectifier({
            'endpoint': self.endpoint,
            'request_body': self.request_body,
            'request_headers': self.request_headers,
            'expected_body': self.expected_body,
            'expected_headers': self.expected_headers
        })


    def set_test_vars(self, test_data):
        # TestRunner.total_test_cases += 1
        self.response = None
        reset_auth_header(TestRunner.client)
        self.request_body = test_data.get('req')
        if self.request_body.get('user_type'):
            user_type = self.request_body.pop('user_type')
            if user_type == 'user':
                self.set_user_auth()
            elif user_type == 'admin':
                self.set_superuser_auth()
            elif user_type == 'invalid':
                set_auth_header(TestRunner.client, 'XXXinvalid_tokenXXX')
     
        self.reset_env = self.request_body.get('reset_env')
        

        self.wait = self.request_body.get('wait', 0)
        self.exp_response = test_data.get('resp')
        self.priority = self.request_body.pop('priority')
        self.test_id = self.request_body.pop('test_id')
        self.test_purpose = self.request_body.pop('comment')
        self.error_info = '\nTest ID: ' + str(
            self.test_id) + ' =====>>>>> ' + self.test_data_set + \
            ' failed for language: %s.\n' % self.accept_lang
        self.custom_headers = test_data.get('headers')
        self.endpoint = form_endpoint(self.endpoint, self.request_body)
        setattr(TestRunner.ENDPOINTS, self.endpoint_alias, self.endpoint)


    def set_test_attributes(self, **kwargs):
        # TestRunner.client = self.get_client()
        self.test_method = kwargs.get('test_method')
        self.environment = kwargs.get('env', [])
        self.set_environment(self.environment)
        self.test_data_set = kwargs.get('test_data_set')
        self.test_data = request_response_formatter('tests/' + self.test_data_set)
        self.endpoint_alias = kwargs.get('test_method').__name__.upper() + '_URL'
        self.endpoint = getattr(
            TestRunner.ENDPOINTS, 
            self.endpoint_alias
            )
        TestRunner.test_pool[self.test_data_set] = self.test_data
        


    def set_environment(self, envs):
        settings.TEST_SERVER = getattr(settings, self.package.upper() + '_BASE_URL')
        self.set_endpoints()
        TestRunner.client = self.get_client()   # need to find out why this is here again
        if settings.TEST_SERVER == 'http://testserver':
            TestRunner.reset_db = reset_db
        if TestRunner.query_executor:
            TestRunner.reset_db(TestRunner.query_executor)
        translation.activate('en')
        self.reproduce_steps = []
        try:
            for env in envs:
                self.reproduce_steps.append(env.__doc__)
                args = inspect.getargspec(env).args
                if args and args[0] == 'client':
                    env(TestRunner.client)
                else:
                    env()
        except Exception as e:
            Constants.EXCEPTIONS.append({
                'test_method': self.test_method.__name__,
                'details': e
            })
            raise Exception(env.__doc__ + ':: ' + str(e))
from .middleware import request_response_formatter

class Orchestrator:
    def __init__(self, execution_parameters):
        self.test_method = execution_parameters.get('test_methods')
        self.environment = execution_parameters.get('env')
        self.test_data_feeder = execution_parameters.get('test_data_set')
        self.test_data = request_response_formatter('tests/' + self.test_data_feeder)

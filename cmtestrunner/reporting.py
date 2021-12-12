from .middleware import generate_test_report, generate_analytics
from django.template.loader import render_to_string


class Reporting:
    def __init__(self, **kwargs):
        self.kwargs = kwargs



        generate_test_report(
                    test_name=kwargs.get('test_data_set'), 
                    priority=kwargs.get('priority'), 
                    test_id=kwargs.get('test_id'), 
                    purpose=kwargs.get('test_purpose'), 
                    reproduce_steps=kwargs.get('reproduce_steps'),
                    request_body=kwargs.get('request_body'), 
                    response=kwargs.get('response'), 
                    request_header=kwargs.get('request_headers'),
                    expected_response=kwargs.get('exp_response'),
                    error_info=kwargs.get('error_info'),
                    response_time=kwargs.get('response_time'),
                    status_code=kwargs.get('response_status_code'),
                    endpoint=kwargs.get('endpoint')
                    )
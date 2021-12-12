#pylint: disable=too-many-function-args invalid-name raise-missing-from missing-function-docstring
from .rectifier import Rectifier
import time

class Environment:
    def __init__(self, behaviors):
        self.behaviors = behaviors
        self.reproduce_steps = []
        self.exception = None
        self.payloads = None
        self.metadata = None

    def set_behavior(self):
        for behavior in self.behaviors:
            try:
                self.reproduce_steps.append(behavior.__doc__)
                behavior()
            except Exception as e:
                self.exception = e
                raise Exception('Environment:: ', behavior.__doc__ + ':: ' + str(e))


    def set_test_props(self, props):
        self.payloads = {
            'endpoint': props.get('endpoint'),
            'request': {
                'body': props.get('req'),
                'headers': props.get('headers')
                },
            'expected': {
                'body': props.get('resp'),
                'headers': props.get('resp_headers')
            }
        }
        self.metadata = {
            'priority': self.payloads.get('request').get('body').get('priority', '5'),
            'purpose': self.payloads.get('request').get('body').get('comment', 'This test has no purpose'),
            'test_id': self.payloads.get('request').get('body').get('test_id', ''),
            'wait': self.payloads.get('request').get('body').get('wait', 0),
            'reset_env': self.payloads.get('request').get('body').get('reset_env')
        }
        self.begin_meta_execution()
        return self.rectify_test_props()
        
    def rectify_test_props(self):
        rectifier = Rectifier(self.payloads)
        return rectifier.get_rectified()

    def begin_meta_execution(self):
        time.sleep(float(self.metadata.get('wait'))/1000)
        if (self.metadata.get('reset_env')):
            self.set_behavior()


    def get_test_metadata(self):
        return self.metadata
        
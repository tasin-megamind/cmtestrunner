from.object_manager import ObjectManager

class VerifyEngine:
    def __init__(self, actual_response, expected_response):
        self.actual_response = actual_response
        self.expected_response = expected_response
        self.verified_actual_response = None
        self.verified_expected_response = None
        self.is_matched = False
        self.mismatched_keys = None

    def verify(self):
        manager = ObjectManager(self.actual_response, self.expected_response)
        manager.match_obj()
        self.verified_actual_response, self.verified_expected_response = manager.get_converted()
        self.is_matched = manager.is_matched()

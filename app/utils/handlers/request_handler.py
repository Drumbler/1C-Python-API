class RequestHandler:
    def __init__(self, list_request_mapping: dict, list_request_options_mapping: dict):
        self.list_for_request = []
        self.list_for_request_options = []
        self.received_data = {}
        self.received_data_options = {}
        self.list_request_mapping = list_request_mapping
        self.list_request_options_mapping = list_request_options_mapping
        
    def handle_request(self, key):
        if key in self.list_request_mapping:
            self.list_for_request.append(self.list_request_mapping[key])
            return self.list_request_mapping[key]
        elif key in self.list_request_options_mapping:
            self.list_for_request_options.append(self.list_request_options_mapping[key])
            return self.list_request_options_mapping[key]
        return key
    
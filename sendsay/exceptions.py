class SendsayAPIError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "%s: %s" % (self.value[0].get('id', ''), self.value[0].get('explain', ''))


class VerificationException(Exception):

    def __init__(self, error_msg="Verification Error Exception"):
        self.error_msg = error_msg
        super().__init__(self.error_msg)

    def __str__(self):
        return self.error_msg
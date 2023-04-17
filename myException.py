class GetFullURLFail(Exception):

    def __init__(self,short_URL="UNKNOWN",message=""):
        self.short_URL = short_URL
        self.message = f'Get Full URL for {self.short_URL} failed. Maybe the shorten URL is not correct.'
        super().__init__(self.message)

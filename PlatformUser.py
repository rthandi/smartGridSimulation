class PlatformUser:
    def __init__(self, name, bill, context, public_key):
        self.name = name
        self.bill = bill
        self.context = context
        self.public_key = public_key

    def __str__(self):
        return "PlatformUser: " + self.name + " bill: " + str(self.bill)

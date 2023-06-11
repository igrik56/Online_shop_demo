from forex_python.converter import CurrencyRates

class Convert():

    def __init__(self):
        self.c = CurrencyRates()
    
    @classmethod
    def check(cls, location):
        
        conv_to = 'USD'

        if location == 'Mexico':
            conv_to = 'MXN'
        if location == 'Canada':
            conv_to = 'CAD'

        conv_to = conv_to.upper()

        rate = CurrencyRates().convert('USD', conv_to, 1)
        rate = round(rate, 2)

        currency = {'label': conv_to,
                    'rate' : rate
                }
        return currency
    
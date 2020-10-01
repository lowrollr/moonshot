
import random

class Indicator:
    def __init__(self, _params, _appended_name='', _name=''):
        # each element i
        self.params = _params
        if _name:
            self.name = _name
        else:
            self.name = self.__class__.__name__ + _appended_name
        self.best_values = {}

    def genData(self, dataset, gen_new_values=True, value='close'):
        # generic indicators don't get added to the dataset as columns because they are simply
        # data used within strategies and thus don't need to be applied to data frames
        if gen_new_values:
            for x in self.params:
                x.genValue()
    
    def shrinkParamRanges(self, percentage):
        if self.best_values:
            for x in self.params:
                x.shrinkRange(self.best_values[x.name], percentage)

    def storeBestValues(self):
        self.best_values = {}
        for x in self.params:
            self.best_values[x.name] = x.value
        return self.best_values
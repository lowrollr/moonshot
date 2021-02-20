
import pickle
import os
import importlib
import inspect
from indicators.indicator import Indicator

class computeEngine:
    def __init__(self, coins):
        self.coins = coins
        mod_obj = importModel
        self.features = mod_obj['features']
        self.probability_threshold = mod_obj['proba_threshold']
        self.indicator_dict = mod_obj['indicators']
        self.indicators = []
        self.model = mod_obj['model']

    def createIndicators(self):
        temp_indicators = []
        for ind in self.indicator_dict:
            indicatorClass = importIndicator(self.indicator_dict[ind]['type'])
            temp_indicators.append(indicatorClass(
                params=self.indicator_dict[ind]['params'],
                name=ind,
                scalingWindowSize=15000,
                value=self.indicator_dict[ind]['value']))

        # order indicators so that indicators that depend on other indicators are comptued last
        base_values = {'open', 'high', 'low', 'close', 'volume', 'trades'}
        names_so_far = set()
        while len(temp_indicators) > len(self.indicators):
            found_any = False
            for ind in temp_indicators:
                if ind not in self.indicators:
                    if ind.value in base_values or ind.value in names_so_far:
                        names_so_far.add(ind.name)
                        self.indicators.append(ind)
                        found_any = True
            if not found_any:
                print('Error importing indicators!')

def importModel(mod_name, version="latest"):
    #get the correct model
    base_dir = f'saved_models/{mod_name}/'
    version_str = version
    if version == "latest":
        # all_files = os.listdir(base_dir)
        highest_version = [0, 0]

        for f in [x for x in os.scandir(f'{base_dir}/')if x.is_dir()]:
            parts = f.name.split('_')
            version_str = int(parts[0])
            subversion = int(parts[1])
            if version_str == highest_version[0]:
                if subversion > highest_version[1]:
                    highest_version = [version_str, subversion]
            elif version_str > highest_version[0]:
                highest_version = [version_str, subversion]
            
    # set version to be the highest version found
    version_str = f'{highest_version[0]}_{highest_version[1]}'

    full_path = base_dir + version_str + '/' + mod_name + '_' + version_str + '.sav'
    mod_obj = pickle.load(open(full_path, 'rb'))

    return mod_obj

def importIndicator(name):
    module = importlib.import_module(f'indicators.{name}')
    for mod in dir(module):
        obj = getattr(module, mod)
        if inspect.isclass(obj) and issubclass(obj, Indicator) and obj != Indicator:
            return obj

    return None
    
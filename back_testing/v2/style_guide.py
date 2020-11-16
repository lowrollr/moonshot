'''
FILE: <filename>
AUTHORS:
    -> <author1> <email1>
    -> <author2> <email2>
WHAT:
    -> point 1 about what the file does/implements
    -> point 2 about what the file does/implements
'''

'''
CLASS: <name_of_class>
WHAT:
    -> point 1 about what the class is/does
    -> point 2 about what the class is/does
--optional--
TODO:
    -> thing 1 that needs done
    -> thing 2 that needs done
'''
class StyleGuide:
    
    '''
    ARGS:
        -> arg_name1 (arg_type1): description of what arg1 is 
        -> arg_name2 (arg_type2): description of what arg2 is 
    RETURN:
        -> return_name (return_type): description of what is returned
    WHAT: 
        -> point 1 about what the function does/implements
        -> point 2 about what the function does/implements
    --optional--
    TODO:
        -> thing 1 that needs done
        -> thing 2 that needs done
    '''
    def myFn(self, arg_name1, arg_name2):
        # This is a helpful inline comment to help the reader understand what is going on
        # There is no set style for these, but make them helpful and use proper English

        # This is a helpful message explaining why a large chunk of commented out code is still present in our codebase :)
        '''
        if self.test_param_ranges:
            params = x.get_param_ranges()
            param_values = []
            for p in params.keys():
                low = params[p][0]
                high = params[p][1]
                step = params[p][2]
                cur = low
                vals = []
                while cur < high:
                    vals.append((cur, p))
                    cur += step
                if vals[-1] != high:
                    vals.append((high, p))
                param_values += [vals]
            param_product = list(product(*param_values))
            max_return = 0.0
            max_attrs = ''
            for p in param_product:
                for p2 in p:
                    setattr(x, p2[1], p2[0])
                name = str(p2)
                new_return = self.executeStrategy(x, d, name)
                if new_return > max_return:
                    max_return = new_return
                    max_attrs = str(p2)
            print('max params: ' + max_attrs)
        '''
        return_name = 'yep'
        return return_name
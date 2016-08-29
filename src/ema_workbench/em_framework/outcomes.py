'''
Module for outcome classes

'''
from __future__ import (absolute_import, print_function, division,
                        unicode_literals)
import abc
import six
import warnings

import pandas

from .util import NamedObject


# Created on 24 mei 2011
# 
# .. codeauthor:: jhkwakkel <j.h.kwakkel (at) tudelft (dot) nl>

__all__ = ['Outcome', 'ScalarOutcome', 'TimeSeriesOutcome']


# TODO:: have two names for an outcome, one is the name as it is known
# to the user, the other is the name of the variable in the model
# the return value for the variable can be passed to a callable known
# to the outcome. This makes is possible to have e.g. a peak infection, which
# takes a time series on the infection, and finds the maximum over the time
# series

# TODO:: we need a output map, this map calls the outcomes to do
# any transformation as outlined above

def Outcome(name, time=False):
    if time:
        warnings.warn('Deprecated, use TimeSeriesOutcome instead')
        return ScalarOutcome(name)
    else:
        warnings.warn('Deprecated, use ScalarOutcome instead')
        return TimeSeriesOutcome(name)
    

class AbstractOutcome(NamedObject):
    '''
    Base Outcome class
    
    Parameters
    ----------
    name : str
           Name of the outcome.
    kind : {INFO, MINIMZE, MAXIMIZE}, optional
    variable_name : str, optional
                    if the name of the outcome in the underlying model
                    is different from the name of the outcome, you can 
                    supply the variable name as an optional argument,
                    if not provided, defaults to name
    function : callable, optional
               a callable to perform postprocessing on data retrieved from
               model
    
    Attributes
    ----------
    name : str
    kind : int
    
    '''
    __metaclass__ = abc.ABCMeta

    MINIMIZE = -1
    MAXIMIZE = 1
    INFO = 0
    
    #TODO:: variable_name should be expanded so that it can also accept a list
    # of variable names, this is only meaningful in case there is also
    # a function, in which case the function gets called with the
    # results for each of the variables in the collection passed to 
    # variable name. 
    # this requires updating the run model in all the model interface
    # classes. To help with this, it might be a good idea to add
    # a outcome_variables attribute, perhaps
    # best solution seems to be to change from setting all
    # outputs in one go to handling to processing in the set_value
    # of the outcomes dict, so changing the descriptor to an outcome
    # specific descriptor
    #
    # other option is to make values into kwargs, so zip
    # values with variable_names and use this in calling function
    # then all that is needed is that the run_model functions
    # simply create a list with the outcomes for each variable name
    #
    
    
    @property
    def variable_name(self):
        if self._variable_name != None:
            return self._variable_name
        else:
            return self.name
        
    @variable_name.setter
    def variable_name(self, name):
        self._variable_name = name
    
    def __init__(self, name, kind=INFO, variable_name=None, function=None):
        super(AbstractOutcome, self).__init__(name)
        
        if function is not None and not callable(function):
            raise ValueError('function must be a callable')
        if variable_name:
            if (not isinstance(variable_name, basestring)) and (not all(isinstance(elem, basestring) for elem in variable_name)):
                    raise ValueError('variable name must be a string or list of strings')
        
        
        self.kind = kind
        self.variable_name = variable_name
        self.function = function
    
    def process(self, values):
        try:
            if isinstance(self.variable_name, basestring):
                return self.function(values)
            else:
                var_names = self.variable_name
                
                len_var = len(var_names)
                try:
                    len_val = len(values)
                except TypeError:
                    len_val = None
                
                if len_var != len_val:
                    raise ValueError(('number of variables is {}, '
                          'number of outputs is {}').format(len_var, len_val))
                
                try:
                    kwargs = {var_names[i]:values[i] for i in range(len(var_names))}
                except TypeError as e:
                    print(e)
                    raise
                return self.function(**kwargs)
        except TypeError:
            return values
    
    def __eq__ (self, other):
        comparison = [all(hasattr(self, key) == hasattr(other, key) and
                          getattr(self, key) == getattr(other, key) for key 
                          in self.__dict__.keys())]
        comparison.append(self.__class__ == other.__class__)
        return all(comparison)


class ScalarOutcome(AbstractOutcome):
    '''
    Scalar Outcome class
    
    Parameters
    ----------
    name : str
           Name of the outcome.
    kind : {INFO, MINIMZE, MAXIMIZE}, optional
    
    Attributes
    ----------
    name : str
    kind : int
    
    '''   
    
    def __init__(self, name, kind=AbstractOutcome.INFO, variable_name=None, 
                 function=None):
        super(ScalarOutcome, self).__init__(name, kind, 
                                            variable_name=variable_name,
                                            function=function)


class TimeSeriesOutcome(AbstractOutcome):
    '''
    TimeSeries Outcome class
    
    Parameters
    ----------
    name : str
           Name of the outcome.
    kind : {INFO, MINIMZE, MAXIMIZE}, optional
    reduce : callable, optional
             a callable which returns a scalar when called. Is only used
             when the outcome is used in an optimization context
    
    Raises
    ------
    ValueError
        if kind is MINIMIZE or MAXIMIZE and callable is not provided or
        not a callable
    
    Attributes
    ----------
    name : str
    kind : int
    reduce : callable
    
    '''   
    
    def __init__(self, name, kind=AbstractOutcome.INFO, variable_name=None, 
                 function=None):
        super(TimeSeriesOutcome, self).__init__(name, kind, variable_name=variable_name, 
                                                function=function)
        
        if (not self.kind==AbstractOutcome.INFO) and (not callable(reduce)):
            raise ValueError(('reduce needs to be specified when using'
                              ' TimeSeriesOutcome in optimization' ))

def create_outcomes(outcomes, **kwargs):
    '''Helper function for creating multiple outcomes
    
    Parameters
    ----------
    outcomes : Dataframe, or something convertable to a dataframe
               in case of string, the string will be paased
    
    Returns
    -------
    list
    
    '''

    if isinstance(outcomes, six.string_types):
        outcomes = pandas.read_csv(outcomes, **kwargs)
    elif not isinstance(outcomes, pandas.DataFrame):
        outcomes = pandas.DataFrame.from_dict(outcomes)
        
    for entry in ['name', 'type']:
        if entry not in outcomes.columns:
            raise ValueError('no {} column in dataframe'.format(entry))
    
    temp_outcomes = []
    for _, row in outcomes.iterrows():
        name = row['name']
        kind = row['type']
        
        if kind=='scalar':
            outcome = ScalarOutcome(name)
        elif kind=='timeseries':
            outcome = TimeSeriesOutcome(name)
        else:
            raise ValueError('unknown type for '+name)
        temp_outcomes.append(outcome)
    return temp_outcomes
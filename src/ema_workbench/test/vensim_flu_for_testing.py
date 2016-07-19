'''
Created on 20 May, 2011

This module shows how you can use vensim models directly
instead of coding the model in Python. The underlying case
is the same as used in fluExample

.. codeauthor:: jhkwakkel <j.h.kwakkel (at) tudelft (dot) nl>
                epruyt <e.pruyt (at) tudelft (dot) nl>
'''
from __future__ import absolute_import
from ..em_framework import RealParameter, TimeSeriesOutcome
from ..connectors.vensim import VensimModelStructureInterface 

class FluModel(VensimModelStructureInterface):
    #base case model
    model_file = r'\FLUvensimV1basecase.vpm'
        
    #outcomes
    outcomes = [TimeSeriesOutcome('deceased population region 1'),
                TimeSeriesOutcome('infected fraction R1')]
 
    #Plain Parametric Uncertainties 
    uncertainties = [
        RealParameter("additional seasonal immune population fraction R1", 
                        0, 0.5),
        RealParameter("additional seasonal immune population fraction R2",
                        0, 0.5),
        RealParameter("fatality ratio region 1", 0.0001, 0.1),
        RealParameter("fatality rate region 2", 0.0001, 0.1),
        RealParameter("initial immune fraction of the population of region 1",
                        0, 0.5),
        RealParameter("initial immune fraction of the population of region 2",
                        0, 0.5),
        RealParameter("normal interregional contact rate", 0, 0.9),
        RealParameter("permanent immune population fraction R1", 0, 0.5),
        RealParameter("permanent immune population fraction R2", 0, 0.5),
        RealParameter("recovery time region 1", 0.1, 0.75),
        RealParameter("recovery time region 2", 0.1, 0.75),
        RealParameter("susceptible to immune population delay time region 1", 
                        0.5,2),
        RealParameter("susceptible to immune population delay time region 2",
                        0.5,2),
        RealParameter("root contact rate region 1", 0.01, 5),
        RealParameter("root contact ratio region 2", 0.01, 5),
        RealParameter("infection ratio region 1", 0, 0.15),
        RealParameter("infection rate region 2", 0, 0.15),
        RealParameter("normal contact rate region 1", 10, 100),
        RealParameter("normal contact rate region 2", 10, 200)]
                         

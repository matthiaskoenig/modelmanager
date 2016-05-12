"""
Testing the database interaction tools.
"""

from __future__ import print_function, division
import unittest
from django.test import TestCase
import django

import simapp.db.api as db_api
from tools import *
from ..dist.samples import Sample
from multiscale.examples.testdata import demo_sbml
django.setup()


class ToolsTestCase(TestCase):
    def setUp(self):
        model = db_api.create_model(demo_sbml, model_format=db_api.CompModelFormat.SBML)
        settings = db_api.create_settings({db_api.SettingKey.ABS_TOL: 1E-8})
        method = db_api.create_method(method_type=db_api.MethodType.ODE, settings=settings)
        self.task = db_api.create_task(model=model, method=method)
        parameters = [
            db_api.create_parameter(key='L', value=1E-6, unit="m",
                                    parameter_type=db_api.ParameterType.GLOBAL_PARAMETER),
            db_api.create_parameter(key='N', value=20, unit="-",
                                    parameter_type=db_api.ParameterType.GLOBAL_PARAMETER)
            ]
        self.sample = Sample.from_parameters(parameters)
        self.sim = db_api.create_simulation(self.task, parameters=parameters)

    def tearDown(self):
        self.sim = None
        self.task = None

    def test_get_samples_from_task(self):
        samples = get_samples_from_task(self.task)
        self.assertEqual(len(samples), 1)

    def test_get_sample_from_simulation(self):
        sample = get_sample_from_simulation(self.sim)
        # Sample has two parameters
        self.assertEqual(len(sample), 2)

    def test_create_simulations_from_samples(self):
        simulations = create_simulations_from_samples(self.task, samples=[self.sample])
        self.assertEqual(len(simulations), 1)


if __name__ == '__main__':
    unittest.main()

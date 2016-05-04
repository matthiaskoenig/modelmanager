"""
Testing the simapp database api.
"""

from __future__ import print_function
from simapp.db.api import *
from django.test import TestCase
from multiscale.examples.testdata import demo_sbml_no_annotations, demo_id

import django
django.setup()


class ApiTestCase(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_model(self):
        m1 = create_model(demo_sbml_no_annotations, model_format=CompModelFormat.SBML)
        self.assertEqual(m1.model_id, demo_id)
        self.assertEqual(m1.sbml_id, demo_id)
        self.assertTrue(m1.is_sbml())
        self.assertFalse(m1.is_cellml())
        self.assertEqual(m1.model_format, CompModelFormat.SBML)

    def test_create_parameter(self):
        p1 = create_parameter(key='L', value=1E-6, unit="m",
                              parameter_type=ParameterType.GLOBAL_PARAMETER)
        p2 = create_parameter(key='N', value=20, unit="-",
                              parameter_type=ParameterType.BOUNDARY_INIT)
        self.assertEqual(p1.key, 'L')
        self.assertEqual(p2.key, 'N')
        self.assertEqual(p1.value, 1E-6)
        self.assertEqual(p2.value, 20)
        self.assertEqual(p1.unit, 'm')
        self.assertEqual(p2.unit, '-')
        self.assertEqual(p1.parameter_type, ParameterType.GLOBAL_PARAMETER)
        self.assertEqual(p2.parameter_type, ParameterType.BOUNDARY_INIT)

    def test_create_task(self):
        p1 = create_parameter(key='L', value=1E-6, unit="m",
                              parameter_type=ParameterType.GLOBAL_PARAMETER)
        p2 = create_parameter(key='N', value=20, unit="-",
                              parameter_type=ParameterType.BOUNDARY_INIT)
        settings = create_settings({})
        method = create_method(method_type=MethodType.ODE, settings=settings)
        model = create_model(filepath=demo_sbml_no_annotations, model_format=CompModelFormat.SBML)
        task = create_task(model, method=method)
        self.assertIsNotNone(task)
        self.assertEqual(method.method_type, task.method.method_type)

    def test_create_settings(self):
        settings_dict = {SettingKey.VAR_STEPS: False,
                         SettingKey.T_START: 0.0,
                         SettingKey.T_END: 20.0,
                         SettingKey.STEPS: 100}

        settings = create_settings(settings_dict, add_defaults=False)
        self.assertEqual(len(settings), 4)

    def test_create_method(self):
        settings_dict = {SettingKey.VAR_STEPS: False,
                         SettingKey.T_START: 0.0,
                         SettingKey.T_END: 20.0,
                         SettingKey.STEPS: 100}

        settings = create_settings(settings_dict, add_defaults=False)
        method = create_method(method_type=MethodType.ODE, settings=settings)
        self.assertIsNotNone(method)

    def test_create_method_defaults(self):
        settings_dict = {SettingKey.VAR_STEPS: False,
                         SettingKey.T_START: 0.0,
                         SettingKey.T_END: 20.0,
                         SettingKey.STEPS: 100}
        settings = create_settings(settings_dict)
        method = create_method(method_type=MethodType.ODE, settings=settings)
        self.assertIsNotNone(method)

    def test_create_simulation(self):
        p1 = create_parameter(key='L', value=1E-6, unit="m",
                              parameter_type=ParameterType.GLOBAL_PARAMETER)
        p2 = create_parameter(key='N', value=20, unit="-",
                              parameter_type=ParameterType.BOUNDARY_INIT)
        settings = create_settings({})
        method = create_method(method_type=MethodType.ODE, settings=settings)
        model = create_model(filepath=demo_sbml_no_annotations, model_format=CompModelFormat.SBML)
        task = create_task(model, method=method)
        simulation = create_simulation(task, parameters=[p1, p2])
        self.assertIsNotNone(simulation)
        self.assertEqual(task.pk, simulation.task.pk)


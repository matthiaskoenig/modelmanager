"""
Tests for simapp.
# TODO: test the links on the pages, do all external links work

@author: Matthias Koenig
@date: 2015-05-10
"""

from __future__ import print_function
import os
from django.test import TestCase
import django
django.setup()

from multiscale.examples.testdata import demo_sbml_no_annotations, demo_id

# ===============================================================================
# CoreTest
# ===============================================================================
from simapp.models import Core


class CoreTestCase(TestCase):
    def setUp(self):
        Core.objects.create(ip='127.0.0.1', cpu=1)
        Core.objects.create(ip='1.2.3.4', cpu=2)

    def test_cores_are_active(self):
        """ Test if cores are active. """
        c1 = Core.objects.get(ip='127.0.0.1', cpu=1)
        c2 = Core.objects.get(ip='1.2.3.4', cpu=2)
        self.assertEqual(c1.active, True)
        self.assertEqual(c2.active, True)

    def test_cores_computer(self):
        """ Check if computers are in the COMPUTER dictionary. """
        c1 = Core.objects.get(ip='127.0.0.1', cpu=1)
        c2 = Core.objects.get(ip='1.2.3.4', cpu=2)
        self.assertEqual(c1.computer, 'localhost')
        self.assertEqual(c2.computer, c2.ip)


# ===============================================================================
# CompModelTest
# ===============================================================================
from simapp.models import CompModel, CompModelFormat


class CompModelFormatTestCase(TestCase):
    def test_equality(self):
        """ Create the demo network in the database. """
        self.assertEqual(CompModelFormat.SBML, CompModelFormat.SBML)


class CompModelTestCase(TestCase):
    def setUp(self):
        CompModel.create(demo_sbml_no_annotations, model_format=CompModelFormat.SBML)

    def test_model_from_filepath(self):
        """ Create the demo network in the database. """
        m1 = CompModel.objects.get(model_id=demo_id)
        self.assertEqual(m1.model_id, demo_id)
        self.assertEqual(m1.sbml_id, demo_id)

    def test_model_format(self):
        """ Make the format checks. """
        m1 = CompModel.objects.get(model_id=demo_id)
        self.assertTrue(m1.is_sbml())
        self.assertFalse(m1.is_cellml())
        self.assertEqual(m1.model_format, CompModelFormat.SBML)

# ===============================================================================
# SettingTest
# ===============================================================================
from simapp.models import DataType, Setting, SettingKey, SimulatorType


class SettingTestCase(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_setting_fields(self):
        """ Test the setting fields. """
        Setting.objects.get_or_create(key=SettingKey.INTEGRATOR, value=SimulatorType.ROADRUNNER)
        s1 = Setting.objects.get(key=SettingKey.INTEGRATOR, value=SimulatorType.ROADRUNNER)
        self.assertEqual(s1.datatype, DataType.STR)

    def test_create_default_settings(self):
        settings = Setting.get_or_create_defaults()
        keys = [s.key for s in settings]
        self.assertTrue(SettingKey.INTEGRATOR in keys)
        self.assertTrue(SettingKey.VAR_STEPS in keys)
        self.assertTrue(SettingKey.ABS_TOL in keys)
        self.assertTrue(SettingKey.REL_TOL in keys)
        self.assertTrue(SettingKey.STIFF in keys)

    def test_datatype_cast(self):
        self.assertIsInstance(DataType.cast_value(1, DataType.STR), str)
        self.assertIsInstance(DataType.cast_value(1, DataType.BOOL), bool)
        self.assertIsInstance(DataType.cast_value(1, DataType.INT), int)
        self.assertIsInstance(DataType.cast_value(1, DataType.FLOAT), float)

    def test_casts(self):
        settings = Setting.get_or_create_defaults()
        for s in settings:
            if s.key == SettingKey.INTEGRATOR:
                self.assertTrue(isinstance(s.cast_value, str))
            if s.key == SettingKey.ABS_TOL:
                self.assertTrue(isinstance(s.cast_value, float))
        self.assertEqual(len(Setting.DEFAULTS), len(settings))

    def test_combine_dicts(self):
        d1 = {'a': 1, 'b': 2, 'c': 3}
        d2 = {'a': 'test', 'e': 10, 'f': 15}
        d = Setting._combine_dicts(d1, d2)
        self.assertEqual(len(d), 5)
        self.assertEqual(d['a'], 'test')
        self.assertEqual(d['e'], 10)

# ===============================================================================
# MethodTest
# ===============================================================================
from simapp.models import Method, MethodType


class MethodTestCase(TestCase):
    def setUp(self):
        settings = Setting.get_or_create_defaults()
        self.m1 = Method.get_or_create(method_type=MethodType.ODE, settings=settings)

    def test_identity(self):
        """ Test the setting fields. """
        settings = Setting.get_or_create_defaults()
        m2 = Method.get_or_create(method_type=MethodType.ODE, settings=settings)
        self.assertEqual(self.m1.pk, m2.pk)
        self.assertEqual(len(m2.settings.all()), len(Setting.DEFAULTS))

    def test_method_type(self):
        self.assertEqual(self.m1.method_type, MethodType.ODE)


# ===============================================================================
# ParameterTest
# ===============================================================================
from simapp.models import Parameter, ParameterType


class ParameterTestCase(TestCase):
    def setUp(self):
        Parameter.objects.create(key='L', value=1E-6, unit="m",
                                 parameter_type=ParameterType.GLOBAL_PARAMETER)
        Parameter.objects.create(key='N', value=20, unit="-",
                                 parameter_type=ParameterType.BOUNDARY_INIT)

    def test_parameters(self):
        """Animals that can speak are correctly identified"""
        p1 = Parameter.objects.get(key='L', unit="m")
        p2 = Parameter.objects.get(key='N', unit="-")
        self.assertEqual(p1.key, 'L')
        self.assertEqual(p2.key, 'N')
        self.assertEqual(p1.value, 1E-6)
        self.assertEqual(p2.value, 20)
        self.assertEqual(p1.unit, 'm')
        self.assertEqual(p2.unit, '-')
        self.assertEqual(p1.parameter_type, ParameterType.GLOBAL_PARAMETER)
        self.assertEqual(p2.parameter_type, ParameterType.BOUNDARY_INIT)


# ===============================================================================
# TaskTest
# ===============================================================================
from simapp.models import Task


class TaskTestCase(TestCase):
    def setUp(self):
        self.model = CompModel.create(demo_sbml_no_annotations, model_format=CompModelFormat.SBML)
        settings = Setting.get_or_create_defaults()
        self.method = Method.get_or_create(method_type=MethodType.ODE, settings=settings)
        Task.objects.create(model=self.model, method=self.method)

    def test_counts(self):
        """Test the count methods."""
        t = Task.objects.get(model=self.model, method=self.method)
        self.assertEqual(t.sim_count(), 0)
        self.assertEqual(t.done_count(), 0)
        self.assertEqual(t.assigned_count(), 0)
        self.assertEqual(t.unassigned_count(), 0)
        self.assertEqual(t.error_count(), 0)

        self.assertEqual(t.priority, 0)
        self.assertEqual(t.info, None)

# ===============================================================================
# SimulationTest
# ===============================================================================
from simapp.db.api import create_simulation
from simapp.models import SimulationStatus


class SimulationTestCase(TestCase):
    def setUp(self):
        # create task
        self.model = CompModel.create(demo_sbml_no_annotations, model_format=CompModelFormat.SBML)
        settings = Setting.get_or_create_defaults()
        self.method = Method.get_or_create(method_type=MethodType.ODE,
                                           settings=settings)
        self.task = Task.objects.create(model=self.model, method=self.method)
        self.p1 = Parameter.objects.create(key='L', value=1E-6, unit="m",
                                           parameter_type=ParameterType.GLOBAL_PARAMETER)
        self.p2 = Parameter.objects.create(key='N', value=20, unit="-",
                                           parameter_type=ParameterType.BOUNDARY_INIT)

    def test_simulation_new(self):
        """ Test fields of newly created simulation. """
        sim = create_simulation(self.task, parameters=[self.p1, self.p1])
        self.assertEqual(sim.task.pk, self.task.pk)
        self.assertEqual(sim.status, SimulationStatus.UNASSIGNED)
        self.assertTrue(sim.is_unassigned())
        self.assertFalse(sim.is_done())
        self.assertFalse(sim.is_assigned())
        self.assertFalse(sim.is_error())
        self.assertFalse(sim.hanging)
        self.assertEqual(sim.task.sim_count(), 1)
        self.assertEqual(sim.task.unassigned_count(), 1)
        self.assertEqual(sim.task.assigned_count(), 0)
        self.assertEqual(sim.task.done_count(), 0)
        self.assertEqual(sim.task.error_count(), 0)

    def test_simulation_clean_creation(self):
        from django.core.exceptions import ValidationError
        # finalize the task
        self.task.finalize_status()
        # simulation creation should raise a ValidationError
        self.assertRaises(ValidationError, create_simulation, self.task, parameters=[])

    def test_simulation_clean_changing(self):
        from django.core.exceptions import ValidationError
        sim = create_simulation(self.task, parameters=[self.p1, self.p1])
        # finalize the task
        self.task.finalize_status()
        # no new simulation can be added
        self.assertRaises(ValidationError, create_simulation, self.task, parameters=[])
        # but the simulation can still be changed
        sim.status = SimulationStatus.DONE
        sim.save()
        self.assertEqual(SimulationStatus.DONE, sim.status)



# ===============================================================================
# ResultTest
# ===============================================================================
from simapp.models import Result, ResultType
from django.core.files import File


class ResultTestCase(TestCase):
    def setUp(self):
        # create task
        self.model = CompModel.create(demo_sbml_no_annotations, model_format=CompModelFormat.SBML)
        settings = Setting.get_or_create_defaults()
        self.method = Method.get_or_create(method_type=MethodType.ODE, settings=settings)
        self.task = Task.objects.create(model=self.model, method=self.method)
        self.p1 = Parameter.objects.create(key='L', value=1E-6, unit="m", parameter_type=ParameterType.GLOBAL_PARAMETER)
        self.p2 = Parameter.objects.create(key='N', value=20, unit="-", parameter_type=ParameterType.BOUNDARY_INIT)
        self.sim = create_simulation(self.task, parameters=[self.p1, self.p1])

    def test_result(self):
        from multiscale.examples.testdata import csv_filepath
        f = open(csv_filepath, 'r')
        myfile = File(f)
        result = Result.objects.create(simulation=self.sim, result_type=ResultType.CSV, file=myfile)
        self.assertEqual(result.simulation.pk, self.sim.pk)
        self.assertEqual(result.result_type, ResultType.CSV)

# ===============================================================================
# ViewTests
# ===============================================================================
from django.test.client import Client


class ViewTestCase(TestCase):
    """ Use the django client to test the status of all views. 
        Tests the urls.py and views.py.
        TODO: setup basic database content and test the views on it.
    """

    def setUp(self):
        self.c = Client()

    def tearDown(self):
        self.c = None

    def test_models_status(self):
        """ Check response status code for view. """
        response = self.c.get('/simapp/models/')
        self.assertEqual(response.status_code, 200)
        n_models = CompModel.objects.all().count()
        self.assertContains(response, 'Models'.format(n_models))

        #  check the response.context
        self.assertEqual(len(response.context['model_list']), n_models)
        # create a model
        CompModel.create(demo_sbml_no_annotations, model_format=CompModelFormat.SBML)
        response = self.c.get('/simapp/models/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['model_list'])>0)

    def test_cores_status(self):
        """ Check response status code for view. """
        response = self.c.get('/simapp/cores/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cores')

    def test_tasks_status(self):
        """ Check response status code for view. """
        response = self.c.get('/simapp/tasks/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tasks')

    def test_task_404(self):
        """ Check response status code for view. """
        response = self.c.get('/simapp/task/112312423')
        self.assertTrue(response.status_code, 404)

    def test_task_200(self):
        """ Check response status code for view. """
        self.model = CompModel.create(demo_sbml_no_annotations, model_format=CompModelFormat.SBML)
        settings = Setting.get_or_create_defaults()
        self.method = Method.get_or_create(method_type=MethodType.ODE, settings=settings)
        task = Task.objects.create(model=self.model, method=self.method)
        response = self.c.get('/simapp/task/{}'.format(task.pk))
        self.assertEqual(response.status_code, 200)

    def test_task_parameters(self):
        """ Check response status code for view. """
        self.model = CompModel.create(demo_sbml_no_annotations, model_format=CompModelFormat.SBML)
        settings = Setting.get_or_create_defaults()
        self.method = Method.get_or_create(method_type=MethodType.ODE, settings=settings)
        task = Task.objects.create(model=self.model, method=self.method)

        response = self.c.get('/simapp/task/T{}'.format(task.pk))
        self.assertEqual(response.status_code, 200)

    def test_methods_status(self):
        """ Check response status code for view. """
        response = self.c.get('/simapp/methods/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Methods')

    def test_simulations_status(self):
        """ Check response status code for view. """
        response = self.c.get('/simapp/simulations/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Simulations')

    def test_simulation_404(self):
        """ Check response status code for view. """
        response = self.c.get('/simapp/simulation/1934929349234')
        self.assertEqual(response.status_code, 404)

    def test_simulation_200(self):
        """ Check response status code for view. """
        self.model = CompModel.create(demo_sbml_no_annotations, model_format=CompModelFormat.SBML)
        settings = Setting.get_or_create_defaults()
        self.method = Method.get_or_create(method_type=MethodType.ODE, settings=settings)
        self.task = Task.objects.create(model=self.model, method=self.method)
        self.p1 = Parameter.objects.create(key='L', value=1E-6, unit="m", parameter_type=ParameterType.GLOBAL_PARAMETER)
        self.p2 = Parameter.objects.create(key='N', value=20, unit="-", parameter_type=ParameterType.BOUNDARY_INIT)
        sim = create_simulation(self.task, parameters=[self.p1, self.p1])

        response = self.c.get('/simapp/simulation/{}'.format(sim.pk))
        self.assertEqual(response.status_code, 200)

    def test_results_status(self):
        """ Check response status code for view. """
        response = self.c.get('/simapp/results/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Results')

    def test_documentation_status(self):
        """ Check response status code for view. """
        response = self.c.get('/simapp/about/')
        self.assertEqual(response.status_code, 200)

# ===============================================================================
# APITest
# ===============================================================================
from django.test.client import Client

from simapp.db.api import create_parameter, create_simulation, create_task, create_model
from simapp.db.api import create_settings, create_method


class APITestCase(TestCase):
    """ Test the API methods."""

    def setUp(self):
        self.model = CompModel.create(demo_sbml_no_annotations, model_format=CompModelFormat.SBML)
        settings = Setting.get_or_create_defaults()
        self.method = Method.get_or_create(method_type=MethodType.ODE, settings=settings)
        self.task = Task.objects.create(model=self.model, method=self.method)
        self.p1 = Parameter.objects.create(key='L', value=1E-6, unit="m", parameter_type=ParameterType.GLOBAL_PARAMETER)
        self.p2 = Parameter.objects.create(key='N', value=20, unit="-", parameter_type=ParameterType.BOUNDARY_INIT)

    def tearDown(self):
        pass

    def test_create_model(self):

        m1 = create_model(filepath=demo_sbml_no_annotations, model_format=CompModelFormat.SBML)

        self.assertEqual(m1.model_format, CompModelFormat.SBML)
        self.assertEqual(m1.model_id, demo_id)

    def test_create_parameter(self):
        p3 = create_parameter(key='L', value=1E-6, unit='m', parameter_type=ParameterType.GLOBAL_PARAMETER)
        p4 = create_parameter(key='N', value=20, unit='-', parameter_type=ParameterType.BOUNDARY_INIT)
        self.assertEqual(p3.key, 'L')
        self.assertEqual(p4.key, 'N')
        self.assertEqual(p3.value, 1E-6)
        self.assertEqual(p4.value, 20)
        self.assertEqual(p3.unit, 'm')
        self.assertEqual(p4.unit, '-')
        self.assertEqual(p3.parameter_type, ParameterType.GLOBAL_PARAMETER)
        self.assertEqual(p4.parameter_type, ParameterType.BOUNDARY_INIT)

    def test_create_simulation(self):
        sim = create_simulation(self.task, [self.p1, self.p2])
        self.assertEqual(sim.task.pk, self.task.pk)
        self.assertEqual(2, len(sim.parameters.all()))
        self.assertEqual(1, self.task.simulations.count())

    def test_create_task(self):
        task = create_task(model=self.model, method=self.method)
        self.assertEqual(task.model.pk, self.model.pk)
        self.assertEqual(task.method.pk, self.method.pk)

    def test_create_task_not_existing(self):
        self.model.pk = 10
        method_new = Method.get_or_create(MethodType.FBA, [])
        task = create_task(self.model, method=method_new)
        self.assertEqual(task.model.pk, self.model.pk)
        self.assertEqual(task.method.pk, method_new.pk)

    def test_create_method_from_settings(self):
        settings_dict = {SettingKey.T_START: 0.0,
                         SettingKey.T_END: 500.0,
                         SettingKey.STEPS: 100
                         }
        settings = create_settings(settings_dict, add_defaults=False)
        m = create_method(method_type=MethodType.ODE, settings=settings)
        self.assertEqual(m.method_type, MethodType.ODE)
        self.assertEqual(len(m.settings.all()), len(settings))

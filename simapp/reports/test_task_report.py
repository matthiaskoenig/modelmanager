"""
Testing the Task Report.
"""

from __future__ import print_function
import django
django.setup()

from django.test import TestCase, Client
from multiscale.examples.testdata import demo_sbml
from ..db.api import *
from task_report import TaskReport

class TaskReportTestCase(TestCase):
    def setUp(self):
        self.model = CompModel.create(demo_sbml, model_format=CompModelFormat.SBML)
        settings = Setting.get_or_create_defaults()
        self.method = Method.get_or_create(method_type=MethodType.ODE, settings=settings)
        self.task = Task.objects.create(model=self.model, method=self.method)
        self.p1 = Parameter.objects.create(key='L', value=1E-6, unit="m", parameter_type=ParameterType.GLOBAL_PARAMETER)
        self.p2 = Parameter.objects.create(key='N', value=20, unit="-", parameter_type=ParameterType.BOUNDARY_INIT)
        sim = create_simulation(self.task, parameters=[self.p1, self.p2])

        # client
        self.c = Client()

    def tearDown(self):
        pass

    def test_html_report(self):
        response = self.c.get('/simapp/task/T{}'.format(self.task.pk))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'status')

    def test_report(self):
        task_report = TaskReport(self.task)
        df = task_report.dataframe
        self.assertEqual(1, len(df))
        self.assertTrue('L' in df.columns)
        self.assertTrue('N' in df.columns)



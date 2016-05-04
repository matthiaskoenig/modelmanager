"""
Creating report of the parameters of a given task.
All parameters of the simulations in a given task are selected.
"""
from __future__ import print_function
import os
import time
from pandas import DataFrame
from multiscale.multiscale_settings import MULTISCALE_GALACTOSE_RESULTS


class TaskReport(object):
    def __init__(self, task):
        self.task = task
        self.dataframe = None
        self.create_parameter_dataframe()

    def create_parameter_dataframe(self):
        """ Pandas DataFrame from simulation parameters and some additional keys. """
        start = time.time()

        # create set of dictionaries for simulations and collect the keys
        sim_dicts = []
        # fetch the related
        simulations = self.task.simulations.all().prefetch_related('parameters')  # DB query
        for sim in simulations:
            data = {
                'sim': sim.pk,
                'status': sim.status_str,
                'core': sim.core,
                'duration': sim.duration,
            }
            for p in sim.parameters.all():  # not hitting DB again due to prefetch
                data[p.key] = p.value
            sim_dicts.append(data)

        print('time: ', (time.time() - start))
        self.dataframe = DataFrame(sim_dicts)

    def save_parameter_file(self, filepath=None):
        if filepath is None:
            filepath = self.filepath()
        if self.dataframe is None:
            self.create_parameter_dataframe()
        # write the csv
        print(filepath)
        self.dataframe.to_csv(filepath, sep='\t')

    def csv_string(self):
        return self.dataframe.to_csv(None, sep='\t')

    def filepath(self):
        return os.path.join(MULTISCALE_GALACTOSE_RESULTS, '{}_parameters.txt'.format(self.task))


if __name__ == "__main__":
    import django
    django.setup()

    from simapp.models import Task
    task = Task.objects.get(pk=1)
    task_report = TaskReport(task)
    task_report.save_parameter_file()



#!/usr/bin/python
"""
Prepares the data for analysis for given set of tasks.

@author: Matthias Koenig
@date: 2015-05-11
"""
from __future__ import print_function
from simapp.models import Task
from prepare_task import prepare_task_for_analysis


if __name__ == "__main__":
    task_pks = range(35, 43)

    for pk in task_pks:
        print('prepare for analysis: Task {}'.format(pk))
        task = Task.objects.get(pk=pk)
        prepare_task_for_analysis(task)

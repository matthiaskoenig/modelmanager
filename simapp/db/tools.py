"""
Helper functions for the interaction with the django database layer.
This module is used to create models, simulations and tasks in the database.

A task is a set of simulations with given integration settings, i.e. the
individual simulations of one task are comparable between each other.
All simulations belonging to the same task run with the same model
and the same settings.
Tasks have a priority which determines the order of execution,
tasks with higher priority are performed first.

If possible all interactions with the django database layer should
go via this intermediate module.
"""

from __future__ import print_function, division

import simapp.db.api as db_api
from django.db import transaction
from ..dist.samples import SampleParameter, Sample


def get_samples_from_task(task):
    """ Returns all samples for simulations in given task. """
    simulations = db_api.get_simulations_for_task(task)
    samples = []
    for simulation in simulations:
        sample = get_sample_from_simulation(simulation)
        if sample:
            samples.append(sample)
    return samples


def get_sample_from_simulation(simulation):
    """
    Reads the sample structure from the database, namely the
    parameters set for a odesim.
    Important to reuse the samples of a given task for another task.
    """
    parameters = db_api.get_parameters_for_simulation(simulation)
    s = Sample()
    for p in parameters:
        s.add_parameter(SampleParameter.from_parameter(p))
    return s


@transaction.atomic
def create_simulations_from_samples(task, samples):
    """ Creates all simulations for given samples.
        The simulation creation does not check if a simulation already exists,
        so that multiple identical simulation can be associated with a single
        task.
    """
    sims = []
    for sample in samples:
        parameters = []
        for sp in sample.parameters:
            # This takes forever to check if parameter already in db
            # How to improve this part ?
            p = db_api.create_parameter(key=sp.key, value=sp.value, unit=sp.unit,
                                        parameter_type=sp.parameter_type)
            parameters.append(p)

        sim = db_api.create_simulation(task, parameters)
        
        sims.append(sim)
    return sims


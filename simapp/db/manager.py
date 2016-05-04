"""
    Database util for consistency checks and database cleanup,
    for instance some simulations are hanging.
    This is the only module removing entries from the database.

    TODO: implement database integrity checks. Are all the files
    accessible. Run control checks.

    TODO: Check for timecourses associated with unassigned & assigned simulations
        and remove these files.

    TODO: remove hanging objects, i.e. parameters which are not used in any simulations

    TODO: remove temporary files which are not represented in the database, namely
        in the tmp_sim folder and the timecourse subfolder.

    TODO: setup cron jobs for database backup

    @author: Matthias Koenig
    @date: 2015-05-11
"""

from simapp.models import Simulation, Result
from simapp.models import SimulationStatus


def unassign_assigned_hanging_simulations(task=None, cutoff_minutes=10):
    unassign_hanging_simulations_with_status(SimulationStatus.ASSIGNED, task, cutoff_minutes)


def unassign_error_hanging_simulations(task=None, cutoff_minutes=10):
    unassign_hanging_simulations_with_status(SimulationStatus.ERROR, task, cutoff_minutes)


def unassign_hanging_simulations_with_status(status, task=None, cutoff_minutes=10):
    if not task:
        sims = Simulation.objects.filter(status=status)
    else:
        sims = Simulation.objects.filter(task=task, status=status)
    for sim in sims:
        if cutoff_minutes >= 0:
            if sim._is_hanging(cutoff_minutes):
                unassign_simulation(sim)
        else:
            unassign_simulation(sim)


def unassign_all_simulations():
    """ ! Be very careful ! Know what are you doing. """
    for sim in Simulation.objects.all():
        unassign_simulation(sim)


def unassign_simulations_by_ip(ip):
    for sim in Simulation.objects.filter(core__ip=ip):
        unassign_simulation(sim)


def unassign_simulations_by_pk(pks):
    for pk in pks:
        sim = Simulation.objects.get(pk=pk)
        unassign_simulation(sim)


def unassign_simulation(sim):
    """ Unassign given simulation.
        Removes the corresponding results if existing. """
    delete_results_for_simulation(sim)
    # reset simulation
    sim.status = SimulationStatus.UNASSIGNED
    sim.core = None
    sim.file = None
    sim.time_assign = None
    sim.time_sim = None
    sim.save()
    print "Simulation reset: ", sim


def delete_task(task):
    """ Deletes task and the simulations associated with the task. """
    delete_simulations_for_task(task)
    task.delete()


def delete_simulations_for_task(task):
    """ Deletes all simulations associated with a task. """
    sims = Simulation.objects.filter(task=task)
    for sim in sims:
        print "remove Simulation: ", sim.pk
        delete_results_for_simulation(sim)
        sim.delete()


def delete_results_for_simulation(sim):
    # TODO: delete the corresponding local file
    results = Result.objects.filter(simulation=sim)
    for result in results:
        result.delete()


#####################################################################################################
if __name__ == "__main__":
    import django
    django.setup()
    #-----------------------------------------------
    #     Unassign hanging simulations
    #-----------------------------------------------
    # task = Task.objects.get(pk=37)
    # print task
    # unassign_assigned_hanging_simulations(task=task, cutoff_minutes=-1);
    # unassign_assigned_hanging_simulations(task=None, cutoff_minutes=-1);
    # unassign_error_hanging_simulations(task=None, cutoff_minutes=-1);
    # unassign_error_hanging_simulations(cutoff_minutes=-1);
    
    #-----------------------------------------------
    #     Unassign by computer
    #-----------------------------------------------
    # unassignSimulationsByIP(ip='10.39.32.106')

    #-----------------------------------------------
    #     Unassign simulations by pk
    #-----------------------------------------------
    #pks = (26985, )
    #print(pks)
    # unassignSimulationsByPk(pks)
    
    #-----------------------------------------------
    #     Remove tasks
    #-----------------------------------------------
    # task = Task.objects.get(pk=1)
    # delete_task(task)
    
    #-----------------------------------------------
    #     Remove simulations for tasks
    #-----------------------------------------------
    # task_pks = (3,)
    # for pk in task_pks:
    #    task = Task.objects.get(pk=pk)
    #    removeSimulationsForTask(task)
    
    #-----------------------------------------------
    #     Unassign all simulations
    #-----------------------------------------------
    # ! CAREFUL - KNOW WHAT YOU ARE DOING !
    # unassignAllSimulation()

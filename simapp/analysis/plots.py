"""
Create simulation plots for individual timecourses.

@author: Matthias Koenig
@date: 2015-05-10
"""
from __future__ import print_function

import matplotlib.pyplot as plt

#===============================================================================
# Simulation plots
#===============================================================================
def read_data_from_result(result):
    """ Read the HDF5 numpy array in memory. """
    # h5_path = timecourse.hdf5
    
    # TODO: implement
    raise NotImplemented
    
#===============================================================================
# Task plots
#===============================================================================
def task_histogram(task, folder):
    """ Histogram of the all task parameters. """
    # get the parameter data for the task
    data = dict()
    for sim in task.simulations.all():
        for p in sim.parameters.parameters.all():
            if data.has_key(p.key):
                data[p.key].append(p.value)
            else:
                data[p.key] = [p.value]
    
    # create histogram for every parameter
    Np = len(data.keys())
    f, axarr = plt.subplots(1, Np)
    f.set_size_inches(Np*3, 3)
    num_bins = 20 
    for k, key in enumerate(data.keys()):
        x = data[key]
        axarr[k].hist(x, num_bins, normed=0, facecolor='green', alpha=0.5)
        axarr[k].set_title(key)
    

def pppv_plot(sim, folder):
    """
    Create the periportal (PP), perivenious (PV) plots.

    Access the data via the x data dictionary via SBML ids.
    PP__gal = x['PP__gal']
    PV__gal = x['PV__gal']
    PP__rbcM = x['PP__rbcM']
    PV__rbcM = x['PV__rbcM']
    """
    import logging
    if sim.status != DONE:
        logging.info('No timecourse available for simulation')
        return None
    
    x = read_data_from_timecourse(sim.timecourse)
    time = x['time']
    del x['time']
    
    fig = plt.figure()
    fig.set_size_inches(5, 5)
    
    # plot all the PP and PV pairs
    # TODO: handle the colors of the plots, unified color schema for
    # ids
    compounds = []
    for name, values in x.iteritems():
        if name.startswith("PP__") or name.startswith("PV__"):
            sname = name[4:]
            if sname in compounds:
                continue
            compounds.append(sname)
            plt.plot(time, x['PP__'+sname], color='k')
            plt.plot(time, x['PV__'+sname], label=name)
    
    plt.legend(loc=1)
    
    plt.title("Simulation " + str(sim.pk))
    plt.ylabel('concentration [mM]')
    plt.xlabel('time [s]')
    plt.xlim([7, 80])
    plt.ylim([-0.1, 1.1])

    # scatter(X,Y, s=75, c=T, alpha=.5)

    filename = folder + "/" + sim.task.model.sbml_id + "_pppv.png"
    plt.savefig(filename, dpi=72, bbox_inches='tight')
    print("Figure created")
        
    
def simulation_plots(sim, folder):
    pppv_plot(sim, folder)


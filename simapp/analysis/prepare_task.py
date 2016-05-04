#!/usr/bin/python
"""
Module for collecting and generating the files for a given task
necessary for subsequent analysis.
- creates folder for analysis
- creates parameter file
file and copying the used model for the simulations.

@author: Matthias Koenig
@date:   2014-06-06
"""

import os
import sys
import shutil
import subprocess
import pipes

from sh import rsync

from multiscale.multiscale_settings import MULTISCALE_GALACTOSE_RESULTS
from multiscalesite.settings import MEDIA_ROOT
from simapp.models import Task
from simapp.reports.task_report import createParameterFileForTask



# IPS = ('10.39.32.106', '10.39.32.189', '10.39.32.111', '10.39.34.27')
IPS = ('10.39.32.106', '10.39.32.189', '10.39.32.111')
# IPS = ('192.168.1.99', '192.168.1.100')
# IPS = ('192.168.1.99',)


def prepare_task_for_analysis(task):
    import time
    # directory for analysis
    date_str = time.strftime("%Y-%m-%d")
    directory = MULTISCALE_GALACTOSE_RESULTS + '/' + date_str + '_' + str(task)
    if not os.path.exists(directory):
        os.makedirs(directory)
    print directory

    # copy SBML
    sbml_file = str(task.model.file.path)
    shutil.copy2(sbml_file, directory)
    
    # create parameter file
    createParameterFileForTask(task, directory)
    
    # collect all the timecourses on localhost
    rsyncTimecoursesForTask(task)
    
    # copy timecourses to new target folder
    # not 
    target_dir = directory + '/' + str(task) + '/'
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    # source_dir = getTimecourseDirectory(task) + '/'
    # print 'copy', source_dir,'->', target_dir
    # copytree(source_dir, target_dir)


def rsyncTimecoursesForTask(task):
    directory = getTimecourseDirectory(task)
    to_path = directory + '/'
    if not os.path.exists(to_path):
        os.makedirs(to_path)
    for ip in IPS:
        host = 'mkoenig@' + ip
        from_path = host + ":" + directory + '/'
        print host        
        if exists_remote(host, to_path): 
            print 'rsync : ', from_path, '->', to_path      
            #rsync -ravzX --delete mkoenig@ip:directory directory
            rsync("-ravzX", from_path + '*.Rdata', to_path)
            rsync("-ravzX", from_path + '*.gz', to_path)


def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


def getTimecourseDirectory(task):
    return MEDIA_ROOT + 'timecourse' + '/' + str(task)


def exists_remote(host, path):
    """ Test if directory/file exists on remote host. """
    resp = subprocess.call(
        ['ssh', host, 'test -e %s' % pipes.quote(path)])
    return resp == 0

#############################################################################

if __name__ == '__main__':
    ''' Preparing data for analysis '''
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-t", "--task", dest="task_pk",
                      help="Provide task pk for analysis")
    
    (options, args) = parser.parse_args()
     
    if options.task_pk:
        task_pk = int(options.task_pk)
        print '#'*60
        print '# Prepare data T', task_pk
        print '#'*60
    else:
        sys.exit()
    task = Task.objects.get(pk=task_pk)
    if task is None:
        print 'Task does not exist'
        sys.exit()
     
    prepare_task_for_analysis(task)
    sys.exit()
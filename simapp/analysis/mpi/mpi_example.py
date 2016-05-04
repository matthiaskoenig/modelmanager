"""
Created on Apr 30, 2015

@author: mkoenig
"""
# run with
# mpiexec -n 4 python mpi_example.py

from mpi4py import MPI
import sys

size = MPI.COMM_WORLD.Get_size()
rank = MPI.COMM_WORLD.Get_rank()
name = MPI.Get_processor_name()

sys.stdout.write(
    "Hello, World! I am process %d of %d on %s.\n"
    % (rank, size, name))
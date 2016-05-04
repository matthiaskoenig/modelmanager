#!/bin/bash
############################################################
# Run unittests
#
# Usage: 
#	./run_tests.sh 2>&1 | tee ./run_tests.log
#
############################################################

python manage.py test

#-------------------------------------------------------------------------------
# Name:        ServiceStatus
# Purpose:     Allows us to check if services are running
#
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-

import subprocess

def check(serviceCmd):
    ''' Check to see if given service is running '''

    try:
        response,error = subprocess.Popen(['ps -Al | grep {0} | wc -l'.format(serviceCmd)], shell=True, stdout=subprocess.PIPE).communicate()

        if error is not None:
            raise ValueError

        # Convert the response to int
        response = int(response.strip())
        
        if response > 0:
            return True
        else:
            return False

    except ValueError as e:
        # TODO: This should not happen, but if it does let's alert someone that
        # it did. We will return 0 since we did not get a number
        return False

#!/usr/bin/python

from main import update_conf, execute_tests

if __name__ == "__main__":
        print "Test Runner Started ..."
        if update_conf():
                print "Executing Tests.."
                execute_tests()


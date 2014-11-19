import os
import logging
import pwd
import sys
from sys import argv
from optparse import OptionParser

USAGE = """%prog <server> [<server> ...] <command> [options] Commands:"""
def main():
    parser = OptionParser(USAGE)
    parser.add_option('-v', '--verbose', action="store_true",
                      default=False, help="display verbose output")
    parser.add_option('-w', '--no-wait', action="store_false", dest="wait",
                      default=True, help="won't wait for server to start "
                      "before returning")
    parser.add_option('-o', '--once', action="store_true",
                      default=False, help="only run one pass of daemon")
    # this is a negative option, default is options.daemon = True
    parser.add_option('-n', '--no-daemon', action="store_false", dest="daemon",
                      default=True, help="start server interactively")
    parser.add_option('-g', '--graceful', action="store_true",
                      default=False, help="send SIGHUP to supporting servers")
    parser.add_option('-c', '--config-num', metavar="N", type="int",
                      dest="number", default=0,
                      help="send command to the Nth server only")
    options, args = parser.parse_args()

    if len(args) < 2:
        parser.print_help()
        print '\nERROR: specify server(s) and command'
        return 1

    print args[-1]
    print args[:-1]

if __name__ == "__main__":
    auth="AUTH_tka4994f05534c4035a1078335a26a5afb_attr21546521"
    n=auth.index("_attr")
    auth_token=auth[:n]
    token=auth[n+5:]
    print n
    print auth_token
    print token
    args=argv[1:]
    account=argv[1]
    print account
    if len(args) <=3 :
	print "Number of args is not enough..."
	exit()
    i=0
    attr=argv[3:]
    attr_temp = ''
    for temp in attr:
	attr_temp = '%s %s' % (attr_temp,temp)
    print attr_temp.lstrip()

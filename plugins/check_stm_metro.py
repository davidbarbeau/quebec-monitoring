#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Checks the status of metros in Montreal.
"""
#
#
#     Copyright (C) 2012 Savoir-Faire Linux Inc.
#
#     This program is free software; you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation; either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program; if not, write to the Free Software
#     Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
#     Projects :
#               SFL Shinken plugins
#
#     File :
#               check_stm_metro.py Checks the status of metros in Montreal.
#
#
#     Author: Matthieu Caneill <matthieu.caneill@savoirfairelinux.com>
#
#

# Generated with tools/create_new_plugin.sh

import getopt
import sys

import re
import urllib2
import lxml.html

PLUGIN_NAME = "check_stm_metro"
PLUGIN_VERSION = "0.1"
STATE_OK = 0
STATE_WARNING = 1
STATE_CRITICAL = 2
STATE_UNKNOWN = 3
STATE_DEPENDENT = 4


def print_version():
    """Show plugin version
    """
    version_msg = """
%s.py v%s (sfl-shinken-plugins)

The SFL Shinken Plugins come with ABSOLUTELY NO WARRANTY. You may redistribute
copies of the plugins under the terms of the GNU General Public License.
For more information about these matters, see the file named COPYING.
""" % (PLUGIN_NAME, PLUGIN_VERSION)
    print version_msg


def print_support():
    """Show plugin support
    """
    support_msg = """
Send email to <matthieu.caneill@savoirfairelinux.com> if you have questions
regarding use of this software. To submit patches or suggest improvements,
send email to <matthieu.caneill@savoirfairelinux.com>
Please include version information with all correspondence (when
possible, use output from the --version option of the plugin itself).
"""
    print support_msg


def print_usage():
    """Show how to use this plugin
    """
    usage_msg = """
%s.py -w <warning> -c <critical>

Usage:
 -h, --help
    Print detailed help screen
 -V, --version
    Print version information
 -w, --warning=INT
    Number of problems to result in warning status
 -c, --critical=INT
    Number of problems to result in critical status
""" % PLUGIN_NAME
    print usage_msg


def get_html():
    url = 'http://www.stm.info/en/info/service-updates/metro'
    try:
        html = urllib2.urlopen(url)
    except Exception as e:
        print('Error while opening url: %s' % str(e))
        sys.exit(STATE_UNKNOWN)
    if html.getcode() >= 400:
        print('HTTP error: %d' % html.getcode())
        sys.exit(STATE_UNKNOWN)
    return html.read()

def get_data(args):
    """Fetch data
    """
    html = get_html()
    tree = lxml.html.fromstring(html)
    status = tree.xpath('//div[@id="wrap"]/div[@id="sub-wrap"]//div[contains(@class, "content-services")]//section[contains(@class,"item-line")]/p/text()')
    lines = tree.xpath('//div[@id="wrap"]/div[@id="sub-wrap"]//div[contains(@class, "content-services")]//section[contains(@class,"item-line")]/h2/text()')
    
    if len(status) == len(lines) == 4:
        problems = []
        for i in range(len(lines)):
            if status[i] != u'Normal métro service':
                problems.append(lines[i].strip())
        
        if 0 <= len(problems) < int(args['warning']):
            msg = 'OK'
            code = STATE_OK
        elif int(args['warning']) <= len(problems) < int(args['critical']):
            msg = 'WARNING'
            code = STATE_WARNING
        else:
            msg = 'CRITICAL'
            code = STATE_CRITICAL

        is_problems = len(problems) > 0
        final_msg = ('%(msg)s - %(problems)d problem%(plural)s %(list)s'
                     % {'msg': msg,
                        'problems': len(problems),
                        'plural': 's' if is_problems else '',
                        'list': ': ' + ', '.join(problems) if is_problems else ''})
        
        print('%(msg)s|problems=%(problems)d;;;0;;'
              % {'msg': final_msg, 'problems': len(problems)})
        sys.exit(code)
    
    print('Wrong data received: %s [...]' % html[:100])
    sys.exit(STATE_UNKNOWN)


def check_arguments(args):
    """Check mandatory fields
    """
    mandatory_arguments = ['warning',
                           'critical']
    for argument_name in mandatory_arguments:
        if not argument_name in args.keys():
            print "Argument '%s' is missing !" % argument_name
            print_usage()
            print_support()
            sys.exit(STATE_UNKNOWN)

def main():
    """Main function
    """
    try:
        options, args = getopt.getopt(sys.argv[1:],
                        'hVw:c:',
                        ['help', 'version',
                         'warning=', 'critical='])
    except getopt.GetoptError, err:
        print str(err)
        print_usage()
        sys.exit(STATE_UNKNOWN)

    args = {}

    for option_name, value in options:
        if option_name in ("-w", "--warning"):
            args['warning'] = value
        elif option_name in ("-c", "--critical"):
            args['critical'] = value
        elif option_name in ("-h", "--help"):
            print_version()
            print_usage()
            print_support()
            sys.exit(STATE_UNKNOWN)
        elif option_name in ("-V", "--version"):
            print_version()
            print_support()
            sys.exit(STATE_UNKNOWN)

    check_arguments(args)

    get_data(args)


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
#
# test_notebooks.py
#
# purpose:
# author:   Filipe P. A. Fernandes
# e-mail:   ocefpaf@gmail
# web:      http://ocefpaf.github.io/
# created:  14-Aug-2014
# modified: Wed 20 Aug 2014 09:57:33 PM BRT
#
# obs:
#

import os
import sys
import unittest
import subprocess
from glob import glob


def clean_output(pattern='*.nc'):
    [os.unlink(fname) for fname in glob(pattern)]


class RunNotebooks(unittest.TestCase):
    def setUp(self):
        files = []
        path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
        for root, dirs, fnames in os.walk(path):
            for fname in fnames:
                if fname.endswith(".ipynb"):
                    files.append(os.path.join(root, fname))
        self.files = files

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def test_notebooks(self):
        """Test the notebook with runipy."""
        for fname in self.files:
            folder, ipy_file = os.path.split(fname)
            # If reading or saving in that directory.
            os.chdir(folder)
            sys.path.append(folder)
            print("Running {}".format(ipy_file))
            ans = subprocess.check_call(['runipy',
                                         ipy_file,
                                         '--html',
                                         ipy_file[:-5] + 'html'])
            # Successful command does not mean Successful notebook!  We should
            # start raising failures that will propagate here.
            self.assertEqual(ans, 0)
            sys.path.pop()


def main():
    unittest.main()


if __name__ == '__main__':
    main()

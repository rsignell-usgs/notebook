# -*- coding: utf-8 -*-
#
# test_system-test_rules.py
#
# purpose:  Test system-test rules
# author:   Filipe P. A. Fernandes
# e-mail:   ocefpaf@gmail
# web:      http://ocefpaf.github.io/
# created:  14-Aug-2014
# modified: Wed 20 Aug 2014 09:55:13 PM BRT
#
# obs:
#

import os
import unittest


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

    def test_pyfile_exists(self):
        """Test the .py version of the .ipynb exists."""
        for fname in self.files:
            folder, ipy_file = os.path.split(fname)
            py_file = fname[:-5] + 'py'
            print('Looking for:\n{}\n'.format(py_file))
            self.assertTrue(os.path.isfile(py_file))

    def test_conda_requeriment_exists(self):
        """Check if there is a conda-requirements.txt for the notebook."""
        for fname in self.files:
            folder, ipy_file = os.path.split(fname)
            req = os.path.join(folder, 'conda-requirements.txt')
            print('Looking for:\n{}\n'.format(req))
            self.assertTrue(os.path.isfile(req))

    def test_pip_requeriment_exists(self):
        """Check if there is a pip-requirements.txt for the notebook."""
        for fname in self.files:
            folder, ipy_file = os.path.split(fname)
            req = os.path.join(folder, 'pip-requirements.txt')
            print('Looking for:\n{}\n'.format(req))
            self.assertTrue(os.path.isfile(req))


def main():
    unittest.main()


if __name__ == '__main__':
    main()

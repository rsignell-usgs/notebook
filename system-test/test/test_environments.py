# -*- coding: utf-8 -*-
#
# test_environments.py
#
# purpose:  Create a venv/conda env based on the given requirement file.
# author:   Filipe P. A. Fernandes
# e-mail:   ocefpaf@gmail
# web:      http://ocefpaf.github.io/
# created:  14-Aug-2014
# modified: Wed 20 Aug 2014 09:56:36 PM BRT
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

    def test_envs(self):
        """A test that would create the venv/condaenv based on a requirement
        file."""
        pass


def main():
    unittest.main()


if __name__ == '__main__':
    main()

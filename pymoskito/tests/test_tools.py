# -*- coding: utf-8 -*-

"""
test_tools
----------

Tests for several tools and functions
"""

import unittest
import numpy as np

from pymoskito import tools


class TestControlTools(unittest.TestCase):

    def setUp(self):
        self.A = np.array([[0, 1, 0], [0, 0, 2/25], [0, -800, -2]])
        self.B = np.array([[0], [0], [100]])
        self.C = np.array([[1, 0, 0]])
        self.Qc = np.array([[0, 0, 8], [0, 8, -16], [100, -200, -6000]])
        self.Qo = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 2/25]])
        self.poles = [-1, -1+1j, -1-1j]
        self.coefficients = np.array([2, 4, 3])
        self.K = np.array([[0.25, -7.5, 0.01]])
        self.L = np.array([[1], [-62], [775]])
        self.V = np.array([[0.25]])
        self.n = 3
        self.m = 1
        self.r = 1

    def test_controlability_matrix(self):
        """
        check the function, which calculates the controlability matrix
        """

        # enter matrices with wrong dimensions
        self.assertRaises(ValueError, tools.controlability_matrix,
                          np.array([[1, 1, 1], [1, 1, 1]]),
                          np.array([[1], [1], [1]]))
        self.assertRaises(ValueError, tools.controlability_matrix,
                          np.array([[1, 1], [1, 1]]),
                          np.array([[1], [1], [1]]))
        self.assertRaises(ValueError, tools.controlability_matrix,
                          np.array([[1, 1], [1, 1]]),
                          np.array([[1, 1, 1], [1, 1, 1]]))

        # enter matrices, where the system shall be not controllable
        self.assertRaises(ValueError, tools.controlability_matrix,
                          np.array([[0, 0], [0, 0]]),
                          np.array([[0], [0]]))

        # calculate an example
        test_Qc = tools.controlability_matrix(self.A, self.B)
        self.assertTrue(np.allclose(test_Qc, self.Qc))
        self.assertTrue(np.allclose(
            tools.controlability_matrix(self.A.tolist(), self.B.tolist()),
            self.Qc))

        # check dimensions
        self.assertEqual(test_Qc.shape, (self.n, self.n*self.m))

    def test_observability_matrix(self):
        """
        check the function, which calculates the observability matrix
        """

        # enter matrices with wrong dimensions
        self.assertRaises(ValueError, tools.observability_matrix,
                          np.array([[1, 1, 1], [1, 1, 1]]),
                          np.array([[1, 1, 1]]))
        self.assertRaises(ValueError, tools.observability_matrix,
                          np.array([[1, 1], [1, 1]]),
                          np.array([[1, 1, 1]]))
        self.assertRaises(ValueError, tools.observability_matrix,
                          np.array([[1, 1], [1, 1]]),
                          np.array([[1, 1], [1, 1], [1, 1]]))

        # enter matrices, where the system shall be not observable
        self.assertRaises(ValueError, tools.observability_matrix,
                          np.array([[0, 0], [0, 0]]),
                          np.array([[0, 0]]))

        # calculate an example
        test_Qo = tools.observability_matrix(self.A, self.C)
        self.assertTrue(np.allclose(test_Qo, self.Qo))
        self.assertTrue(np.allclose(
            tools.observability_matrix(self.A.tolist(), self.C.tolist()),
            self.Qo))

        # check dimensions
        self.assertEqual(test_Qo.shape, (self.r*self.n, self.n))

    def test_get_coefficients(self):
        """
        check function, which calculates the coefficients of a characteristic
        polynomial
        """

        # calculate an example
        co = tools.get_coefficients(self.poles)
        self.assertTrue(np.allclose(co, self.coefficients))
        self.assertEqual(co.size, self.coefficients.size)

    def test_place_siso(self):
        """
        test for pole placement
        """

        # ValueError must occur if it is a MIMO system
        self.assertRaises(ValueError, tools.place_siso,
                          np.array([[1, 1], [1, 1]]),
                          np.array([[1, 1], [1, 1]]),
                          self.poles)
        self.assertRaises(ValueError, tools.place_siso,
                          np.array([[1, 1], [1, 1]]),
                          np.array([[1], [1]]),
                          np.array([1, 1, 1]))

        # calculate a state feedback and an observer gain
        test_K = tools.place_siso(self.A, self.B, self.poles)
        test_L = tools.place_siso(self.A.transpose(),
                                  self.C.transpose(),
                                  self.poles).transpose()

        self.assertTrue(np.allclose(test_K, self.K))
        self.assertTrue(np.allclose(test_L, self.L))

    def test_prefilter(self):
        """
        check function, which calculates the prefilter matrix
        """

        self.assertRaises(ValueError, tools.calc_prefilter,
                          np.array([[1], [1]]),
                          np.array([[1], [1]]),
                          np.array([[1, 1]]))
        self.assertRaises(ValueError, tools.calc_prefilter,
                          np.array([[1, 1], [1, 1]]),
                          np.array([[1], [1], [1]]),
                          np.array([[1, 1]]))
        self.assertRaises(ValueError, tools.calc_prefilter,
                          np.array([[1, 1], [1, 1]]),
                          np.array([[1, 1, 1], [1, 1, 1]]),
                          np.array([[1, 1]]))

        self.assertRaises(ValueError, tools.calc_prefilter,
                          np.array([[1, 1], [1, 1]]),
                          np.array([[1], [1]]),
                          np.array([[1, 1, 1]]))
        self.assertRaises(ValueError, tools.calc_prefilter,
                          np.array([[1, 1], [1, 1]]),
                          np.array([[1], [1]]),
                          np.array([[1, 1], [1, 1], [1, 1]]))

        # enter matrices, where the prefilter's calculation should fail
        self.assertRaises(ValueError, tools.calc_prefilter,
                          np.array([[0, 0], [0, 0]]), np.array([[0], [0]]),
                          np.array([[0, 0]]), np.array([[0, 0]]))

        test_V = tools.calc_prefilter(self.A, self.B, self.C, self.K)
        self.assertTrue(np.allclose(test_V, self.V))


if __name__ == '__main__':
    unittest.main()

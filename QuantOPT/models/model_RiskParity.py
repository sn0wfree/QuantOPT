# coding=utf-8
from abc import ABC
from itertools import permutations

import numpy as np
import pandas as pd

from QuantOPT.models import BaseModels


class RiskParity(BaseModels, ABC):

    @classmethod
    def rc_i(cls, i, w, sigma2):
        SIGMA_dot_w = np.dot(sigma2, w.T)
        SIGMA_sqrt = np.sqrt(np.dot(w, np.dot(sigma2, w.T)))
        return cls.rc_i_reduced(i, w, SIGMA_dot_w, SIGMA_sqrt)

    @staticmethod
    def rc_i_reduced(i, w, SIGMA_dot_w, SIGMA_sqrt):
        d1 = w[i] * SIGMA_dot_w[i]
        return d1 / SIGMA_sqrt

    @staticmethod
    def rc_i_reduced_num(w_i, SIGMA_dot_w_i, SIGMA_sqrt):
        d1 = w_i * SIGMA_dot_w_i
        return d1 / SIGMA_sqrt

    @classmethod
    def loss_func(cls, w: np.array, **kwargs):
        """

        :param w: weight for min var
        :return: variance
        """
        sigma2 = cls.min_var_sigma2(w)
        SIGMA_dot_w = np.dot(sigma2, w.T)
        SIGMA_sqrt = np.sqrt(np.dot(w, np.dot(sigma2, w.T)))
        vri_list = (cls.rc_i_reduced_num(w_i, SIGMA_dot_w_i, SIGMA_sqrt) for w_i, SIGMA_dot_w_i in zip(w, SIGMA_dot_w))
        temp = np.nansum([np.power(a - b, 2) for a, b in permutations(vri_list, 2)])
        return temp

    @classmethod
    def run_opt(cls, stockpool: (list, np.array), sigma2: pd.DataFrame, bounds, constraints, method=None, **kwargs):
        """
        the main function for Minimum Variance Optimization(MVO) run optimization
        :param stockpool: the stockpool
        :param bounds: the bounds of weight
        :param constraints: the constraints of weight
        :param method: the method of optimization
        :param kwargs: the kwargs of optimization
        :return: the optimized weight
        """
        weight_length = len(stockpool)

        def min_var_sigma2(*args, **kwargs):
            return sigma2

        cls.min_var_sigma2 = min_var_sigma2
        return cls.opt(bounds, constraints, weight_length, method=method, **kwargs)


if __name__ == '__main__':
    pass

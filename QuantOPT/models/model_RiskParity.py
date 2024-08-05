# coding=utf-8
from abc import ABC
from itertools import permutations

import numpy as np
import pandas as pd

from QuantOPT.models import BaseModels


class RiskParity(BaseModels):
    @classmethod
    def mrc(cls, w, cov, port_std):
        return (np.dot(cov, w) / port_std).ravel()

    @classmethod
    def rc(cls, w, cov, port_std):
        mrc = cls.mrc(w, cov, port_std)
        return pd.DataFrame([w_i * mrc_i for w_i, mrc_i in zip(w, mrc)]).values.ravel()

    @classmethod
    def loss_func(cls, w: np.array, **kwargs):
        """

        :param w: weight for min var
        :return: variance
        """
        cov = cls.get_cov(w)
        port_std = cls.get_port_std(w)
        rc_list = cls.rc(w, cov, port_std)

        temp = np.nansum([np.power(a - b, 2) for a, b in permutations(rc_list, 2)])
        return temp

    @classmethod
    def run_opt(cls, stockpool: (list, np.array), port_std, cov, bounds, constraints, method=None, **kwargs):
        """

        :param stockpool: the stockpool
        :param bounds: the bounds of weight
        :param constraints: the constraints of weight
        :param method: the method of optimization
        :param kwargs: the kwargs of optimization
        :return: the optimized weight
        """
        weight_length = len(stockpool)

        def get_cov(*args, **kwargs):
            return cov

        def get_port_std(*args, **kwargs):
            return port_std

        cls.get_cov = get_cov
        cls.get_port_std = get_port_std
        return cls.opt(bounds, constraints, weight_length, method=method, **kwargs)


if __name__ == '__main__':
    pass

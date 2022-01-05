# coding=utf-8
from abc import ABC

import numpy as np

from QuantOPT.models import BaseModels


class MVO(BaseModels, ABC):
    @staticmethod
    def min_var_sigma2(*args, **kwargs):
        """
        return var_sigma function
        """
        return NotImplementedError('should be rewritten!')

    @staticmethod
    def stock_ret(*args, **kwargs):
        return NotImplementedError('should be rewritten!')

    @classmethod
    def loss_func(cls, w: np.array, **kwargs):
        """
        calculate variance with the given weight
        :param w: weight for min var
        :return: variance
        """
        sigma2 = cls.min_var_sigma2(w)
        stock_ret = cls.stock_ret(w)
        var = np.dot(w, np.dot(sigma2, w.T))
        return 0.5 * var - np.dot(w, stock_ret)

    @classmethod
    def run_opt(cls, stockpool, sigma2, stock_ret, bounds, constraints, method=None, **kwargs):
        """
        the main function for Minimum Variance Optimization run optimization
        :param stock_ret:
        :param sigma2:
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

        cls.stock_ret = lambda x: stock_ret

        cls.min_var_sigma2 = min_var_sigma2
        return cls.opt(bounds, constraints, weight_length, method=method, **kwargs)


if __name__ == '__main__':
    pass

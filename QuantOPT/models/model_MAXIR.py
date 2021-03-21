# coding=utf-8

from QuantOPT.core.base import _SimpleOpt


def maxIR_loss_func(cls, w, sigma2, port_ret, cost_func=lambda x: 0):
    return -1 * (cls.portfolio_return(w, port_ret) - cost_func(w)) / cls.risk(w, sigma2)


model = type('Model', (_SimpleOpt,), {'loss_func': classmethod(maxIR_loss_func)})

if __name__ == '__main__':
    pass

#coding=utf-8

from typing import OrderedDict, Union
import pandas as pd
import numpy as np
from scipy import optimize

import warnings
MAX_ITER_COUNT = 15000*2

class _Orderedbnds(object):
    def __init__(self,weight_length:int,default_lower:Union[int,float]=0,default_upper:Union[int,float]=1) -> None:
        """
        
        :param weight_length: the length of weigth vector
        :param default_lower: the default lower bound
        :param default_upper: the default upper bound
        :return: OrderedDict, {i:(约束下限,约束上限)}
        """
        t = {i:(default_lower,default_upper) for i in range(weight_length)}
        self.odict = OrderedDict(t)

    def update(self,adict:dict):
        self.odict.update(adict)

    def __getitem__(self,key):
        return self.odict[key]

    def __setitem__(self,key,value):
        self.odict.__setitem__(key,value)

    def tolist(self):
        return list(self.odict.values())

class _SimpleOpt(object):
    """
    
    base function
    """
    @staticmethod
    def tc(x):
        return 0

    @staticmethod
    def create_bound(weight_length:int,bounds=None,default_lower=0,default_upper=1):
        """
        create_bound 给定权重的上下限，返回一个 OrderedDict.tolist() 可以转换为 scipy.optimize.minimize 的参数

        :param weight_length: the length of weight
        :param bounds: the extra bounds of weight
        :param default_lower: the default lower bound of weight
        :param default_upper: the default upper bound of weight
        :return: a list of bounds
        """
        OB = _Orderedbnds(weight_length,default_lower,default_upper)

        if bounds is None:
            pass
        else:
            for i,lower,upper in bounds:
                OB[i]=( lower,upper )
        return OB.tolist()

    
    @staticmethod
    def total_upper(w):
        """
        total upper bound of weight

        :param w: weight
        :return: constraint function reuslt: total upper bound of weight
        """
        return 1 - np.sum(w)

    @staticmethod   
    def total_lower(w):
        """
        total lower bound of weight

        :param w: weight
        :return: constraint function reuslt: total lower bound of weight
        """
        return np.sum(w)

    @staticmethod
    def create_weight(length:int = 100):
        """
        create weight from equal distribution
        :param: length: the length of weight
        :return: weight
        
        """
        return np.array(1/length*np.ones(length))
    @staticmethod
    def scipy_optimize_minimize(fmin,x,args=(),method=None,jac=None,hassp=None,bounds=None,constraints=(),tol=None,callback=None,options=None,**kwargs):
        """
        the core function of optimizer, which will use scipy optimize minimize function to optimize the function

        :param fmin: the function to be optimized
        :param x: the initial value of weight
        :param args: the args of function
        :param method: the method of optimization
        :param jac: the jacobian of function
        :param hassp: the has sparsity of function
        :param bounds: the bounds of weight
        :param constraints: the constraints of weight
        :param tol: the tolerance of optimization
        :param callback: the callback function
        :param options: the options of optimization
        :param kwargs: the kwargs of optimization
        :return: the optimized weight
        
        
        """



        if options is None:
            options = {'maxiter':MAX_ITER_COUNT}
        else:
            options.update({'maxiter':MAX_ITER_COUNT})
        return optimize.minimize(fmin,x,args=args,method=method,jac=jac,hassp=hassp,bounds=bounds,constraints=constraints,tol=tol,callback=callback,options=options,**kwargs)

    @classmethod
    def create_constraints(cls,constraints,add_default=True):
        """
        create constraints from the given constraints parameters
        :param constraints: the constraints parameters
        :param add_default: whether add the default constraints
        :return: the constraints of weight
        
        """
        if add_default:
            LC = [{'type':'ineq','fun':cls.total_lower},{'type':'ineq','fun':cls.total_upper}]
        else:
            LC = []
        if constraints is not None:
            for c in constraints:
                if isinstance(c,dict):
                    LC.append(c)
                else:
                    warnings.warn(f'found wrong constraints: {c}, please check the constraints, will pass this one!')
        return LC

class _MinVar(object):
    @staticmethod
    def min_var_sigma2():
        """
        return var_sigma function
        """
        return ValueError('should be rewrite!')
    @classmethod
    def min_var_constraints(cls,constraint,add_default=True):
        """
        create constraints
        :param constraints: the raw of constraints
        :param add_default: boolen, whether add default settings
        :return: useable constraints for minimum variance

        """
        return _SimpleOpt.create_constraints(constraint,add_default=add_default)

    @classmethod
    def min_var(cls,w:np.array):
        """
        calcualte variance with the given weight
        :param w: weight for min var
        :return: variance
        """
        return np.dot(w,cls.min_var_sigma2()*w.T)


    @classmethod
    def opt(cls, bounds,constraints,weight_length,method=None,**kwargs):
        """
        the core function to calculate optimized solutions thought scipy optimization and minimize
        :param bounds: the bounds of weight
        :param constraints: the constraints of weight
        :param weight_length: the length of weight
        :param method: the method of optimization
        :param kwargs: the kwargs of optimization
        :return: the optimized weight
        """
        w = _SimpleOpt.create_weight(weight_length)
        cons = cls.min_var_constraints(constraints)
        fmin = cls.min_var
        if method is None:
            method = 'L-BFGS-B'
        if 'options' not in kwargs:
            kwargs['options'] = {'maxiter':MAX_ITER_COUNT}
        else:
            kwargs['options'].update({'maxiter':MAX_ITER_COUNT})
        return _SimpleOpt.scipy_optimize_minimize(fmin,w,bounds=bounds,constraints=cons,method=method,**kwargs)

    @classmethod
    def run_opt(cls, stockpool,bounds,constraints,method=None,**kwargs):
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
        return cls.opt(bounds,constraints,weight_length,method=method,**kwargs) 
        
        
class MinVar(object):
    """
    the class for Minimum Variance Optimization(MVO)
    """
    # def __init__(self,stockpool,bounds=None,constraints=None,method=None,**kwargs):
    #     """
    #     the constructor of Minimum Variance Optimization(MVO)
    #     :param stockpool: the stockpool
    #     :param bounds: the bounds of weight
    #     :param constraints: the constraints of weight
    #     :param method: the method of optimization
    #     :param kwargs: the kwargs of optimization
    #     """
    #     self.stockpool = stockpool
    #     self.bounds = _SimpleOpt.create_bounds(len(stockpool),bounds,default_lower=0,default_upper=1)
    #     self.constraints = _SimpleOpt.create_constraints(constraints)
    #     self.method = method

    @staticmethod
    def _run_opt_fun(stockpool,bounds,constraints,min_var_sigma2,method=None,**kwargs):
        """
        the function for run optimization
        :param stockpool: the stockpool
        :param bounds: the bounds of weight
        :param constraints: the constraints of weight
        :param method: the method of optimization
        :param kwargs: the kwargs of optimization
        :return: the optimized weight
        """
        _MinVar.min_var_sigma2 = min_var_sigma2
        return _MinVar.run_opt(stockpool,bounds,constraints,method=method,**kwargs)
    @classmethod
    def run_opt(cls, stockpool,bounds,constraints,sigma2,method=None,**kwargs):
        """
        the main(shell) func for Minimum Variance Optimization(MVO)
        :param stockpool: the stockpool
        :param bounds: the bounds of weight
        :param constraints: the constraints of weight
        :param sigma2: the sigma2 function
        :param method: the method of optimization
        :param kwargs: the kwargs of optimization
        :return: the optimized weight
        """
        def min_var_sigma2():
            return sigma2

        return cls._run_opt_fun(stockpool,bounds,constraints,min_var_sigma2,method=method,**kwargs)


class MaxRiskAdjReturn(object):
    """
    the class for Maximum Risk Adjust Return Optimization(MRAO)

    requires:
        sigma2: the sigma2 function 协方差矩阵
        lambda_r: 风险厌恶系数
        portfolio_return: 组合收益率
        TC function: the TC function

    """
    

    @staticmethod
    def _run_opt_fun(stockpool,bounds,constraints,min_var_sigma2,risk_aversion,get_portfolio_returns,TC_func=None,method=None,**kwargs):
        """
        the core function which will call _MaxRiskAdjReturn.run_opt with the given Min_var_sigma2 matrix,risk aversion,get_portfolio_return and TC_func for run optimization
        :param stockpool: the stockpool
        :param bounds: the bounds of weight
        :param constraints: the constraints of weight
        :param method: the method of optimization
        :param kwargs: the kwargs of optimization
        :return: the optimized weight
        """
        _MaxRiskAdjReturn.min_var_sigma2 = min_var_sigma2
        _MaxRiskAdjReturn.risk_aversion = risk_aversion
        _MaxRiskAdjReturn.get_portfolio_returns = get_portfolio_returns
        _MaxRiskAdjReturn.TC_func = TC_func if TC_func is not None else _SimpleOpt.tc
        return _MaxRiskAdjReturn.run_opt(stockpool,bounds,constraints,method=method,**kwargs) 



    @classmethod
    def run_opt(cls, stockpool,bounds,constraints,sigma2,lambda_r,portfolio_returns,TC_func=None,method=None,**kwargs):
        """
        the main(shell) func for Maximum Risk Adjust Return Optimization(MRAO)
        :param stockpool: the stockpool
        :param bounds: the bounds of weight
        :param constraints: the constraints of weight
        :param sigma2: the sigma2 function
        :param lambda_r: the risk aversion
        :param portfolio_returns: the get_portfolio_returns function
        :param TC_func: the TC function
        :param method: the method of optimization
        :param kwargs: the kwargs of optimization
        :return: the optimized weight
        """
        def min_var_sigma2():
            return sigma2
        def risk_aversion():
            return lambda_r

        def get_portfolio_returns():
            return portfolio_returns

        return cls._run_opt_fun(stockpool,bounds,constraints,min_var_sigma2,risk_aversion,get_portfolio_returns,TC_func=TC_func,method=method,**kwargs)


class _MaxRiskAdjReturn(object):
    """
    
     requires:
        sigma2: the sigma2 function 协方差矩阵
        lambda_r: 风险厌恶系数
        portfolio_return: 组合收益率
        TC function: the TC function

    """

    @staticmethod
    def TC(w):
        """
        the total cost function

        :param w: the weight
        :return: the total cost
        """
        return _SimpleOpt.tc(w)
        
    @staticmethod
    def min_var_sigma2(w):
        """
        the sigma2 function

        :param w: the weight
        :return: the sigma2
        """
        raise NotImplementedError('return sigma2 should be rewriten!')
    @staticmethod
    def risk_aversion(w):
        """
        the risk aversion function

        :param w: the weight
        :return: the risk aversion
        """
        raise NotImplementedError('return lambda_r should be rewriten!')

    @staticmethod
    def get_portfolio_returns(w):
        """
        the portfolio returns function

        :param w: the weight
        :return: the portfolio returns
        """
        raise NotImplementedError('return get_portfolio_returns should be rewriten!')

    @classmethod
    def min_var_constraints(cls,constraints,add_default=True):
        """
        the constraints function

        :param constraints: the constraints
        :param add_default: whether add the default constraints
        :return: the constraints
        """
        
        constraints = _SimpleOpt.create_constraints(constraints,add_default=add_default)
        return constraints
    @classmethod
    def loss_func(cls,w):
        """
        the loss function

        :param w: the weight
        :return: the loss
        """
        return cls.TC(w) + cls.aversion_risk(w) - cls.portfolio_returns(w)

    @classmethod
    def aversion_risk(cls,w):
        """
        the risk aversion function

        :param w: the weight
        :return: the risk aversion
        """
        return cls.risk_aversion() * np.dot(np.dot(w,cls.sigma2()),w.T)

    @classmethod
    def portfolio_returns(cls,w):
        """
        the portfolio returns function

        :param w: the weight
        :return: the portfolio returns
        """
        try:
            return np.sum(np.dot(w,cls.get_portfolio_returns()))
        except ValueError as e:
            return np.sum(np.dot(w,cls.get_portfolio_returns().T))

    @classmethod
    def opt(cls,bounds,constraints,weight_length, method=None,jac=None,hess=None,hessp=None,tol=None,callback=None,option=None,**kwargs):
        """
        the optimization function

        
        :param bounds: the bounds of weight
        :param constraints: the constraints of weight
        :param method: the method of optimization
        :param kwargs: the kwargs of optimization
        :return: the optimized weight
        """
        w = _SimpleOpt.create_weight(weight_length)
        cons = cls.min_var_constraints(constraints)
        fmin = cls.loss_func
        if method is None:
            method = 'L-BFGS-B'
        return _SimpleOpt.scipy_optimize_minimize(w,fmin,bounds,cons,method=method,jac=jac,hess=hess,hessp=hessp,tol=tol,callback=callback,option=option,**kwargs)

    @classmethod
    def run_opt(cls,stockpool,bounds,constraints,method=None,**kwargs):
        """
        the main(shell) func for Maximum Risk Adjust Return Optimization(MRAO)
        :param stockpool: the stockpool
        :param bounds: the bounds of weight
        :param constraints: the constraints of weight
        :param method: the method of optimization
        :param kwargs: the kwargs of optimization
        :return: the optimized weight
        """
        weight_length = len(stockpool)
        return cls.opt(bounds,constraints,weight_length,method=method,**kwargs)


class _MaxIR(object):
    """
    require:
        sigma2: the sigma2 function 协方差矩阵
        lambda_r: 风险厌恶系数
        portfolio_return: 组合收益率
        TC function: the TC function
    """

    @staticmethod
    def TC(w):
        """
        the total cost function

        :param w: the weight
        :return: the total cost
        """
        return _SimpleOpt.tc(w)
        
    @staticmethod
    def min_var_sigma2(w):
        """
        the sigma2 function

        :param w: the weight
        :return: the sigma2
        """
        raise NotImplementedError('return sigma2 should be rewriten!')
    @staticmethod
    def risk_aversion(w):
        """
        the risk aversion function

        :param w: the weight
        :return: the risk aversion
        """
        raise NotImplementedError('return lambda_r should be rewriten!')

    @staticmethod
    def get_portfolio_returns(w):
        """
        the portfolio returns function

        :param w: the weight
        :return: the portfolio returns
        """
        raise NotImplementedError('return get_portfolio_returns should be rewriten!')

    @classmethod
    def portfolio_returns(cls,w):
        """
        the portfolio returns function
        """
        try:
            return np.sum(np.dot(w,cls.get_portfolio_returns()))
        except ValueError as e:
            return np.sum(np.dot(w,cls.get_portfolio_returns().T))

    @classmethod
    def min_var_constraints(cls,constraints,add_default=True):
        """
        the constraints function

        :param constraints: the constraints
        :param add_default: whether add the default constraints
        :return: the constraints
        """
        
        constraints = _SimpleOpt.create_constraints(constraints,add_default=add_default)
        return constraints


    @classmethod
    def loss_func(cls,w):
        """
        the loss function

        :param w: the weight
        :return: the loss
        """
        warnings.warn("由于超额收益构造复杂，且无直接数据，特此降维为组合收益超额收益，组合风险代替主动风险")
        return (cls.TC(w) - cls.portfolio_returns(w))/cls.risk(w)

    @classmethod
    def risk(cls,w):
        s = np.dot(np.dot(w,cls.min_var_sigma2(w)),w.T)
        if s <0:
            warnings.warn("sigma2 is negative, please check your data! will set a large value 1w10!")

            std  = 1e10
        else:
            std = np.sqrt(s)
        return std


    @classmethod
    def opt(cls,bounds,constraints,weight_length, method=None,jac=None,hess=None,hessp=None,tol=None,callback=None,option=None,**kwargs):
        """
        the optimization function

        
        :param
        """
        w = _SimpleOpt.create_weight(weight_length)
        cons = cls.min_var_constraints(constraints)
        fmin = cls.loss_func
        if method is None:
            method = 'L-BFGS-B'

        return _SimpleOpt.scipy_optimize_minimize(w,fmin,bounds,cons,method=method,jac=jac,hess=hess,hessp=hessp,tol=tol,callback=callback,option=option,**kwargs)

    @classmethod
    def run_opt(cls,stockpool,bounds,constraints,method=None,**kwargs):
        """
        the main(shell) func for Maximum ICIR Optimization(MICIPO)
        :param stockpool: the stockpool
        :param bounds: the bounds of weight
        :param constraints: the constraints of weight
        :param method: the method of optimization
        :param kwargs: the kwargs of optimization
        :return: the optimized weight
        """
        weight_length = len(stockpool)
        return cls.opt(bounds,constraints,weight_length,method=method,**kwargs)


class _MaxICIR(object):

    @classmethod
    def _run_opt_func(cls,stockpool,bounds,constraints,min_var_sigma2,risk_aversion,get_portfolio_returns,TC_func=None,method=None,**kwargs):
        """
        the main(shell) func for Maximum ICIR Optimization(MICIPO)
        :param stockpool: the stockpool
        :param bounds: the bounds of weight
        :param constraints: the constraints of weight
        :param method: the method of optimization
        :param kwargs: the kwargs of optimization
        :return: the optimized weight
        """
        _MaxIR.min_var_sigma2 = min_var_sigma2
        _MaxIR.risk_aversion = risk_aversion
        _MaxIR.get_portfolio_returns = get_portfolio_returns
        if TC_func is not None:
            _MaxIR.TC = _SimpleOpt.tc
        else:
            _MaxIR.TC = TC_func

        return _MaxIR.run_opt(stockpool,bounds,constraints,method=method,**kwargs)

    @classmethod
    def run_opt(cls,stockpool,bounds,constraints,sigma2,lambda_r,portfolio_returns,TC_func=None,method=None,**kwargs):
        """
        the main(shell) func for Maximum ICIR Optimization(MICIPO)
        :param stockpool: the stockpool
        :param bounds: the bounds of weight
        :param constraints: the constraints of weight
        :param method: the method of optimization
        :param kwargs: the kwargs of optimization
        :return: the optimized weight
        """
        def min_var_sigma2_func():
            return sigma2

        def risk_aversion_func():
            return lambda_r
        

        def get_portfolio_returns_func():
            return portfolio_returns
        

        return cls._run_opt_func(stockpool,bounds,constraints,min_var_sigma2_func,risk_aversion_func,get_portfolio_returns_func,TC_func=TC_func,method=method,**kwargs)


if __name__ == '__main__':
    pass
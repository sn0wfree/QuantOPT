# coding=utf-8
import warnings
from functools import lru_cache
import numpy as np
import pandas as pd

from typing import List, Tuple, Union, Dict, Optional, Callable, Any

from QuantOPT.core.opt3 import _SimpleOpt
__current_priority__: int = 1
__first_time__: bool = True
__max_try_count__: int = 10

from QuantOPT import opt3
class Constraint(Ext):
    pass


for func_name_sample, kwargs_sample, formula_sample, import_func, direction in load_all(f=setting_yaml_path):
    set_attribute(Constraints, func_name_sample, kwargs_sample,
                  formula_sample, import_func, direction)


class Relaxer(object):
    @classmethod
    def parse_all(cls, args_list: Union[list, tuple], relax_mul: float = 0.01, constr_cls=Constraints):
        """
        parse all constraints
        """
        if relax_mul < 0:
            warnings.warn(
                'relax_mul must be greater than 0, will fiercely set to 1%')
            relax_mul = 0.01
        for func, kwargs, priority, constraint_type in args_list:
            yield constraint_type, cls.parse(getattr(constr_cls, func), kwargs, priority, relax_mul)

    @staticmethod
    def get_side(func: object):
        """
        get the side of the constraint
        """
        var = func.__code__.co_varnames[-1]
        if var.startswith('func_') and var.endswith('_lower'):
            side = -1
        elif var.startswith('func_') and var.endswith('_eq'):
            side = 0
        else:
            side = 1
        return side

    @classmethod
    def parse(cls, func, kwargs, priority, relax_mul_incr: float = 0.01):
        """
        parse constraint function to constraint object
        """
        relax = priority == __current_priority__

        side = cls.get_side(func)
        if relax and 'bound_value' in kwargs.keys() and not __first_time__:
            kwargs['bound_value'] = np.abs(
                kwargs['bound_value']*relax_mul_incr) + kwargs['bound_value']
        return func(**kwargs)


    @staticmethod
    def get_priority_level():
        """
        get the current priority level of the constraint
        """
        return __current_priority__

    @staticmethod
    def get_current_priority():
        """
        get the current priority level of the constraint
        """
        global __current_priority__
        return __current_priority__

    @staticmethod
    def increase_priority_level():
        """
        increase the current priority level  of the constraint
        """
        global __current_priority__
        __current_priority__ += 1
        # __first_time__ = False

    @staticmethod
    def decrease_priority_level():
        """
        deccrease the current priority level  of the constraint
        """
        global __current_priority__
        __current_priority__ -= 1

    @staticmethod
    def switch_first_time():
        """
        switch first time status of the constraint
        """
        global __first_time__
        __first_time__ = False

    @staticmethod
    def reset_priority_level():
        """
        reset the current priority level  of the constraint
        """
        global __current_priority__
        __current_priority__ = 1

    @staticmethod
    def get_max_try_count():
        """
        get the max try count of the constraint
        """
        global __max_try_count__
        return __max_try_count__

    @staticmethod
    def increase_max_try_count():
        """
        increase the max try count of the constraint
        """
        global __max_try_count__
        __max_try_count__ += 1

    @staticmethod
    def decrease_max_try_count():
        """
        decrease the max try count of the constraint
        """
        global __max_try_count__
        __max_try_count__ -= 1

    @staticmethod
    def reset_max_try_count():
        """
        reset the max try count of the constraint
        """
        global __max_try_count__
        __max_try_count__ = 10

class RunOpt(Relaxer):
    """
    run optimization
    """
    @classmethod
    def param2constraints(cls,constraint_param_list,step_length=0.01,constr_cls=Constraints):
        """
        parse constraint parameters to constraint objects
        """
        for c_types,func in cls.parse_all(constraint_param_list,relax_mul=step_length,constr_cls=constr_cls):
            yield {'types':c_types,'fun':func}


    @classmethod
    def run_opt_single(cls,kwargs_data,constraint_param_list,method,step_length=0.01,default_lower=0,default_upper=1,constr_cls=Constraints):
        """
        run optimization
        """
        # parse constraint parameters to constraint objects
        len_pool=len(kwargs_data['stockpool'])
        bounds = _SimpleOpt.create_bounds(len_pool,default_lower,default_upper)
        constraints = list(cls.param2constraints(constraint_param_list,step_length=step_length,constr_cls=constr_cls))
        
        
        # run optimization
        res = getattr(opt3,method).run_opt(bounds=bounds,constraints=constraints,**kwargs_data)
        return res


    @classmethod
    def run_opt_slack(cls,kwagrs_data,constraint_param_list,method,step_length=0.01,default_lower=0,default_upper=1,max_try_count=10,bounds=None,constr_cls=Constraints):
        """
        run_opt_slack, run optimization with slack
        给定优化参数方法，使用opt3模块中的对应的优化方法进行优化，如果不成功，则使用slack方法进行优化，直到达到指定的最大尝试次数或者最大优先等级
        """
        global __current_priority__
        global __max_try_count__
        
        __first_time__ = True
        __current_priority__ = 1
        funcs,kwargs,priorities,constraint_types = zip(*constraint_param_list)
        max_priority = max(priorities)
        active_slack= max_priority != 0

        res = cls.run_opt_single(kwagrs_data,constraint_param_list,method,step_length=step_length,default_lower=default_lower,default_upper=default_upper,constr_cls=constr_cls)

        cls.switch_first_time()
        if active_slack:
            count =0
            while res.success is False and count < max_try_count:
                # cls.increase_max_try_count()
                res = cls.run_opt_single(kwagrs_data,constraint_param_list,method,step_length=step_length,default_lower=default_lower,default_upper=default_upper,constr_cls=constr_cls)
                if count >= max_try_count:
                    warnings.warn('max try count reached! will imporve priority level')
                    count = 0
                    if cls.get_current_priority() > max_priority:
                        warnings.warn('max priority reach! will end automatically!')
                        break
                    else:
                        cls.increase_priority_level()
                        
                else:
                    count += 1
        return res,constraint_param_list

       
       
        











if __name__ == '__main__':
    pass

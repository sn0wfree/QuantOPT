# coding=utf-8

import warnings
from typing import Union, Any

import numpy as np

from QuantOPT.constraints.constraints import Constraints
from QuantOPT.core import core as opt3
from QuantOPT.core.base import _SimpleOpt

__current_priority__: int = 1
__first_time__: bool = True
__max_try_count__: int = 3


class Relaxer(object):
    @classmethod
    def parse_all(cls, args_list: Union[list, tuple], relax_mul: float = 0.01, constr_cls=Constraints):
        """
        parse all constraints

        :param args_list:
        :param relax_mul:
        :param constr_cls:
        :return:
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

        :param func:
        :param kwargs:
        :param priority:
        :param relax_mul_incr:
        :return:
        """
        global __current_priority__
        relax = priority == __current_priority__
        side = cls.get_side(func)
        if relax and 'bound_value' in kwargs.keys() and not __first_time__:
            kwargs['bound_value'] = side * kwargs['bound_value'] * np.abs(relax_mul_incr) + kwargs['bound_value']
        return func(**kwargs)

    @staticmethod
    def get_priority_level():
        """
        get the current priority level of the constraint
        """
        global __current_priority__
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
    kwargs_data: dict[str, Any]

    def __init__(self, method='MinVar', **kwargs):
        """

        :param method:
        :param kwargs:
        """
        self.method = method
        self.kwargs_data = kwargs

    def run_opt(self, constraint_param_list, slack=False, **kwargs):
        """

        :param constraint_param_list:
        :param slack:
        :param kwargs:
        :return:
        """

        func = self.run_opt_slack if slack else self.run_opt_single

        return func(self.kwargs_data, constraint_param_list, self.method, **kwargs)

    @classmethod
    def param2constraints(cls, constraint_param_list, step_length=0.01, constr_cls=Constraints):
        """

        parse constraint parameters to constraint objects

        :param constraint_param_list:
        :param step_length:
        :param constr_cls:
        :return:
        """

        for c_types, func in cls.parse_all(constraint_param_list, relax_mul=step_length, constr_cls=constr_cls):
            yield {'type': c_types, 'fun': func}

    @classmethod
    def run_opt_single(cls, kwargs_data, constraint_param_list, method, step_length=0.01, bounds=None, default_lower=0,
                       default_upper=1, constr_cls=Constraints):
        """

        run optimization

        :param kwargs_data:
        :param constraint_param_list:
        :param method:
        :param step_length:
        :param bounds:
        :param default_lower:
        :param default_upper:
        :param constr_cls:
        :return:
        """

        # parse constraint parameters to constraint objects
        len_pool = len(kwargs_data['stockpool'])
        bounds = _SimpleOpt.create_bounds(len_pool, bounds, default_lower, default_upper)
        constraints = list(cls.param2constraints(constraint_param_list, step_length=step_length, constr_cls=constr_cls))

        # run optimization
        res = getattr(opt3, method).run_opt(bounds=bounds, constraints=constraints, **kwargs_data)
        return res

    @classmethod
    def run_opt_slack(cls, kwargs_data, constraint_param_list, method, step_length=0.01, default_lower=0,
                      default_upper=1, max_try_count=10, bounds=None, constr_cls=Constraints, show_constraints=False):
        """
        run_opt_slack, run optimization with slack
        给定优化参数方法，使用opt3模块中的对应的优化方法进行优化，如果不成功，则使用slack方法进行优化，直到达到指定的最大尝试次数或者最大优先等级

        :param kwargs_data:
        :param constraint_param_list:
        :param method:
        :param step_length:
        :param default_lower:
        :param default_upper:
        :param max_try_count:
        :param bounds:
        :param constr_cls:
        :param show_constraints:
        :return:
        """
        global __current_priority__
        global __max_try_count__

        __first_time__ = True
        __current_priority__ = 1
        funcs, kwargs, priorities, constraint_types = zip(*constraint_param_list)
        max_priority = max(priorities)
        active_slack = max_priority != 0

        res = cls.run_opt_single(kwargs_data, constraint_param_list, method, step_length=step_length, bounds=bounds,
                                 default_lower=default_lower, default_upper=default_upper, constr_cls=constr_cls)

        cls.switch_first_time()
        if active_slack:
            count = 0
            while not res.success and count < max_try_count:
                # cls.increase_max_try_count()
                res = cls.run_opt_single(kwargs_data, constraint_param_list, method, step_length=step_length,
                                         bounds=bounds,
                                         default_lower=default_lower, default_upper=default_upper,
                                         constr_cls=constr_cls)
                if count >= max_try_count:
                    warnings.warn('max try count reached! will improve priority level')
                    count = 0
                    if cls.get_current_priority() > max_priority:
                        warnings.warn('max priority reach! will end automatically!')
                        break
                    else:
                        cls.increase_priority_level()
                else:
                    count += 1
            if show_constraints:
                return res, constraint_param_list
            else:
                return res
        else:
            return res


if __name__ == '__main__':
    pass

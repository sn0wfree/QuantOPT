# coding=utf-8
import unittest

import pandas as pd

from QuantOPT.constraints.relaxer import RunOpt

quote = pd.read_csv('F:\\Data\\quote\\2021.csv')
stack_price = quote.pivot_table(index='trade_dt', columns='s_info_windcode', values='s_dq_adjclose')
stockpool = quote['s_info_windcode'].unique().tolist()[:10]

cov_price = stack_price[stockpool].pct_change(1).cov()


class MyTestCaseMinVar(unittest.TestCase):
    def test_main_entry_no_instance(self):
        kwargs_data = {}
        kwargs_data['stockpool'] = stockpool
        kwargs_data['sigma2'] = cov_price
        constraint_param_list = []
        Ro = RunOpt
        result = Ro.run_opt_single(kwargs_data, constraint_param_list, 'MinVar')
        self.assertEqual(result.success, True)  # add assertion here

    def test_main_entry_instance(self):
        from QuantOPT.constraints.relaxer import RunOpt

        constraint_param_list = []
        Ro = RunOpt(method='MinVar', stockpool=stockpool, sigma2=cov_price)
        result = Ro.run_opt(constraint_param_list, slack=False)
        self.assertEqual(result.success, True)  # add assertion here

    def test_instance_constraint(self):
        from QuantOPT.constraints.relaxer import RunOpt
        # add the count of weight value which is greater than 0 should be 5 or more constraints!
        constraint_param_list = [('general_count_lower_rc', {'bound_value': 5}, 1, 'ineq')]
        Ro = RunOpt(method='MinVar', stockpool=stockpool, sigma2=cov_price)
        result = Ro.run_opt(constraint_param_list, slack=False)
        self.assertEqual(result.success, True)  # add assertion here

    def test_instance_constraint_slack(self):
        from QuantOPT.constraints.relaxer import RunOpt
        # add the count of weight value which is greater than 0 should be 5 or more constraints!
        constraint_param_list = [('general_count_lower_rc', {'bound_value': 20}, 1, 'ineq')]
        Ro = RunOpt(method='MinVar', stockpool=stockpool, sigma2=cov_price)
        result = Ro.run_opt(constraint_param_list, slack=True)
        self.assertEqual(result.success, True)  # add assertion here


if __name__ == '__main__':
    unittest.main()

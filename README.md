# QuantOPT


## Description

This module is to create and run optimizer for the portfolio optimization. 
it will have constraints with soft slack version and objects 

main functions:
1. RunOpt, main functions with slack constraints path
2. create_constraints_holder, the creator for custom constraints with string
3. Holder, model holder which can be defined by custom or new model




## Usage

```python
from QuantOPT.constraints.relaxer import RunOpt
from QuantOPT.constraints.constraints import create_constraints_holder
from QuantOPT.core.model_core import Holder
import numpy as np
## add model
class risk_budge: 
    @staticmethod
    def loss_func(w):
        return np.sum(w)
Holder.add_model('risk_budge',risk_budge)

cov_price= stock_price.pct_change(1).cov()

stock_pool = len(cov_price.columns)

## init constraints
setting_yaml_path = './constraints.yaml'
constr_cls = create_constraints_holder(setting_yaml_path)
method = 'MinVar'

Ropt = RunOpt(method=method, constr_cls=constr_cls)

constraint_param_list = [('general_count_lower_rc', {'bound_value': 5}, 1, 'ineq')]
res = Ropt.run_opt(constraint_param_list, slack=True,stockpool=stock_pool, sigma2=cov_price)



```
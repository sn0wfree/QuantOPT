# coding=utf-8
import importlib
import os
from glob import glob

from QuantOPT import models
from QuantOPT.core.base import _SimpleOpt
from QuantOPT.utils.singleton import singleton

MODELS_PATH = models.__path__[0]


# __all__ = ['_SimpleOpt', 'MinVar', 'MaxRiskAdjReturn', 'MaxIR']


@singleton
class Models(object):
    # MinVar = MinVar
    # MaxRiskAdjReturn = MaxRiskAdjReturn
    # MaxIR = MaxIR
    _SimpleOpt = _SimpleOpt

    def __init__(self, *args, **kwargs):
        self.load_model_from_path(MODELS_PATH, py_pattern='model_*.py')

    @classmethod
    def load_model_from_path(cls, models_path: str, py_pattern: str = 'model_*.py'):
        for x in glob(os.path.join(models_path, py_pattern)):
            model_name = os.path.basename(x)[6:-3]
            module_name = os.path.basename(x)[:-3]
            model_path = x
            # print(model_path, model_name)

            spec = importlib.util.spec_from_file_location(module_name, model_path)
            modulevar = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(modulevar)
            cls_obj = getattr(modulevar, model_name)
            cls.add_model(model_name, cls_obj)

    @classmethod
    def add_model(cls, name: str, model):
        setattr(cls, name, model)


Holder = Models()
if __name__ == '__main__':
    pass

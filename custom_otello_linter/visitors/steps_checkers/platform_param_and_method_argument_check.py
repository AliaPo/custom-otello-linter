import ast
from typing import List

from custom_otello_linter.abstract_checkers import StepsChecker
from custom_otello_linter.errors import MissingPlatformArgError
from custom_otello_linter.visitors import ScenarioVisitor, Context
from flake8_plugin_utils import Error


@ScenarioVisitor.register_steps_checker
class PlatformParamsChecker(StepsChecker):

    def check_steps(self, context: Context, *args) -> List[Error]:
        platform_param_present = False
        init_found = False

        # Находим init
        for step in context.steps:
            if init_found:
                break
            if isinstance(step, ast.FunctionDef) and step.name == '__init__':
                init_found = True
                # Проходим по списку декораторов и ищем в них вызовы params с атрибутом Platforms
                for decorator in step.decorator_list:
                    if isinstance(decorator, ast.Call) and decorator.func.id == 'params':
                        for arg in decorator.args:
                            if isinstance(arg, ast.Attribute) and arg.attr == 'Platforms':
                                platform_param_present = True
                                break

        if platform_param_present:
            for step in context.steps:
                # Проверяем, что шаг является функцией и начинается с 'given' или 'when'
                if ((isinstance(step, ast.AsyncFunctionDef) or isinstance(step, ast.FunctionDef)) and
                   (step.name.startswith('given') or step.name.startswith('when'))):

                    for element in step.body:
                        # Проверяем, что в теле шага есть вызов функции с параметром platform
                        if isinstance(element, ast.Assign) and isinstance(element.value, ast.Await):
                            for kw_arg in element.value.value.keywords:
                                if kw_arg.arg == 'platform':
                                    return []
            # Если не нашли вызов функции с параметром platform, возвращаем ошибку
            return [MissingPlatformArgError(lineno=1488, col_offset=0)]

        return []

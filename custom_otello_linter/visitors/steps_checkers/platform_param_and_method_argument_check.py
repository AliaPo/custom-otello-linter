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

                    # Для декораторов вида "@params[allure_labels(AllureID('808960'))](Platforms.MOBILE)"
                    if isinstance(decorator.func, ast.Subscript):
                        params_attr = decorator.func.value.id
                    # Для декораторов вида "@params(Platforms.MOBILE)"
                    else:
                        params_attr = decorator.func.id

                    if params_attr == 'params':
                        for arg in decorator.args:
                            if (
                                    isinstance(arg, ast.Attribute)
                                    and isinstance(arg.value, ast.Name)
                                    and arg.value.id == 'Platforms'
                            ):
                                platform_param_present = True
                                break

        if platform_param_present:
            for step in context.steps:
                # Проверяем, что шаг является функцией и начинается с 'given' или 'when'
                if (
                        (isinstance(step, ast.AsyncFunctionDef) or isinstance(step, ast.FunctionDef))
                        and (step.name.startswith('given') or step.name.startswith('when'))
                ):
                    # Среди действий в шаге ищем присвоение с await методом, например:
                    # self.page = await opened_dashboard()
                    for element in ast.walk(step):
                        if (
                                isinstance(element, ast.Assign)
                                and isinstance(element.value, ast.Await)
                                and isinstance(element.value.value, ast.Call)
                        ):
                            # Проверяем, что в теле шага есть вызов функции с keyword параметром platform
                            for kw_arg in element.value.value.keywords:
                                if kw_arg.arg == 'platform':
                                    return []
                            # Если не нашли keyword = platform, проверяем наличие позиционного аргумента
                            for param in ast.walk(element.value):
                                # Ищем атрибут без вложенности, только self.platform
                                if isinstance(param, ast.Attribute) and isinstance(param.value, ast.Name):
                                    if param.value.id == 'self' and param.attr == 'platform':
                                        return []

            # Если не нашли вызов функции с параметром platform, возвращаем ошибку
            return [MissingPlatformArgError(lineno=0, col_offset=0)]

        return []

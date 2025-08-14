import ast

from custom_otello_linter.visitors import Context


def get_init_step(context: Context) -> ast.FunctionDef | None:
    """
    Ищет метод __init__ в сценарии
    """
    for step in context.steps:
        if isinstance(step, ast.FunctionDef) and step.name == '__init__':
            return step


def is_platform_param_present(init_step: ast.FunctionDef) -> bool:
    """
    Проходит по списку декораторов и ищет в них вызовы params с атрибутом Platforms
    """

    def is_platforms_in_decorator(dec: ast.Call) -> bool:
        # Ищем Platforms в аргументах декоратора params
        for arg in dec.args:
            if (
                    isinstance(arg, ast.Attribute)
                    and isinstance(arg.value, ast.Name)
                    and arg.value.id == 'Platforms'
            ):
                return True
        return False

    for decorator in init_step.decorator_list:
        if isinstance(decorator, ast.Call):
            match decorator:
                # Для декораторов вида "@params[allure_labels(AllureID('808960'))](Platforms.MOBILE)"
                case ast.Call(func=ast.Subscript(value=ast.Name(id='params'))):
                    return is_platforms_in_decorator(decorator)
                # Для декораторов вида "@params(Platforms.MOBILE)"
                case ast.Call(func=ast.Name(id='params')):
                    return is_platforms_in_decorator(decorator)

    return False

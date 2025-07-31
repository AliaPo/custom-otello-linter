from flake8_plugin_utils import assert_error, assert_not_error

from custom_otello_linter.errors import MissingPlatformArgError
from custom_otello_linter.visitors import ScenarioVisitor
from custom_otello_linter.visitors.steps_checkers.platform_param_and_method_argument_check import PlatformParamsChecker


def test_scenario_with_platform_param_used():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(PlatformParamsChecker)
    code = """
    class Scenario(vedro.Scenario):

        @params(Platforms.DESKTOP)
        @params(Platforms.MOBILE)
        def __init__(self, platform):
            pass

        def given_opened_page(self):
            self.page = open_page(booking=self.booking, platform=self.platform)
    """
    assert_not_error(ScenarioVisitor, code)


def test_scenario_with_platform_param_not_used():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(PlatformParamsChecker)
    code = """
    class Scenario(vedro.Scenario):

        @params(Platforms.DESKTOP)
        @params(Platforms.MOBILE)
        def __init__(self, platform):
            pass

        def given_opened_page(self):
            self.page = open_page(booking=self.booking)
    """
    assert_error(ScenarioVisitor, code, MissingPlatformArgError)

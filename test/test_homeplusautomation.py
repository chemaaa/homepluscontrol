from homepluscontrol import (
    homeplusinteractivemodule,
    homeplusautomation,
    homeplusmodule,
)


# Light Module Tests
def test_automation_module_url(test_automation):
    assert (
        test_automation.statusUrl
        == "https://api.developer.legrand.com/hc/api/v1.0/automation/automation/addressLocation/plants/mock_plant_1/modules/parameter/id/value/module_id_5"
    )


def test_automation_module_str(test_automation):
    module_str = "Home+ Automation Module: device->Automation, name->Automation Module 1, id->module_id_5, reachable->False, level->None"
    assert test_automation.__str__() == module_str

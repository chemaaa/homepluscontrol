from homepluscontrol import (
    homeplusmodule,
)


# Base Module Tests
def test_base_module_str(test_module):
    module_str = (
        "Home+ Module: device->Base Module, name->Test Module 1, id->module_id, reachable->False, bridge->00:11:22:33:44:55"
    )
    assert test_module.__str__() == module_str


def test_base_update_status(async_mock_plant):
    mock_plant, loop = async_mock_plant
    mock_module = mock_plant.modules["0000000587654321fedcba"]

    status_result = loop.run_until_complete(mock_module.get_status_update())
    assert isinstance(mock_module, homeplusmodule.HomePlusModule)
    assert status_result["reachable"]
    assert status_result["fw"] is not None

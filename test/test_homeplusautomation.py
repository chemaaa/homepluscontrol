from unittest.mock import patch

from homepluscontrol.homeplusautomation import HomePlusAutomation


# Automation Module Tests
def test_automation_module_str(test_automation):
    module_str = "Home+ Automation Module: device->Automation, name->Automation Module 1, id->module_id_5, reachable->False, level->None, bridge->00:11:22:33:44:55"
    assert test_automation.__str__() == module_str


def test_automation_read_status(async_mock_plant):
    mock_plant, loop = async_mock_plant

    mock_automation = mock_plant.modules["aa:34:56:78:90:00:0c:dd"]
    assert mock_automation.device == "automation"
    assert mock_automation.name == "Volet Cuisine"
    assert mock_automation.hw_type == "NBR"
    assert mock_automation.level == HomePlusAutomation.OPEN_FULL
    assert mock_automation.reachable
    assert mock_automation.fw == 59

    mock_automation = mock_plant.modules["aa:88:99:43:18:1f:09:76"]
    assert mock_automation.device == "automation"
    assert mock_automation.name == "Volet Chambre"
    assert mock_automation.hw_type == "NBR"
    assert mock_automation.level == HomePlusAutomation.CLOSED_FULL
    assert mock_automation.reachable
    assert mock_automation.fw == 57


def test_automation_high_level(async_mock_plant, mock_automation_post):
    mock_plant, loop = async_mock_plant
    mock_automation = mock_plant.modules["aa:88:99:43:18:1f:09:76"]

    for invalid_level in [101, 1000, 100.1, 901]:
        with patch(
            "homepluscontrol.homeplusautomation.HomePlusAutomation.post_status_update",
            return_value=mock_automation_post,
        ) as mock_post:
            loop.run_until_complete(mock_automation.set_level(invalid_level))

        assert len(mock_post.mock_calls) == 1
        assert mock_automation.level == HomePlusAutomation.OPEN_FULL


def test_automation_low_level(async_mock_plant, mock_automation_post):
    mock_plant, loop = async_mock_plant
    mock_automation = mock_plant.modules["aa:88:99:43:18:1f:09:76"]

    for invalid_level in [-2, -1.01, -999, -0.1]:
        with patch(
            "homepluscontrol.homeplusautomation.HomePlusAutomation.post_status_update",
            return_value=mock_automation_post,
        ) as mock_post:
            loop.run_until_complete(mock_automation.set_level(invalid_level))

        assert len(mock_post.mock_calls) == 1
        assert mock_automation.level == HomePlusAutomation.CLOSED_FULL

    # Test for the special -1 case
    with patch(
        "homepluscontrol.homeplusautomation.HomePlusAutomation.post_status_update",
        return_value=mock_automation_post,
    ) as mock_post:
        loop.run_until_complete(mock_automation.set_level(-1))

    assert len(mock_post.mock_calls) == 1
    assert mock_automation.level == 0  # Value returned by mock "get_status_update" request


def test_automation_open(async_mock_plant, mock_automation_post):
    mock_plant, loop = async_mock_plant
    mock_automation = mock_plant.modules["aa:88:99:43:18:1f:09:76"]

    assert mock_automation.level == HomePlusAutomation.CLOSED_FULL  # Automation is closed

    with patch(
        "homepluscontrol.homeplusautomation.HomePlusAutomation.post_status_update",
        return_value=mock_automation_post,
    ) as mock_post:
        loop.run_until_complete(mock_automation.open())

    assert len(mock_post.mock_calls) == 1
    assert mock_automation.level == HomePlusAutomation.OPEN_FULL


def test_automation_close(async_mock_plant, mock_automation_post):
    mock_plant, loop = async_mock_plant
    mock_automation = mock_plant.modules["aa:34:56:78:90:00:0c:dd"]

    assert mock_automation.level == HomePlusAutomation.OPEN_FULL  # Automation is open

    with patch(
        "homepluscontrol.homeplusautomation.HomePlusAutomation.post_status_update",
        return_value=mock_automation_post,
    ) as mock_post:
        loop.run_until_complete(mock_automation.close())

    assert len(mock_post.mock_calls) == 1
    assert mock_automation.level == HomePlusAutomation.CLOSED_FULL


def test_automation_stop(async_mock_plant, mock_automation_post):
    mock_plant, loop = async_mock_plant
    mock_automation = mock_plant.modules["aa:88:99:43:18:1f:09:76"]

    assert mock_automation.level == HomePlusAutomation.CLOSED_FULL  # Automation is closed

    with patch(
        "homepluscontrol.homeplusautomation.HomePlusAutomation.post_status_update",
        return_value=mock_automation_post,
    ) as mock_post:
        loop.run_until_complete(mock_automation.open())

    # Automation "starts" to open - the level value is assumed to be the final requested level
    assert len(mock_post.mock_calls) == 1
    assert mock_automation.level == HomePlusAutomation.OPEN_FULL

    # But while closing, we issue the stop command - so the final level value has to be read from the API
    with patch(
        "homepluscontrol.homeplusautomation.HomePlusAutomation.post_status_update",
        return_value=mock_automation_post,
    ) as mock_post:
        loop.run_until_complete(mock_automation.stop())

    assert len(mock_post.mock_calls) == 1
    assert mock_automation.level == 0  # Value returned by mock "get_status_update" request

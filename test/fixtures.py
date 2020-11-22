# Text fixtures

def plant_data():
    return """
    {
    "plants": [
        {
            "id": "123456789009876543210",
            "name": "My Home",
            "country": "ES"
        }
    ]
    }"""

def plant_topology():
    return """
    {
    "plant": {
        "id": "123456789009876543210",
        "ambients": [
            {
                "id": "000000012345678fedcba",
                "name": "Kitchen",
                "type": "kitchen",
                "modules": [
                    {
                        "id": "0000000987654321fedcba",
                        "name": "Kitchen Wall Outlet",
                        "hw_type": "NLP",
                        "type": "other",
                        "device": "plug"
                    }
                ]
            },
            {
                "id": "000000032345678fedcba",
                "name": "Master Bedroom",
                "type": "bedroom",
                "modules": [
                    {
                        "id": "0000000887654321fedcba",
                        "name": "Bedroom Wall Outlet",
                        "hw_type": "NLP",
                        "type": "other",
                        "device": "plug"
                    }
                ]
            },
            {
                "id": "000000042345678fedcba",
                "name": "Living Room",
                "type": "livingroom",
                "modules": [
                    {
                        "id": "0000000787654321fedcba",
                        "name": "Living Room Ceiling Light",
                        "hw_type": "NLF",
                        "device": "light"
                    }
                ]
            },
            {
                "id": "000000052345678fedcba",
                "name": "Dining Room",
                "type": "dining_room",
                "modules": [
                    {
                        "id": "0000000687654321fedcba",
                        "name": "Dining Room Ceiling Light",
                        "hw_type": "NLF",
                        "device": "light"
                    },
                    {
                        "id": "0000000587654321fedcba",
                        "name": "Dining Room Wall Outlet",
                        "hw_type": "NLP",
                        "type": "other",
                        "device": "plug"
                    }
                ]
            }
        ],
        "modules": [
            {
                "id": "000000012345678abcdef",
                "name": "General Command",
                "hw_type": "NLT",
                "device": "remote"
            },
            {
                "id": "000000022345678abcdef",
                "name": "Wall Switch 1",
                "hw_type": "NLT",
                "device": "remote"
            },
            {
                "id": "000000032345678abcdef",
                "name": "Wall Switch 2",
                "hw_type": "NLT",
                "device": "remote"
            }
        ]
    }
    }   
    """

def plant_modules():
    return """
    {
    "modules": {
        "lights": [
            {
                "reachable": true,
                "status": "off",
                "fw": 46,
                "consumptions": [
                    {
                        "unit": "watt",
                        "value": 0,
                        "timestamp": "2020-11-22T11:03:05+00:00"
                    }
                ],
                "sender": {
                    "plant": {
                        "module": {
                            "id": "0000000787654321fedcba"
                        }
                    }
                }
            },
            {
                "reachable": true,
                "status": "off",
                "fw": 46,
                "consumptions": [
                    {
                        "unit": "watt",
                        "value": 0,
                        "timestamp": "2020-11-22T11:03:05+00:00"
                    }
                ],
                "sender": {
                    "plant": {
                        "module": {
                            "id": "0000000687654321fedcba"
                        }
                    }
                }
            }
        ],
        "plugs": [
            {
                "reachable": true,
                "status": "on",
                "consumptions": [
                    {
                        "unit": "watt",
                        "value": 0,
                        "timestamp": "2020-11-22T11:03:05+00:00"
                    }
                ],
                "sender": {
                    "plant": {
                        "module": {
                            "id": "0000000987654321fedcba"
                        }
                    }
                },
                "fw": 42
            },
            {
                "reachable": true,
                "status": "on",
                "consumptions": [
                    {
                        "unit": "watt",
                        "value": 0,
                        "timestamp": "2020-11-22T11:03:05+00:00"
                    }
                ],
                "sender": {
                    "plant": {
                        "module": {
                            "id": "0000000887654321fedcba"
                        }
                    }
                },
                "fw": 42
            },
            {
                "reachable": true,
                "status": "on",
                "consumptions": [
                    {
                        "unit": "watt",
                        "value": 0,
                        "timestamp": "2020-11-22T11:03:05+00:00"
                    }
                ],
                "sender": {
                    "plant": {
                        "module": {
                            "id": "0000000587654321fedcba"
                        }
                    }
                },
                "fw": 42
            }
        ],
        "automations": [],
        "energymeters": [],
        "remotes": [
            {
                "reachable": false,
                "battery": "full",
                "sender": {
                    "plant": {
                        "module": {
                            "id": "000000012345678abcdef"
                        }
                    }
                },
                "fw": 36
            },
            {
                "reachable": true,
                "battery": "full",
                "sender": {
                    "plant": {
                        "module": {
                            "id": "000000022345678abcdef"
                        }
                    }
                },
                "fw": 36
            },
            {
                "reachable": true,
                "battery": "full",
                "sender": {
                    "plant": {
                        "module": {
                            "id": "000000032345678abcdef"
                        }
                    }
                },
                "fw": 36
            }
        ],
        "heaters": []
    }
    }
    """

def plug_status():
    return """
    {
    "plugs": [
        {
            "reachable": true,
            "status": "on",
            "consumptions": [
                {
                    "unit": "watt",
                    "value": 0,
                    "timestamp": "2020-11-22T11:14:14+00:00"
                }
            ],
            "sender": {
                "plant": {
                    "module": {
                        "id": "0000000587654321fedcba"
                    }
                }
            },
            "fw": 42
        }
    ]
}
    """

def light_status():
    return """
    {
    "lights": [
        {
            "reachable": true,
            "status": "off",
            "fw": 46,
            "consumptions": [
                {
                    "unit": "watt",
                    "value": 0,
                    "timestamp": "2020-11-22T11:26:24+00:00"
                }
            ],
            "sender": {
                "plant": {
                    "module": {
                        "id": "0000000787654321fedcba"
                    }
                }
            }
        }
    ]
    }
    """

def remote_status():
    return """
    {
    "remotes": [
        {
            "reachable": false,
            "battery": "full",
            "sender": {
                "plant": {
                    "module": {
                        "id": "000000012345678abcdef"
                    }
                }
            },
            "fw": 36
        }
    ]
    }
    """
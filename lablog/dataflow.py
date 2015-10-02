energy = {
    "name":"Energy",
    "nodes":[
        "Energy Gateway",
        "Home Energy Monitor",
        "Universal Power Supply"
    ],
    "data":[
        "Power",
        "Received",
        "Delivered",
        "Price",
        "Amps",
        "Voltage",
        "Current",
    ]
}

presence = {
    "name":"Presence",
    "nodes":[
        "Presence"
    ],
    "data":[
        "Presence"
    ]
}

air_quality = {
    "name": "Air Quality",
    "nodes":[
        "Sensor Node",
        "Netatmo Weather Station",
        "Cube Sensors",
    ],
    "data":[
        "Temperature",
        "Humidity",
        "Light",
        "CO2",
        "Sound",
        "VOC"
    ]
}

weather = {
    "name":"Weather",
    "nodes":[
        "Wunderground"
    ],
    "data":[
        'UV',
        'Dew Point',
        'Feels Like',
        'Heat Index',
        'Precipitation',
        'Pressure'
        'Humidity',
        'Solar Radiation',
        'Temperature',
        'Visibility',
        'Wind Direction',
        'Wind Gust',
        'Wind Speed',
        'Wind Chill'
    ]
}

triggers = [
    "Presence",
    "CO2",
]


exchanges = [
    energy,
    presence,
    air_quality,
    weather
]

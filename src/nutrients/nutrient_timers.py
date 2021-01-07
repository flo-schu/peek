from speech_timer import Timer

nitrite = {
    10:"start",
    30:"shake",
    60:"done"
}

phosphate = {
    0:"start",
    15: "schütteln",
    35: "schütteln",
    45: "messen",
    60: "60",
    90: "30",
    110: "10",
    120: ""
}


# 4 flasks at the same time
nitrate_b = {
    0: "5 tropfen",
    10: "schütteln dann pulver",
    30: "1 minute schütteln",
    90: "stop",
    100: "5 tropfen",
    110: "schütteln dann pulver",
    130: "1 minute schütteln",
    190: "stop",
    200: "5 tropfen",
    210: "schütteln dann pulver",
    230: "1 minute schütteln",
    290: "stop",
    300: "messung 1",
    390: "10",
    400: "messung 2",
    490: "10",
    500: "messung 3",
    590: "10",
    600: "",
}

nitrate_a = {
    0:   "5 Tropfen",
    20:  "schütteln, dann Pulver",
    45:  "eine Minute schütteln",
    75:  "30",
    95:  "10",
    105: "stop. Messen",
    130: "20",
    145: "5",
    150: "",
}

test = {
    0:"start",
    5:"test",
    10:""
}

Timer(40, nitrate_a, prep_time=10)

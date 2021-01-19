from nutrients.speech_timer import Timer

# am Anfang und am Ende können 4 Proben verarbeitet
# werden sobald das Messen anfängt auf 3 Proben reduzieren
nitrite = {
    0:   "Start. 4 Tropfen",
    25:  "Schütteln, dann Pulver",
    50:  "Schütteln, dann Warteschlange",
    60:  "Messen",
    90:  "30",
    110: "10",
    120: "",
}

# 3 gleichzeitig müsste gehen (über 1 Minute Zeit
# zum messen)
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

# 3 gleichzeitig für stressfreies messen
nitrate = {
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

# empfehlung 3 gleichzeitig für stressfreies messen
# 4 geht aber super stressig
ammonium = {
    0:   "10 Tropfen Lösung 1",
    30:  "Schütteln, dann Pulver.",
    55:  "Schütteln, dann auf Warteposition.",
    60:  "Proben von Warteposition, dann 4 Tropfen Lösung 2",
    85:  "Schütteln, dann in Messschlange",
    90:  "Messen",
    120: "30",
    140: "10",
    150: "",
}


Timer(40, phosphate, prep_time=10)


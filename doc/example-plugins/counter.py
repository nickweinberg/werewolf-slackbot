import time
crontable = []
outputs = []

crontable.append([5,"say_time"])
config = yaml.load("rtmbot.conf")

def say_time():
    #NOTE: you must add a real channel ID for this to work

    outputs.append([config["CHANNEL"], time.time()])

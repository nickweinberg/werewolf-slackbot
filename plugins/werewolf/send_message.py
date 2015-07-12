import yaml

outputs = []


def send_message(message, channel=None):
    if not channel:
        config = yaml.load(file("rtmbot.conf", "r"))
        channel = config["CHANNEL"]

    global outputs
    outputs.append([channel, message])


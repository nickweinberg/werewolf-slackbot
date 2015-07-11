import time
import random
crontable = []
outputs = []
"""
with open("data/clean_excuse.txt", "r") as ff:
    excuses = ff.readlines()
    excuses = [excuse.strip() for excuse in excuses]

def process_message(data):
    if data['channel'].startswith("D"):
        """ pick random excuse """

        if "help" in data['text']:
            # lazy bot has excuse
            new_excuse = random.choice(excuses)
            outputs.append([data['channel'], new_excuse])
        else:
            # bot hates noobs
            insult_list = ["lol noob", "l2p", "haha wow."]
            new_insult = random.choice(insult_list)
            outputs.append([data['channel'], new_insult])
"""

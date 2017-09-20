#!/usr/bin/env python3


import csv
import json
from datetime import datetime
from collections import OrderedDict

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

from config import *


def plot_db(total, chats_by_date):
    plt.figure()
    ax = plt.subplot(1, 1, 1)
    ax.plot(range(len(chats_by_date)), list(chats_by_date.values()))
    ax.set_xticks(range(len(chats_by_date)))
    ax.set_xticklabels([i[-5:] for i in chats_by_date.keys()], rotation=30, fontsize=8)
    ax.set_title("Total: %d\n%s" % (total, str(datetime.now())[0:16]))
    ax.set_ylabel("Chats")
    ax.set_xlabel("Date")
    ax.grid(True)
    plt.savefig(log_analyze_addr)


def print_db(total, chats_by_date):
    print("\033[7;1m%-10s\t%-5s\033[0m" % ("Server Date", "Chats"))
    for (date, num) in chats_by_date.items():
        print("%-10s\t%-5d" % (date, num))
    print("\033[7m%-10s\t%-5d\033[0m" % ("Total", total))


def extract_date_from_datetime_string(datetime):
    return datetime.split(" ")[0]


def main(plot=True, pretty_print=True):
    db = []
    with open(log_addr) as f:
        reader = csv.DictReader(f, fieldnames=["datetime", "caht_id", "action"], delimiter="\t")
        for row in reader:
            db.append(dict(row))

    chat_ids = {i["caht_id"] for i in db}

    chat_ids_by_date = OrderedDict()
    for i in db:
        if extract_date_from_datetime_string(i["datetime"]) not in chat_ids_by_date.keys():
            chat_ids_by_date[extract_date_from_datetime_string(i["datetime"])] = set()
        chat_ids_by_date[extract_date_from_datetime_string(i["datetime"])].add(i["caht_id"])
    chats_by_date = OrderedDict((date, len(chat_ids)) for (date, chat_ids) in chat_ids_by_date.items())

    if pretty_print:
        print_db(len(chat_ids), chats_by_date)
    if plot:
        plot_db(len(chat_ids), chats_by_date)


if __name__ == '__main__':
    main()

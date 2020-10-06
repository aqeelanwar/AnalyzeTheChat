# Author: aqeelanwar
# Created: 14 June,2020, 12:24 AM
# Email: aqeel.anwar@gatech.edu


import os
import re
import time as T
from datetime import datetime

import numpy as np
import pandas as pd

import cv2
import emoji
import matplotlib.pyplot as plt
from matplotlib import rc

# rc("text", usetex=True)
# rc("font", family="cmr10")
GREEN_COLOR = "#A5AB81"
ORANGE_COLOR = "#DD8047"
BLUE_COLOR = "#94B6D2"
YELLOW_COLOR = "#D8B25C"


def create_folder(args):
    dt_string = str(datetime.now())
    dt_string = (
        dt_string.replace("-", "").replace(":", "").replace(" ", "").split(".")[0]
    )
    path = os.path.join(
        "results", dt_string + "_" + args.path.split(".")[0] + "_" + args.save_as
    )
    if not os.path.exists(path):
        os.mkdir(path)
    return (path, args.save_as)


def extract_emojis(s):
    emoji_count = {}
    for c in s:
        if c in emoji.UNICODE_EMOJI:
            if c in emoji_count:
                emoji_count[c] += 1
            else:
                emoji_count[c] = 1

    return emoji_count


def plot_time_circle(time, count, title, save_path):
    c = np.zeros(24)
    c[time] = count
    count = c
    f = plt.figure(figsize=(7, 7))
    ax = plt.subplot(111, projection="polar")
    x = np.arange(0, 2 * np.pi, 2 * np.pi / len(count)) + np.pi / len(count)
    max_ind = np.argmax(count)
    bars = ax.bar(
        x,
        count,
        width=2 * np.pi / len(count),
        alpha=1,
        color=GREEN_COLOR,
        # label="Time Zone: EST",
        bottom=0,
    )
    max_height = 0
    for rect in bars:
        if rect.get_height() > max_height:
            max_height = rect.get_height()
    for rect in bars:
        height = rect.get_height()
        plt.text(
            rect.get_x() + rect.get_width() / 2.0,
            0.8 * max_height,
            "%d" % int(height),
            ha="center",
            va="bottom",
        )

    ax.bar(
        x[max_ind],
        count[max_ind],
        bottom=0,
        width=2 * np.pi / len(count),
        alpha=1,
        color=ORANGE_COLOR,
    )
    ax.bar(
        x,
        np.max(count) * np.ones(len(count)),
        width=2 * np.pi / len(count),
        alpha=0.1,
        bottom=0,
        color=YELLOW_COLOR,
        edgecolor="black",
    )

    # Make the labels go clockwise
    ax.set_theta_direction(-1)
    ax.grid(False)
    ax.spines["polar"].set_visible(False)
    # # Place Zero at Top
    ax.set_theta_offset(np.pi / 2)
    # # Set the circumference ticks
    ax.set_xticks(np.linspace(0, 2 * np.pi, 24, endpoint=False))
    # set the label names
    ticks = [
        "12 AM",
        "1 AM",
        "2 AM",
        "3 AM",
        "4 AM",
        "5 AM",
        "6 AM",
        "7 AM",
        "8 AM",
        "9 AM",
        "10 AM",
        "11 AM",
        "12 PM",
        "1 PM",
        "2 PM",
        "3 PM",
        "4 PM",
        "5 PM",
        "6 PM",
        "7 PM",
        "8 PM",
        "9 PM",
        "10 PM",
        "11 PM",
    ]
    ax.set_xticklabels(ticks)
    plt.setp(ax.get_yticklabels(), visible=False)
    im = cv2.imread("images/logo_small.png")
    small = cv2.resize(im, (0, 0), fx=0.2, fy=0.2)
    small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
    height = small.shape[0]
    plt.figimage(small, 5, f.bbox.ymax - 1.4 * height)
    plt.title(title, fontdict={"fontsize": 20})
    # plt.figtext(0.3,0.3,  "Hello World !")
    footer_text = "www.aqeel-anwar.com/AnalyzeTheChat"
    plt.figtext(0.25, 0.98, footer_text)

    name = save_path[0] + "/" + title + "." + save_path[1]

    # plt_bytes = buf.getvalue()
    # buf.close()
    f.savefig(name)
    plt.close()


def plot_line(x, y, title, save_path, max_limit=0):

    f = plt.figure(figsize=(8, 5))
    if max_limit > 0:
        x = x[0:max_limit]
        y = y[0:max_limit]
    barlist = plt.plot(x, y, color=GREEN_COLOR)
    plt.title(title, fontdict={"fontsize": 20})
    # barlist[np.argmax(y)].set_color(ORANGE_COLOR)
    # for bar in barlist:
    #     yval = bar.get_height()
    #     plt.text(
    #         bar.get_x() + bar.get_width() / 2.0,
    #         1.01 * yval,
    #         int(yval),
    #         ha="center",
    #         va="bottom",
    #     )
    plt.xticks(rotation=15)
    name = save_path + "/" + title + ".png"
    f.savefig(name, bbox_inches="tight")


def plot_bar(x, y, title, save_path, max_limit=0):
    f = plt.figure(figsize=(10, 6))
    if max_limit > 0:
        x = x[0:max_limit]
        y = y[0:max_limit]

    barlist = plt.bar(x=x, height=y, color=GREEN_COLOR)
    plt.title(title, fontdict={"fontsize": 20})
    barlist[np.argmax(np.array(y))].set_color(ORANGE_COLOR)
    for bar in barlist:
        yval = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2.0,
            1.01 * yval,
            np.round(yval, 1),
            ha="center",
            va="bottom",
        )
    plt.xticks(rotation=20)
    im = cv2.imread("images/logo_small.png")
    small = cv2.resize(im, (0, 0), fx=0.2, fy=0.2)
    small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
    height = small.shape[0]
    f.figimage(small, 5, f.bbox.ymax - 1.4 * height)
    name = save_path[0] + "/" + title + "." + save_path[1]
    footer_text = "www.aqeel-anwar.com/AnalyzeTheChat"
    plt.figtext(0.25, 0.98, footer_text)
    print(name)
    # plt_bytes = buf.getvalue()
    # buf.close()
    f.savefig(name)
    plt.close()


def display_AnalyzeTheChat():
    with open("display.txt", "r") as file:
        for line in file:
            print(line, end="")

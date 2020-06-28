# Author: aqeelanwar
# Created: 15 June,2020, 4:13 AM
# Email: aqeel.anwar@gatech.edu


# Collections of analysis function
# Each function should have input and output as pandas dataframe
import pandas as pd
import emoji
import time as T
from aux_functions import *


def crawl_the_chat(chat):
    # This function crawls the .txt chat file and converts it into a pandas dataframe.
    # Each message is stored as a row in the dataframe
    # To identify messages, regular expressions are used to identify dates format
    # Depending on the user's mobile clock settings, there existing two clock patterns
    print("Crawling the chat")
    pattern_time_24hr = ", (0?[0-9]|1[0-9]|2[0-3]):([0-5][0-9])"
    pattern_time_12hr = ", (0?[0-9]|1[0-2]):([0-9]|[0-5][0-9]) [AP]M"

    pattern_date_US = "(0?[1-9]|1[0-2])/(0?[1-9]|[12][0-9]|3[01])/(\d{2}|\d{4}), "
    pattern_date_UK = "([12][0-9]|3[01]|0?[1-9])/(0?[1-9]|1[0-2])/(\d{2}|\d{4}), "

    # pattern_date_US = "(0?[1-9]|1[0-2])/(0?[1-9]|[12][0-9]|3[01])/\d\d"
    # pattern_date_UK = "([12][0-9]|3[01]|0?[1-9])/(0?[1-9]|1[0-2])/\d\d"

    day_of_week_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    data = []
    data_extended = []
    last_message_end = 0
    is_UK = False
    dp = re.compile(pattern_date_UK)
    for d in dp.finditer(chat):
        date = d.group()
        if int(date.split("/")[0]) > 12:
            pattern_date = pattern_date_UK
            is_UK = True

    if not is_UK:
        pattern_date = pattern_date_US

    if re.search(pattern_time_12hr, chat):
        pattern_time = pattern_time_12hr
    else:
        pattern_time = pattern_time_24hr

    pattern = pattern_date + pattern_time[2:]
    pattern_time = pattern_time[2:]
    p = re.compile(pattern)
    for m in p.finditer(chat):
        DateTime = m.group()
        # Split dateTime
        time = re.search(pattern_time, DateTime).group()
        date = re.search(pattern_date, DateTime).group()
        date = date[:-2]
        if is_UK:
            spp = date.split("/")
            date = spp[1] + "/" + spp[0] + "/" + spp[2]

        if len(date.split("/")[-1]) > 2:
            date_split = date.split("/")
            date = date_split[0] + "/" + date_split[1] + "/" + date_split[2][2:4]

        day_of_week = day_of_week_labels[T.strptime(date, "%m/%d/%y").tm_wday]

        if last_message_end > 0:
            contact_and_msg = chat[last_message_end + 3 : m.start()]
            split_ = contact_and_msg.split(":")
            if len(split_) > 1:
                # Msg by user
                contact = split_[0]
                msg = split_[1].split("\n")
                message = ""
                for msg_row in msg:
                    message += " " + msg_row
                message = message[2:-1]

            elif len(split_) == 1:
                # System generated message
                contact = "System Generated"
                message = split_[0].split("\n")[0]

            data.append([last_date, last_time, day_of_week, contact, message])

            date_split = last_date.split("/")
            month = np.round(int(date_split[0]), 0)
            day = np.round(int(date_split[1]))
            year = np.round(int(date_split[2]))
            time_split = last_time.split(":")
            hour = np.round(int(time_split[0]))
            min = np.round(int(time_split[1].split(" ")[0]))

            if "M" in last_time:
                # AM/PM format - Convert to 24 hr format
                AM_PM = time_split[1].split(" ")[1]
                if AM_PM == "PM":
                    hour += 12
                    if hour == 24:
                        hour = 12

                else:
                    if hour == 12:
                        hour = 0

            data_extended.append(
                [month, day, year, hour, min, day_of_week, contact, message]
            )

        last_date = date
        last_time = time

        last_message_end = m.end()

    df_simple = pd.DataFrame(
        data, columns=["Date", "Time", "DayOfWeek", "Contact", "Message"]
    )
    df_extended = pd.DataFrame(
        data_extended,
        columns=[
            "Month",
            "Day",
            "Year",
            "Hour",
            "Min",
            "DayOfWeek",
            "Contact",
            "Message",
        ],
    )
    return df_simple, df_extended


def chat_summary(df):
    total_msgs = df.shape[0]
    first_msg_date = df["Date"].iloc[0]
    last_msg_date = df["Date"].iloc[-1]
    days_active = (
        T.mktime(T.strptime(last_msg_date, "%m/%d/%y"))
        - T.mktime(T.strptime(first_msg_date, "%m/%d/%y"))
    ) / (60 * 60 * 24)

    # Remove 'System Generated' from participant's list

    if "System Generated" in df["Contact"].values:
        active_participants = df["Contact"].nunique() - 1
    else:
        active_participants = df["Contact"].nunique()

    df = pd.DataFrame(
        [
            [
                total_msgs,
                active_participants,
                first_msg_date,
                last_msg_date,
                int(days_active),
            ]
        ],
        columns=[
            "Total Messages",
            "Active Participants",
            "First Message Date",
            "Last Message Date",
            "Days Active",
        ],
    )
    print_summary(df)
    return df


def print_summary(df):
    print("------------------- Summary -------------------")
    values = df.values.tolist()[0]
    columns = df.columns

    for col, val in zip(columns, values):
        print("{:<25} : {:<9}".format(col, val))


def daily_msgs(df, plot=False):
    grouped = df.groupby("Date", as_index=False)["Contact"]
    df_ = grouped.count()
    df_.columns = ["Date", "Count"]
    if plot:
        plot_line(x=df_["Date"], y=df_["Count"], title="Daily Messages")

    return df_


def msgs_per_hour(df, save_path, plot=False):
    grouped = df.groupby("Hour", as_index=False)["Contact"]
    df_ = grouped.count()
    df_.columns = ["Hour", "Count"]
    if plot:
        plot_time_circle(
            df_["Hour"],
            df_["Count"],
            title="Number of Messages per Hour",
            save_path=save_path,
        )
    return df_


def msgs_per_weekday(
    df, save_path, sort=False, plot=False,
):
    grouped = df.groupby("DayOfWeek", as_index=False)["Contact"]
    df_ = grouped.count()
    df_.columns = ["DayOfWeek", "Count"]
    if sort:
        df_.sort_values(by=["Count"], inplace=True, ascending=False)
    if plot:
        plot_bar(
            x=df_["DayOfWeek"],
            y=df_["Count"],
            title="Messages per Weekday",
            save_path=save_path,
        )
    return df_


def msgs_per_month(df, save_path, sort=False, plot=False):
    grouped = df.groupby("Month", as_index=False)["Contact"]

    df_ = grouped.count()
    df_.columns = ["Month", "Count"]

    if sort:
        df_.sort_values(by=["Count"], inplace=True, ascending=False)

    if plot:
        plot_bar(
            x=df_["Month"].astype(str),
            y=df_["Count"],
            title="Messages per month",
            save_path=save_path,
        )
    return df_


def msgs_per_year(df, save_path, sort=False, plot=False):
    grouped = df.groupby("Year", as_index=False)["Contact"]
    df_ = grouped.count()
    df_.columns = ["Year", "Count"]

    if sort:
        df_.sort_values(by=["Count"], inplace=True, ascending=False)

    if plot:
        plot_bar(
            x=df_["Year"].astype(str),
            y=df_["Count"],
            title="Messages per year",
            save_path=save_path,
        )
    return df_


def emojis_per_user(df, save_path, sort=False, plot=False):
    grouped = df.groupby("Contact", as_index=False)
    df_list = []
    for name, group in grouped:
        emoji_count = 0
        msgs = group["Message"].str.split(" ")
        for m in msgs:
            if any(x in m for x in emoji.UNICODE_EMOJI):
                emoji_count += 1
        df_list.append([name, emoji_count])

    df_ = pd.DataFrame(df_list, columns=["Contact", "WordCount"])
    if sort:
        df_.sort_values(by=["WordCount"], inplace=True, ascending=False)
    if plot:
        plot_bar(
            x=df_["Contact"],
            y=df_["WordCount"],
            title="Emojis per User",
            save_path=save_path,
            max_limit=15,
        )
    return df_


def msgs_per_contact(df, save_path, sort=False, plot=False):
    grouped = df.groupby("Contact", as_index=False)["Hour"]
    df_ = grouped.count()
    df_.columns = ["Contact", "Count"]

    if sort:
        df_.sort_values(by=["Count"], inplace=True, ascending=False)

    if plot:
        plot_bar(
            x=df_["Contact"],
            y=df_["Count"],
            title="Messages per contact",
            save_path=save_path,
            max_limit=15,
        )

    return df_


def words_per_contact(df, save_path, sort=False, plot=False):
    grouped = df.groupby("Contact", as_index=False)
    d = []
    for name, group in grouped:
        msg_count = group["Message"].str.split(" ").apply(len).sum()
        d.append([name, msg_count])

    df_ = pd.DataFrame(d, columns=["Contact", "WordCount"])

    if sort:
        df_.sort_values(by=["WordCount"], inplace=True, ascending=False)

    if plot:
        plot_bar(
            x=df_["Contact"],
            y=df_["WordCount"],
            title="Words per contact",
            save_path=save_path,
            max_limit=15,
        )
    return df_


def this_word_per_contact(
    df, check_word, case_sensitive=False, save_path="", sort=False, plot=False
):

    word_list = []
    for w in check_word:
        word_list.append(w)
        word_list.append(w.lower())
        word_list.append(w.upper())
        word_list.append(w.capitalize())
    grouped = df.groupby("Contact", as_index=False)
    df_list = []
    for name, group in grouped:
        word_count = 0
        msgs = group["Message"].str.split(" ")
        for m in msgs:
            if any(x in m for x in word_list):
                word_count += 1
        df_list.append([name, word_count])

    df_ = pd.DataFrame(df_list, columns=["Contact", "WordCount"])
    if sort:
        df_.sort_values(by=["WordCount"], inplace=True, ascending=False)

    if plot:
        title = "Number of -" + check_word[0] + "- per contact"
        plot_bar(
            x=df_["Contact"],
            y=df_["WordCount"],
            title=title,
            save_path=save_path,
            max_limit=15,
        )

    return df_


def average_words_per_message_per_contact(df, save_path, sort=False, plot=False):
    df_words = words_per_contact(df, save_path, sort=False, plot=False)
    df_msgs = msgs_per_contact(df, save_path, sort=False, plot=False)

    df_words.set_index("Contact", inplace=True)
    df_msgs.set_index("Contact", inplace=True)

    df_words["Count"] = df_words["WordCount"] / df_msgs["Count"]
    del df_words["WordCount"]
    df_ = df_words
    df_.reset_index(inplace=True)
    if sort:
        df_.sort_values(by=["Count"], inplace=True, ascending=False)

    if plot:
        plot_bar(
            x=df_["Contact"],
            y=df_["Count"],
            title="Average words per message",
            save_path=save_path,
            max_limit=15,
        )

    return df_


def media_per_contact(df, save_path, sort=False, plot=False):
    df_ = this_word_per_contact(
        df, check_word=["<Media", "omitted>"], save_path=save_path, sort=sort, plot=plot
    )
    return df_


def emojis_per_msg_per_contact(df, save_path, sort=False, plot=False):
    df_emojis = emojis_per_user(df, save_path, sort=False, plot=False)
    df_msgs = msgs_per_contact(df, save_path, sort=False, plot=False)

    df_emojis.set_index("Contact", inplace=True)
    df_msgs.set_index("Contact", inplace=True)

    df_emojis["Count"] = df_emojis["WordCount"] / df_msgs["Count"]
    del df_emojis["WordCount"]
    df_ = df_emojis
    df_.reset_index(inplace=True)
    if sort:
        df_.sort_values(by=["Count"], inplace=True, ascending=False)

    if plot:
        plot_bar(
            x=df_["Contact"],
            y=df_["Count"],
            title="Average number of emojis per message",
            save_path=save_path,
            max_limit=15,
        )

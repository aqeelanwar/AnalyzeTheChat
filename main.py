# Author: aqeelanwar
# Created: 13 June,2020, 9:42 PM
# Email: aqeel.anwar@gatech.edu


from analysis_functions import *
import argparse
from aux_functions import display_AnalyzeTheChat


# Command-line input setup
parser = argparse.ArgumentParser(
    description="AnalyzeTheChat - Analyze your WhatsApp chat"
)
parser.add_argument(
    "--path",
    type=str,
    default="",
    help="Path to the .txt file exported from WhatsApp",
)
parser.add_argument(
    "--keyword",
    type=str,
    default="",
    help="Path to the .txt file exported from WhatsApp",
)

parser.add_argument(
    "--save_as",
    type=str,
    choices=["pdf", "png", "jpg"],
    default="pdf",
    help="Format of the results saved",
)


def process_chat(file_path):

    args = parser.parse_args()
    args.path = file_path

    chat = open(args.path, mode="r")
    chat = chat.read()
    st = T.time()
    df, df_extended = crawl_the_chat(chat)
    save_path = create_folder(args)
    df_summary = chat_summary(df)
    # print('------------------- Summary -------------------')
    print("-------------- Generating Graphs --------------")
    df_media = media_per_contact(df, save_path, sort=True, plot=True)
    df_daily_msgs = daily_msgs(df)
    average_words_per_message_per_contact(df_extended, save_path, sort=True, plot=True)
    _ = msgs_per_weekday(df_extended, save_path, sort=True, plot=True)
    _ = msgs_per_hour(df_extended, save_path, plot=True)
    _ = msgs_per_month(df_extended, save_path, plot=True)
    df_msgs_per_year = msgs_per_year(df_extended, save_path, sort=False, plot=True)
    df_emojis_per_user = emojis_per_user(df, save_path, sort=True, plot=True)
    df_msgs_per_contact = msgs_per_contact(df_extended, save_path, sort=True, plot=True)
    df_words_per_contact = words_per_contact(
        df_extended, save_path, sort=True, plot=True
    )

    df_emojis_per_msg_per_contact = emojis_per_msg_per_contact(
        df_extended, save_path, sort=True, plot=True
    )
    if args.keyword != '':
        df_this_word_per_contact = this_word_per_contact(
            df_extended,
            check_word=[args.keyword],
            save_path=save_path,
            sort=True,
            plot=True,
        )

    print("----------------- Time Spent ------------------")
    print("Time spent: ", np.round(T.time() - st, 2), "secs")


if __name__ == "__main__":
    args = parser.parse_args()
    display_AnalyzeTheChat()
    process_chat(args.path)

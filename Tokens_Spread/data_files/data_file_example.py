import os
import re


BOT_TOKEN = "<insert_your_bot_token>"

dir_path = os.path.dirname(os.path.realpath(__file__))
dir_database = dir_path.replace("/data_files", "/database")
dir_json_files = re.sub("Tokens_Spread.*", "Tokens_Spread/json_files", dir_path)

exchange_cex_list = []
exchange_dex_list = []
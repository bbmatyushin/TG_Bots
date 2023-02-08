from database.sqlite_create import CreateDatabase
from parsing.parser import MainParser
from data_files.useful_tools import UsefulTools

import json


class SelectQuery(CreateDatabase):
    def __init__(self):
        super().__init__()
        self.parser = MainParser()
        self.ut = UsefulTools()
        self.output = []

    def select_all(self):
        self.insert_table_all_data_coins()
        result = self.cursor.execute(f"""SELECT * FROM temp_all_data_coins LIMIT 30""")

        return result.fetchall()

    def select_for_symbol_tokens_json(self):
        rows = self.cursor.execute("""SELECT symbol, name, slug_name, cmc_rank, date
                                    FROM temp_all_data_coins""")

        return rows.fetchall()

    def test_select(self, table, symbol):
        # (exchange, pair, price, volume_usd, market_url)
        spread_data = [(row) for row in self.parser.get_spread_data(symbol)]
        self.create_table(table)
        self.cursor.execute(f"DELETE FROM {table}")
        self.insert_table(table, spread_data)
        result = self.cursor.execute(f"""WITH t1(exchange, pair, price, volume_usd,
                                                market_url, max_vol)
                        AS (SELECT *,
                            MAX(volume_usd) OVER()
                            FROM {table}
                        ),
                        t2
                        AS (SELECT * FROM t1 WHERE volume_usd >= max_vol * 0.5
                        )
                        SELECT * FROM t2""")

        return result.fetchall()

    def select_spread(self, table, symbol, volume=0):
        # (exchange, pair, price, volume_usd, market_url)
        spread_data = [(row) for row in self.parser.get_spread_data(symbol)]
        if spread_data:  # проверка, что данные не пустые
            self.create_table(table)
            self.cursor.execute(f"DELETE FROM {table}")
            self.insert_table(table, spread_data)
            result = self.cursor.execute(
                f"""WITH t1(exchange, pair, price, volume_usd,
                            market_reputation, market_url)
                AS (SELECT * FROM {table}
                    WHERE volume_usd >= {volume})
                SELECT exchange,
                    pair,
                    price,
                    CASE
                        WHEN ROUND(((SELECT MAX(price) FROM t1) / price - 1) * 100, 2) == 0
                        THEN '0.0%'
                        ELSE ROUND(((SELECT MAX(price) FROM t1) / price - 1) * 100, 2) || '%'
                    END AS 'diff_%',
                    CASE
                        WHEN ROUND((SELECT MAX(price) FROM t1) - price, 2) == 0
                        THEN 0
                        ELSE ROUND((SELECT MAX(price) FROM t1) - price, 2)
                    END AS 'diff_usd',
                    volume_usd,
                    CASE
                        WHEN market_reputation > 0.76 THEN '🟢 High'
                        WHEN market_reputation BETWEEN 0.51 AND 0.75 THEN '🟠 Moderate'
                        ELSE '🔴 Low'
                    END AS 'Confidence',
                    market_url
                FROM t1
                WHERE price == (
                        SELECT MIN(price) FROM t1
                        ) 
                    OR price == (
                        SELECT MAX(price) FROM t1
                        )
                ORDER BY price DESC"""
            )

            return result.fetchall()
        else:
            return None

    def select_best_change(self, rank_min='0', rank_max='1', limit='15'):
        """Запрос на поиск лучших pump'ов"""
        self.insert_table_all_data_coins()
        if rank_min == '0':
            min_cmc_rank = self.cursor.execute("""SELECT cmc_rank FROM all_data_coins
                                                  ORDER BY cmc_rank DESC LIMIT 1""")
            rank_min = min_cmc_rank.fetchall()[0][0]
        else:
            rank_min = rank_min
        result = self.cursor.execute(
            f"""SELECT symbol, name, cmc_rank, price, change_1h, change_24h,
                    change_7d, change_30d, change_60d, change_90d, change_ytd,
                    volume_30d, ath, atl, strftime('%m-%d-%Y', date_added),
                    strftime('%d-%m-%Y', date), strftime('%H:%M', date)
                FROM all_data_coins
                WHERE cmc_rank BETWEEN {int(rank_max)} AND {int(rank_min)}
                ORDER BY change_1h DESC
                LIMIT {int(limit)}"""
        )

        return result.fetchall()

    def spread_output(self, table, symbol, volume=0):
        data = self.select_spread(table=table, symbol=symbol, volume=volume)
        if data:
            if len(data) == 1:  # если был отобран только один вариант по условию
                self.output = f"----------------------------\n" \
                              f"◗ <b>СПРЕД по заданному условию не найден.</b>\n" \
                              f"----------------------------\n" \
                              f"Доступен единственный вариант торгов по токену " \
                              f"<b>{symbol.upper()}</b>:\n\n" \
                              f"<b>Биржа:</b> <a href='{data[0][-1]}'>{data[0][0]}</a> " \
                              f"<b>|</b> {data[0][6]} <b>|</b>\n" \
                              f"<b>Oбъём торгов:</b> ${data[0][5]:,.2f}\n" \
                              f"<b>Пара:</b> {data[0][1]}\n" \
                              f"<b>Цена:</b> ${data[0][2]}"
            elif len(data) > 1:
                # data[0] - лежит максимальная цена за токен
                self.output = f"◗ <b>Максимальная цена:</b>\n" \
                              f"<b>Биржа:</b> <a href='{data[0][-1]}'>{data[0][0]}</a> " \
                              f"<b>|</b> {data[0][6]} <b>|</b>\n" \
                              f"<b>Oбъём торгов:</b> ${data[0][5]:,.2f}\n" \
                              f"<b>Пара:</b> {data[0][1]}\n" \
                              f"<b>Цена:</b> ${data[0][2]}\n\n" \
                              f"◗ <b>Минимальная цена:</b>\n" \
                              f"<b>Биржа:</b> <a href='{data[1][-1]}'>{data[1][0]}</a> " \
                              f"<b>|</b> {data[1][6]} <b>|</b>\n" \
                              f"<b>Объём торгов:</b> ${data[1][5]:,.2f}\n" \
                              f"<b>Пара:</b> {data[1][1]}\n" \
                              f"<b>Цена:</b> ${data[1][2]}\n" \
                              f"----------------------------\n" \
                              f"<b>СПРЕД:</b> ${data[1][4]:.2f} (+{data[1][3]})\n" \
                              f"----------------------------"

            return self.output
        else:
            return f'❌ Нет данных по токену <b>{symbol.upper()}</b> ¯\_(ツ)_/¯\n\n' \
                   f'<b>Проверьте критерии запроса:</b>\n' \
                   f'<b>Токен:</b> {symbol.upper()}\n' \
                   f'<b>Объём торгов не меньше:</b> ${volume:,.2f}\n\n' \
                   f'<em>Данные представлены для бирж с уровнем доверия выше 🔴 <b>"Low"</b> ' \
                   f'и биржа не находится в черном списке ' \
                   f'<b>{self.ut.exemption_exchanges()}</b>.</em>'

    def best_change_output(self, rank_min='0', rank_max='1', limit='10'):
        """parser_mode = 'Markdown'"""
        all_data = self.select_best_change(rank_min=rank_min, rank_max=rank_max, limit=limit)
        if all_data:
            output = []
            for data in all_data:
                symbol, name, cmc_rank, price, change_1h, change_24h, change_7d, change_30d, change_60d, \
                    change_90d, change_ytd, volume_30d, ath, atl, date_added, date, time = \
                    data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], \
                    data[9], data[10], data[11], data[12], data[13], data[14], data[15], data[16]
                if float(price) * 100000 < 1:
                    format_price = round(price, 7)
                elif float(price) * 10000 < 1:
                    format_price = round(price, 6)
                elif float(price) * 1000 < 1:
                    format_price = round(price, 5)
                elif float(price) * 100 < 1:
                    format_price = round(price, 4)
                elif float(price) * 10 < 1:
                    format_price = round(price, 3)
                else:
                    format_price = round(price, 2)
                change_1h = f"↳ *1ч:* +{float(change_1h):,.1f}% ✅" if float(change_1h) > 0 \
                    else f"↳ *1ч:* {float(change_1h):,.1f}% 🔻"
                change_24h = f"*24ч:* +{float(change_24h):,.1f}% ✅" if float(change_24h) > 0 \
                    else f"*24ч:* {float(change_24h):,.1f}% 🔻"
                change_30d = f"↳ *30дн:* +{float(change_30d):,.1f}% ✅" if float(change_30d) > 0 \
                    else f"↳ *30дн:* {float(change_30d):,.1f}% 🔻"
                change_ytd = f"*YTD:* +{float(change_ytd):,.1f}% ✅" if float(change_ytd) > 0 \
                    else f"*YTD:* {float(change_ytd):,.1f}% 🔻"
                str_n = f"*Rank #{int(cmc_rank)}* | *{symbol}* ({name})\n" \
                        f"📌 _на СМС с {date_added}_\n" \
                        f"💲 *цена* ${format_price:,}, *ATH* ${ath:,.2f},\n" \
                        f"📊 *объём за 30 дн.* ${volume_30d:,.2f}\n" \
                        f"⇅ *Изменение цены:*\n" \
                        f"{change_1h} | {change_24h}\n" \
                        f"{change_30d} | {change_ytd}\n" \
                        f"_Обновление {date} в {time} UTC_\n" \
                        f"-----------------------------------\n"
                output.append(str_n)
            if len("".join(output)) > 4096:
                return "🚫 Ограничение на количество символов в сообщении.\n" \
                       "*Задайте меньший лимит в запросею*"
            else:
                return "".join(output)
        else:
            return f'❌ Нет данных *¯\_(ツ)_/¯*'


if __name__ == "__main__":
    symbol = 'FYN'
    get_select = SelectQuery()
    # x = get_select.spread_output(table=symbol, symbol=symbol, volume=2500000)
    # x = get_select.select_best_change(rank='1000')
    out = get_select.best_change_output(rank_min='1000')
    for i in range(len(out)):
        print(out[i])

    # with open("test_data_file.json", "w") as f:
    #     token_key, token_val = {}, {}
    #     for i in range(len(x)):
    #         token_val["name"] = x[i][1]
    #         token_val["cmc_rank"] = x[i][2]
    #         token_val["date_update"] = x[i][3]
    #         token_key[x[i][0]] = token_val.copy()
    #     json.dump(token_key, f)

    # for i in range(len(x)):
    #     print(','.join(map(str, x[i])).split(','))


    # cursor.execute(f"""SELECT * FROM {table} WHERE pair == ?""", ('ETH/USDT',))
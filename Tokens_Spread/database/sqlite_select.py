import sqlite3

from database.sqlite_create import CreateDatabaseSpread, CreateDatabasePump
from parsing.parser import MainParser
from data_files.useful_tools import UsefulTools


class SelectQuerySpread(CreateDatabaseSpread):
    def __init__(self):
        super().__init__()
        self.parser = MainParser()
        self.ut = UsefulTools()
        self.output = []

    def format_price_correct(self, price):
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
        return format_price

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

    def spread_output(self, table, symbol, volume=0):
        data = self.select_spread(table=table, symbol=symbol, volume=volume)
        if data:
            if len(data) == 1:  # если был отобран только один вариант по условию
                self.output = f"----------------------------\n" \
                              f"<b>СПРЕД по заданному условию не найден.</b>\n" \
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

    def select_spread_zazam(self, volume_usd='0', spread_val='2'):
        result = self.cursor.execute(f"""
            WITH t1(token_name, price)
            AS (SELECT token_name, MIN(price)
                FROM zazam_table
                WHERE volume_usd >= {float(volume_usd)}
                GROUP BY token_name),
                t2(token_name, price)
            AS (SELECT token_name, MAX(price)
                FROM zazam_table
                WHERE volume_usd >= {float(volume_usd)}
                GROUP BY token_name) 
            SELECT z1.symbol, z1.token_name, z1.exchange,
                CASE
                    WHEN z1.market_reputation > 0.76 THEN '🟢 High'
                    WHEN z1.market_reputation BETWEEN 0.51 AND 0.75 THEN '🟠 Moderate'
                    ELSE '🔴 Low'
                END AS 'confidence_min',
                z1.market_url, z1.pair, t1.price, z1.volume_usd,
                z2.exchange,
                CASE
                    WHEN z2.market_reputation > 0.76 THEN '🟢 High'
                    WHEN z2.market_reputation BETWEEN 0.51 AND 0.75 THEN '🟠 Moderate'
                    ELSE '🔴 Low'
                END AS 'confidence_max',
                z2.market_url, z2.pair, t2.price, z2.volume_usd,
                ROUND((t2.price / t1.price - 1) * 100, 2) AS spread
            FROM t1 JOIN t2 USING(token_name)
            JOIN zazam_table z1 ON z1.price=t1.price
            JOIN zazam_table z2 ON z2.price=t2.price
            WHERE spread >= {float(spread_val)}
            ORDER BY spread DESC
            """)
        return result.fetchall()

    def select_output_zazam(self, volume_usd='1000', spread_val='2'):
        zazam_output = []
        data = self.select_spread_zazam(volume_usd=volume_usd, spread_val=spread_val)
        if data:
            for row in data:
                keys = ['symbol', 'token_name', 'exchange_min', 'confidence_min', 'url_min', 'pair_min',
                          'price_min', 'volume_min', 'exchange_max', 'confidence_max', 'url_max',
                          'pair_max', 'price_max', 'volume_max', 'spread']
                params = dict(zip(keys, [*row]))
                params["price_min"] = self.format_price_correct(price=params["price_min"])
                params["price_max"] = self.format_price_correct(price=params["price_max"])
                message = f"◗ <b>{params['symbol']}</b> ({params['token_name']})\n" \
                          f"↳ <b>Max</b> - ${params['price_max']:,} " \
                          f"на <a href='{params['url_max']}'>{params['exchange_max']}</a> " \
                          f"| {params['confidence_max']}, " \
                          f"<b>Vol.:</b> ${params['volume_max']:,.0f} {params['pair_max']}\n" \
                          f"↳ <b>Min</b> - ${params['price_min']:,} " \
                          f"на <a href='{params['url_min']}'>{params['exchange_min']}</a> " \
                          f"| {params['confidence_min']}, " \
                          f"<b>Vol:</b> ${params['volume_min']:,.0f} {params['pair_min']}\n" \
                          f"\n" \
                          f"📈 <b>СПРЕД:</b> {params['spread']}%\n" \
                          f"-----------------------------\n"
                zazam_output.append(message)
        return zazam_output  # возвращать списком, в хэндлере делить на 3 части и делать "".join()

class SelectQueryPump(CreateDatabasePump, SelectQuerySpread):
    def __init__(self):
        super().__init__()
        self.parser = MainParser()
        self.ut = UsefulTools()
        self.output = []

    def select_all(self):
        # self.insert_table_all_data_coins()
        in_tokens = self.ut.get_tokens_on_exchanges('binance_bybit_tokens.txt')
        try:
            result = self.cursor.execute(f"""SELECT * FROM all_data_coins
                                            WHERE symbol IN ({in_tokens})
                                            LIMIT 30""")

            return result.fetchall()
        except sqlite3.OperationalError:
           self.insert_table_all_data_coins()

    def select_for_symbol_tokens_json(self):
        rows = self.cursor.execute("""SELECT symbol, name, slug_name, cmc_rank, date
                                    FROM temp_all_data_coins""")

        return rows.fetchall()

    def select_best_change(self, rank_min='100000', rank_max='1', limit='10'):
        """Запрос на поиск лучших pump'ов"""
        self.insert_table_all_data_coins()
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

    def best_change_output(self, rank_min='100000', rank_max='1', limit='10'):
        """parser_mode = 'Markdown'"""
        all_data = self.select_best_change(rank_min=rank_min, rank_max=rank_max, limit=limit)
        if all_data:
            output = []
            for data in all_data:
                symbol, name, cmc_rank, price, change_1h, change_24h, change_7d, change_30d, change_60d, \
                    change_90d, change_ytd, volume_30d, ath, atl, date_added, date, time = \
                    data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], \
                    data[9], data[10], data[11], data[12], data[13], data[14], data[15], data[16]
                format_price = self.format_price_correct(price)
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

    def select_best_change_to_me(self, rank_min='100000', rank_max='1'):
        """Запрос на поиск лучших pump'ов монет из предоставленного списка"""
        self.insert_table_all_data_coins()
        in_symbols = self.ut.get_tokens_on_exchanges('binance_bybit_tokens.txt')
        result = self.cursor.execute(
            f"""SELECT symbol, name, cmc_rank, price, change_1h, change_24h,
                    change_7d, change_30d, change_60d, change_90d, change_ytd,
                    volume_30d, ath, atl, strftime('%m-%d-%Y', date_added),
                    strftime('%d-%m-%Y', date), strftime('%H:%M', date)
                FROM all_data_coins
                WHERE cmc_rank BETWEEN {int(rank_max)} AND {int(rank_min)}
                      AND symbol IN ({in_symbols})
                ORDER BY change_1h DESC
                LIMIT 10"""
        )

        return result.fetchall()

    def best_change_output_to_me(self, rank_min='100000', rank_max='1'):
        """parser_mode = 'Markdown'"""
        all_data = self.select_best_change_to_me(rank_min=rank_min, rank_max=rank_max)
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

    result = SelectQuerySpread().select_output_zazam()
    # part = len(result) // 3
    # res1 = result[:part]
    # res2 = result[part:part + part]
    # res3 = result[part + part:]
    # print("".join(res1))
    # print('===============================')
    # print("".join(res2))
    # print('===============================')
    # print("".join(res3))
    # print('===============================')
    print("".join(result))
    print(len("".join(result)))

    # get_select = SelectQuerySpread().select_spread_zazam(volume_usd='100000')
    # for _ in get_select:
    #     print(*_)

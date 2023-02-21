from building_data.get_data import BuildingData


class OutputData(BuildingData):
    def __init__(self):
        super().__init__()
        self.main_url = 'https://dom.mingkh.ru'

    def get_output_result(self, data_flainfo: dict, data_mingkh: dict, url_mingkh: str):
        """Сюда приходят данные со всех сайтов и подготавливается сообщение для вывода
        пользователю. Данные приходят от бота."""
        """Данные с сайта FLATINFO"""
        addr_name_f = data_flainfo["name"].replace("улица", "ул.,").replace("дом ", "д.")\
                        .replace("корпус ", "к.").replace("строение ", "стр.")
        url_f = data_flainfo.get("url", 'https://flatinfo.ru/')
        flatinfo_data = self.flatinfo_data(url=url_f)
        """Данные с сайта dom.mingkh.ru"""
        url_gkh = url_mingkh
        mingkh_data = data_mingkh


        if isinstance(flatinfo_data, str):
            return flatinfo_data
        else:
            if flatinfo_data["Назначение:"].strip() == 'Жилой дом':
                """Инфа будет с разных сайтов"""
                self.flatinfo_output = [f"🏠 <b>{addr_name_f}</b>\n"
                                        f"<a href='{url_f}'>FlaInfo.ru</a> | <a href='{url_gkh}'>ДОМ.МИНЖКХ</a> \n"
                                        f"◗ <b>Назначение:</b> \n"
                                        f" ↳ {flatinfo_data.get('Назначение:', '<em>нет данных</em>')}\n"
                                        f" ↳ {mingkh_data.get('Назначение:', '<em>нет данных</em>')}\n"
                                        f"◗ <b>Год постройки:</b> "
                                        f"{flatinfo_data.get('Год постройки:', '<em>нет данных</em>')} | "
                                        f"{mingkh_data.get('Год постройки:', '<em>нет данных</em>')}\n"
                                        f"◗ <b>Кол-во этажей:</b> "
                                        f"{flatinfo_data.get('Этажей всего:', '<em>нет данных</em>')} | "
                                        f"{mingkh_data.get('Этажей всего:', '<em>нет данных</em>')}\n"
                                        f"◗ <b>Подъездов:</b> "
                                        f"{flatinfo_data.get('Подъездов:', '<em>нет данных</em>')} | "
                                        f"{mingkh_data.get('Подъездов:', '<em>нет данных</em>')}\n"
                                        f"◗ <b>Подвальных этажей:</b> "
                                        f"{flatinfo_data.get('Подвальных этажей:', '<em>нет данных</em>')}\n"
                                        f"◗ <b>Площадь подвала, кв.м.:</b> "
                                        f"{mingkh_data.get('Площадь подвала:', '<em>нет данных</em>')}\n"
                                        f"◗ <b>Типовая серия:</b>\n"
                                        f" ↳ {flatinfo_data.get('Типовая серия:', '<em>нет данных</em>')}\n"
                                        f" ↳ {mingkh_data.get('Типовая серия:', '<em>нет данных</em>')}\n"
                                        f"◗ <b>Перекрытия:</b>\n"
                                        f" ↳ {flatinfo_data.get('Перекрытия:', '<em>нет данных</em>')}\n"
                                        f" ↳ {mingkh_data.get('Перекрытия:', '<em>нет данных</em>')}\n"
                                        f"◗ <b>Каркас:</b>\n"
                                        f" ↳ {flatinfo_data.get('Каркас:', '<em>нет данных</em>')}\n"
                                        f"◗ <b>Стены:</b> {flatinfo_data.get('Стены:', '<em>нет данных</em>')}\n"
                                        f" ↳ <b>Несущие стены:</b> "
                                        f"{mingkh_data.get('Несущие стены:', '<em>нет данных</em>')}\n"
                                        f" ↳ <b>Внутр.стены:</b> {mingkh_data.get('Внутр.стены:', '<em>нет данных</em>')}\n"
                                        f"◗ <b>Фундамент:</b>\n"
                                        f" ↳ {flatinfo_data.get('Фундамент:', '<em>нет данных</em>')}\n"
                                        f" ↳ {mingkh_data.get('Фундамент:', '<em>нет данных</em>')}\n"
                                        f"◗ <b>Газоснабжение:</b>\n"
                                        f" ↳ {flatinfo_data.get('Газоснабжение:', 'нет')}\n"
                                        f" ↳ {mingkh_data.get('Газоснабжение:', 'нет')}\n"
                                        ]
            else:
                """Инфа только с FlaInfo.ru сайта """
                self.flatinfo_output = [f"🏢 <b>{addr_name_f}</b>\n"
                                        f"<a href='{url_f}'>FlaInfo.ru</a>\n"
                                        f"◗ <b>Назначение:</b> {flatinfo_data.get('Назначение:', '<em>нет данных</em>')}\n"
                                        f"◗ <b>Год постройки:</b> {flatinfo_data.get('Год постройки:', '<em>нет данных</em>')}\n"
                                        f"◗ <b>Типовая серия:</b> {flatinfo_data.get('Типовая серия:', '<em>нет данных</em>')}\n"
                                        f"◗ <b>Каркас:</b> {flatinfo_data.get('Каркас:', '<em>нет данных</em>')}\n"
                                        f"◗ <b>Стены:</b> {flatinfo_data.get('Стены:', '<em>нет данных</em>')}\n"
                                        f"◗ <b>Этажей всего:</b> {flatinfo_data.get('Этажей всего:', '<em>нет данных</em>')}\n"
                                        f"◗ <b>Подвальных этажей:</b> {flatinfo_data.get('Подвальных этажей:', '<em>нет данных</em>')}\n"
                                        f"◗ <b>Подъездов:</b> {flatinfo_data.get('Подъездов:', '<em>нет данных</em>')}\n"
                                        ]

            return self.flatinfo_output

    def output_info(self, data_flainfo, full_address):
        """full_address - будет прилетать от бота. Он формируется на сайте
        flstinfo.ru"""
        url_mingkh = self.mingkh_get_address_url(address=full_address)
        data_mingkh = self.mingkh_data(url=url_mingkh) if url_mingkh else {}
        output_result = self.get_output_result(data_flainfo=data_flainfo,
                                               data_mingkh=data_mingkh, url_mingkh=url_mingkh)

        return "".join(output_result)

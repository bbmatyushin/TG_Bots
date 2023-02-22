import re

from building_data.get_data import BuildingData


class OutputData(BuildingData):
    def __init__(self):
        super().__init__()
        self.main_mingkh_url = 'https://dom.mingkh.ru'
        self.main_dommos_url = 'https://dom.mos.ru'
        self.search_url_dommos = 'https://dom.mos.ru/Lookups/GetSearchAutoComplete'

    def get_output_result(self, addr_data_flainfo: dict, data_mingkh: dict, data_dommos: dict,
                          url_mingkh: str, url_dommos: str):
        """Сюда приходят данные со всех сайтов и подготавливается сообщение для вывода
        пользователю. Данные приходят от бота."""
        """Данные с сайта FLATINFO"""
        addr_name_f = addr_data_flainfo["name"].replace("улица", "ул.,").replace("дом ", "д.")\
                        .replace("корпус ", "к.").replace("строение ", "стр.").replace("шоссе", "ш.")
        url_f = addr_data_flainfo.get("url", 'https://flatinfo.ru/')
        flatinfo_data = self.flatinfo_data(url=url_f)
        """Данные с сайта dom.mingkh.ru"""
        url_gkh = url_mingkh
        mingkh_data = data_mingkh
        dommos_data = data_dommos

        if isinstance(flatinfo_data, str):
            return flatinfo_data
        else:
            if flatinfo_data.get("Назначение:") or mingkh_data.get('Назначение:'):
                s = f"{flatinfo_data.get('Назначение:')} {mingkh_data.get('Назначение:')}"
                if re.search(r'[Жж]илой.*дом', s):
                # if flatinfo_data.get("Назначение:").strip() == 'Жилой дом':
                    """Инфа будет с разных сайтов"""
                    self.output_result = [f"🌐 <a href='{url_f}'>FlaInfo.ru</a> | "
                                          f"<a href='{url_gkh}'>ДОМ.МИНЖКХ</a> | "
                                          f"<a href='{url_dommos}'>Дома Москвы</a>\n"
                                          f"🏠 <b>{addr_name_f}</b>\n"
                                          f"-------------------------------\n"
                                          f"◗ <b>Назначение:</b> \n"
                                          f" ↳ {flatinfo_data.get('Назначение:', '<em>нет данных</em>')}\n"
                                          f" ↳ {mingkh_data.get('Назначение:', '<em>нет данных</em>')}\n"
                                          f" ↳ {dommos_data.get('Назначение:', '<em>нет данных</em>')}\n"
                                          f"◗ <b>Год постройки:</b> "
                                          f"{flatinfo_data.get('Год постройки:', '<em>нет данных</em>')} | "
                                          f"{mingkh_data.get('Год постройки:', '<em>нет данных</em>')} | "
                                          f"{dommos_data.get('Год постройки:', '<em>нет данных</em>')}\n"
                                          f"◗ <b>Кол-во этажей:</b> "
                                          f"{flatinfo_data.get('Этажей всего:', '<em>нет данных</em>')} | "
                                          f"{mingkh_data.get('Этажей всего:', '<em>нет данных</em>')} | "
                                          f"{dommos_data.get('Этажей всего:', '<em>нет данных</em>')}\n"
                                          f"◗ <b>Подъездов:</b> "
                                          f"{flatinfo_data.get('Подъездов:', '<em>нет данных</em>')} | "
                                          f"{mingkh_data.get('Подъездов:', '<em>нет данных</em>')} | "
                                          f"{dommos_data.get('Подъездов:', '<em>нет данных</em>')}\n"
                                          f"◗ <b>Подвальных этажей:</b> "
                                          f"{flatinfo_data.get('Подвальных этажей:', '<em>нет данных</em>')} | "
                                          f"{dommos_data.get('Подвальных этажей:', '<em>нет данных</em>')}\n"
                                          f"◗ <b>Площадь подвала, кв.м.:</b> "
                                          f"{mingkh_data.get('Площадь подвала:', '<em>нет данных</em>')}\n"
                                          f"◗ <b>Типовая серия:</b>\n"
                                          f" ↳ {flatinfo_data.get('Типовая серия:', '<em>нет данных</em>')}\n"
                                          f" ↳ {mingkh_data.get('Типовая серия:', '<em>нет данных</em>')}\n"
                                          f" ↳ {dommos_data.get('Типовая серия:', '<em>нет данных</em>')}\n"
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
                                          f"-------------------------------\n"
                                          ]
                else:
                    """Инфа только с FlaInfo.ru сайта """
                    self.output_result = [f"🌐 <a href='{url_f}'>FlaInfo.ru</a>\n"
                                          f"🏢 <b>{addr_name_f}</b>\n"
                                          f"-------------------------------\n"
                                          f"◗ <b>Назначение:</b> {flatinfo_data.get('Назначение:', '<em>нет данных</em>')}\n"
                                          f"◗ <b>Год постройки:</b> {flatinfo_data.get('Год постройки:', '<em>нет данных</em>')}\n"
                                          f"◗ <b>Типовая серия:</b> {flatinfo_data.get('Типовая серия:', '<em>нет данных</em>')}\n"
                                          f"◗ <b>Каркас:</b> {flatinfo_data.get('Каркас:', '<em>нет данных</em>')}\n"
                                          f"◗ <b>Стены:</b> {flatinfo_data.get('Стены:', '<em>нет данных</em>')}\n"
                                          f"◗ <b>Этажей всего:</b> {flatinfo_data.get('Этажей всего:', '<em>нет данных</em>')}\n"
                                          f"◗ <b>Подвальных этажей:</b> {flatinfo_data.get('Подвальных этажей:', '<em>нет данных</em>')}\n"
                                          f"◗ <b>Подъездов:</b> {flatinfo_data.get('Подъездов:', '<em>нет данных</em>')}\n"
                                          f"-------------------------------\n"
                                          ]
            elif re.search(r'\d+\b', url_f) or re.search(r'\d+\b', url_gkh) \
                    or re.search(r'Passport', url_dommos):  # если url flatinfo заканчивается на цифры, значит какая-то инфа есть
                self.output_result = [f"🌐 <a href='{url_f}'>FlaInfo.ru</a> | "
                                      f"<a href='{url_gkh}'>ДОМ.МИНЖКХ</a> | "
                                      f"<a href='{url_dommos}'>Дома Москвы</a>\n"
                                      f"🏗 <b>{addr_name_f}</b>\n"
                                      f"-------------------------------\n"
                                      f"Нет полезной информации 🔍"
                                      f"-------------------------------\n"]
            else:
                return ["❓ Информация не найдена"]

            return self.output_result

    def output_info(self, addr_data_flainfo, full_address):
        """full_address - будет прилетать от бота. Он формируется на сайте
        flstinfo.ru. В data_flainfo содержится инфа об улице"""
        url_mingkh = self.mingkh_get_address_url(address=full_address)
        data_mingkh = self.mingkh_data(url=url_mingkh) if url_mingkh else {}
        url_dommos = self.dommos_get_building_url(address=full_address)
        data_dommos = self.dommos_data(url=url_dommos) if url_dommos else {}
        output_result = self.get_output_result(addr_data_flainfo=addr_data_flainfo, data_mingkh=data_mingkh,
                                               data_dommos=data_dommos,
                                               url_mingkh=url_mingkh, url_dommos=url_dommos)

        return "".join(output_result)

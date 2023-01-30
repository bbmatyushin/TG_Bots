from data_files.delline_cities_code import DellineCitiesCode

shipper_list = ['Деловые Линии']
cities_list = list(DellineCitiesCode().extract_cities_code_dl().keys())


if __name__ == "__main__":
    for c in cities_list:
        print(c)

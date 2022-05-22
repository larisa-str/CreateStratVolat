# -*- coding: utf-8 -*-
# !/usr/bin/env python3


class QuikStr():

    def __init__(self, file, rts_code, rts_expir_date, now_baseprice, expir_date, **pos_parameters):
        '''Конструктор класса, вызывается при инициализации/создании экземпляра объекта Strat().
        Собирает "Стратегию.str" для загрузки в QUIK => Расширения => Стратегии.'''
        # Пр.
        # INFOSTR
        # LongCall_18июня-5.str&Лонг колл&RTS&1&SPBFUT&RIM0&3 12 4 121120 0 20200614 23 5 121120 0 20200618 33023 16744448 255 1 1 1 0 1 2 20200618 120000 1 1 2900 6 RI120000BF0 SPBOPT 1 1 111000
        # Пр.: INFOSTR
        #      LongCall_18июня.str&nopattern&RTS&1&SPBFUT&RIM0&      [Имя файла=LongCall_18июня.str, ШаблонQuik=nopattern, --??Инструмент--=1, SPBFUT, RIM0]
        #      0                                   [Фактич: ставка=0]
        #      10 0 121120 0 20200614              [Сценарий 1:  волат=+10, ставка=0, цена б/а=121120, --??xxx--=0, дата расчёта=14.06.2020]
        #      20 0 121120 0 20200618              [Сценарий 2:  волат=+20, ставка=0, цена б/а=121120, --??xxx--=0, дата расчёта=18.06.2020]
        #      33023 16744448 255                  [цвета графика= ---(фактич), ---(сценарий1), 255(сценарий2)]
        #      1 0 1                               [График(CheckBox, вкл./выкл. сценарий): 1-(фактич), 0-(сценарий1), 1-(сценарий2)]
        #      0 1                                 [Отображать прибыль в валюте=0, кол-во компонентов в таблице Позиций=1]
        #      2 20200618 120000 1 1 2900          [Тип иснтрумента(1=Call, 2=Put), Дата.исп.=18.06.2020, Страйк=120000, Тип сделки(long=1, Short=2), Кол-во=1, Цена=2900]
        #      6 RI120000BF0 SPBOPT 1              [Источник=6(Предложение), Код инструмента=RI120000BF0, Площадка=SPBOPT, Вкл./выкл.инструмент=1]
        #      1 20000                             [Обновлять рын.информацию=1, Время обновл.=20 сек.(+,000???)]

        # 1. Информационный блок
        self.file = file
        self.rts_code = rts_code                      # код базового актива (RIU0 - Exp:17.09.2020)
        self.rts_number = '1'                         # кол-во RTS в списке доступных базовых инструментов
        self.pattern = 'nopattern'                    # если задан шаблон QUIK-стратегии, то вставить название, напр.'Лонг колл'
        end = '\x04\x00\x00\x00\n'                    # => '' или '&#4;' или '\x04' - символ конца передачи данных
        self.info = f"INFOSTR{end}" + f"{file}&{self.pattern}&RTS&{self.rts_number}&SPBFUT&{rts_code}&"

        # 2. Блок "Параметры", Фактическое состояние
        self.fact_rate = '0'                          # безриск.ставка
        self.fact = self.fact_rate

        # 3. Блок "Параметры", Сценарий 1
        # 10 0 121120 0 20200614
        self.scen1_vola = f'''0'''                        # волатильность (+- смещение относительно открытия)
        self.scen1_rate = '0'                             # безриск.ставка
        self.scen1_baseprice = f'''{now_baseprice}'''     # if-цена базового актива, по-умолч.= текущей цене
        self.scen1_xxx = '0'                              # ??? - не понятно что это за поле
        self.scen1_date = '20200630'                      # if-дата расчёта = дата между датой открытия позы и экспирацией
        self.scen1 = self.scen1_vola +' '+ self.scen1_rate +' '+self.scen1_baseprice +' '+ self.scen1_xxx +' '+ self.scen1_date

        # 4. Блок "Параметры", Сценарий 2 (экспирация)
        # "20 0 121120 0 20200618"
        self.scen2_vola = f'''0'''                        # волатильность (+- смещение относительно открытия)
        self.scen2_rate = '0'                             # безриск.ставка
        self.scen2_baseprice = f'''{now_baseprice}'''     # if-цена базового актива, по-умолч.= текущей цене
        self.scen2_xxx = '0'                              # ??? - непонятно что это за поле
        self.scen2_date = f'''{expir_date}'''             # дата расчёта = дата экспирации
        self.scen2 = self.scen2_vola +' '+ self.scen2_rate +' '+self.scen2_baseprice +' '+ self.scen2_xxx +' '+ self.scen2_date

        # 5. Цвета графика
        # "33023 16744448 255"
        self.color_fact = '33023'                   # оранжевый
        self.color_scen1 = '16744448'               # голубой
        self.color_scen2 = '255'                    # красный
        self.color = self.color_fact +' '+ self.color_scen1 +' '+ self.color_scen2

        # 6. Графики к сценариям
        # "1 0 1"
        self.graph_fact = '1'                       # график (check box, вкл./выкл.)
        self.graph_scen1 = '1'                      # график (check box, вкл./выкл.)
        self.graph_scen2 = '1'                      # график (check box, вкл./выкл.)
        self.graph = self.graph_fact +' '+ self.graph_scen1 +' '+ self.graph_scen2

        # 7. Валюта
        # "0"
        self.currency = '0'                         # отображать прибыль в валюте (0/1)


        # 8. Кол-во компонентов в таблице 'Позиции'
        # "1"
        self.comp_pos = str(len(pos_parameters))     # кол-во компонентов в таблице Позиций (активных и неактивных)


        # 9. Позиции, Список инструментов, Опцион
        # Цикл по позициям *pos_parameters
        self.pos = None
        for pos_code in pos_parameters:

            pos_inst = pos_parameters[pos_code][0]           # инструмент
            pos_strike = pos_parameters[pos_code][1]         # страйк
            pos_transaction = pos_parameters[pos_code][2]    # long/short
            pos_number = pos_parameters[pos_code][3]         # кол-во
            pos_price = pos_parameters[pos_code][4]          # цена

            # Опцион:   "2 20200618 120000 1 22 1335 4 RI122500BF0 SPBOPT 1"
            # Фьючерс:  "1 20200618 0 2 66 121120 2 RIM0 SPBFUT 1"
            self.pos_inst = f'''{pos_inst}'''                # инструмент (1=FUT, 2=CALL, 3=PUT)
            # параметры для опционов
            if pos_inst in ["2", "3"]:
                self.pos_date = f'''{expir_date}'''         # дата экспирации опциона
                self.pos_platform = 'SPBOPT'                # площадка, биржа
            # параметры для фьючерсов
            if (pos_inst == "1"):
                self.pos_date = f'''{rts_expir_date}'''     # дата экспирации фьючерса
                self.pos_platform = 'SPBFUT'                 # площадка, биржа
            # общие параметры
            self.pos_strike = f'''{pos_strike}'''            # страйк  (для фьючерса='0')
            self.pos_transaction = f'''{pos_transaction}'''  # тип сделки (1=Long, 2=Short)
            self.pos_number = f'''{pos_number}'''            # количество позиций по инструменту
            self.pos_price = f'''{pos_price}'''              # цена инструмента
            # "6 RI120000BF0 SPBOPT",  "3 RIM0 SPBFUT"
            self.pos_source = '2'                       # источник цены: (1=Ввод вручную, 2=Теотер.цена, 3=Послед.сделка,
                                                        # 4=Средн.котировочная (среднее между спросом и предлож.), 5=Спрос, 6=Предложение)
            self.pos_code = pos_code                    # код инструмента (опциона или фьючерса) - 'RI122500BF0'
            self.pos_on = '1'                           # вкл./выкл. инструмент (1=вкл., 0=выкл)
            self.pos_temp = self.pos_inst +' '+ self.pos_date +' '+ self.pos_strike +' '+ self.pos_transaction +' '+ self.pos_number +' '+ \
                       self.pos_price +' '+ self.pos_source +' '+ self.pos_code +' '+ self.pos_platform +' '+ self.pos_on
            if self.pos == None:
                self.pos = self.pos_temp
            else:
                self.pos = self.pos +' '+ self.pos_temp


        # 10. Время обновления
        # "1 20000"
        self.time_update = '1'                      # обновлять рыночную информацию (checkbox=0/1)
        self.time_sec = '20000'                     # время обновления 20 сек.(+ ,000)
        self.time = self.time_update +' '+ self.time_sec

        # Собрать шаблон (между info и fact пробел не нужен)
        self.strinfo = self.info + self.fact +' '+ self.scen1 +' '+ self.scen2 +' '+ self.color +' '+ self.graph +' '+ \
                       self.currency +' '+ self.comp_pos +' '+ self.pos +' '+ self.time

        self.strinfo = self.strinfo + '\n'
        # ----end of __init__----



    def save_strat_to_file(self, strat_file_path):
        '''Сохранить стратегию в отдельный текстовый файл 'Моя_стратегия.str'.'''
        with open(strat_file_path, "w", encoding='cp1251') as str_file:
            str_file.write(self.strinfo)

        return



    def check_file_content(self, strat_file_path, quik_file_path):
        '''Проверка содержимого файла стратегии в сравнении с файлом, созданным в Quik.'''
        for file in [strat_file_path, quik_file_path]:
            print(f'\nСодержимое файла {file}:')
            file = open(file, "r")
            #print(file)                                # вывести файл-объект, показать кодировку
            lines = file.readlines()                   # построчное считывание файла
            print(lines)                               # вывести содержимое файла, в виде списка строк
            file.close()

        return
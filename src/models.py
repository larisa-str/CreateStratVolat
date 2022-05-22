# -*- coding: utf-8 -*-
# !/usr/bin/env python3

"""Построение моделей на основе шаблонов стратегий."""

import yaml
import re


# Открыть файл со списком стратегий, страйков, кодировок
try:
   stream = open("patterns/patterns.yaml", encoding='utf-8')
   PATTERNS = yaml.safe_load(stream)
except yaml.YAMLError as exc:  print(exc)



class Model():

    def __init__(self, rts_code, rts_expir_date, now_baseprice, expir_date, pattern):
        self.rts_code = rts_code
        self.rts_expir_date = rts_expir_date
        self.now_baseprice = now_baseprice
        self.expir_date = expir_date
        self.pattern = pattern
        # Коды опционов
        self.call_code = PATTERNS['OptCodes'][self.expir_date][0]
        self.put_code = PATTERNS['OptCodes'][self.expir_date][1]
        # end of __init___
        
        return


    def get_model_by_pattern(self):
        '''Получить модель стратегии с кодами инструментов на базе заданного шаблона.
           Пр. pattern = "-2*put(x), call(y)"   => model_by_pattern = "-2*RI125000BS0A(x), RI125000BG0A(y)" '''

        # Находим ближайший страйк к текущей цене актива - "стартовый" страйк, слева от него собираем Put-ы, справа- Call-ы
        # округлить round(x,-1): до десятков, -2: до сотен, -3: до тысяч
        ## print(f"{round(124520, -1)}, {round(124520, -2)}, {round(124520, -3)}")
        self.start_strike, n = 0, -2
        while self.start_strike not in PATTERNS['Strikes']:
            self.start_strike = str(round(int(self.now_baseprice), n))
            n -= 1
        print(f"Стартовый страйк: {self.start_strike}")


        model = self.pattern[1]   # "-1*put(x), call(y)"
        # Заменить отрицательные номера шагов на страйки (с -1 до -9 в обратном порядке)
        for ind in range(-1, -10, -1):
            new_strike = str(int(self.start_strike) + 2500 * ind)
            if model.find(f'{ind}*put') > -1:    model = model.replace(f'{ind}*put', f'RI{new_strike}{self.put_code}')
            if model.find(f'{ind}*call') > -1:   model = model.replace(f'{ind}*call', f'RI{new_strike}{self.call_code}')

        # Только после этого можно заменить положит.номера шагов на страйки (с 1 до 9 в прямом порядке)
        for ind in range(1, 10):
            new_strike = str(int(self.start_strike) + 2500 * ind)
            if model.find(f'{ind}*put') > -1:     model = model.replace(f'{ind}*put', f'RI{new_strike}{self.put_code}')
            if model.find(f'{ind}*call') > -1:    model = model.replace(f'{ind}*call', f'RI{new_strike}{self.call_code}')

        # И только теперь подставить текущие страйки
        new_strike = self.start_strike
        if model.find('put') > -1:      model = model.replace('put', f'RI{new_strike}{self.put_code}')
        if model.find('call') > -1:     model = model.replace('call', f'RI{new_strike}{self.call_code}')


        # Подставить код фьючерса
        if model.find('fut') > -1:      model = model.replace('fut', self.rts_code)


        # Модель с указанием кодов, список инструментов
        self.model = model
        print(f"Сгенерирована модель: '{self.model}' по шаблону '{self.pattern[1]}'")

        return



    def get_parameters_by_model(self):
        '''Получить строку с параметрами позиций используя модель.
           Параметры: {Код инструм.: [страйк, тип инструм., (+-)кол-во, цена]}
           цену можно не указывать, если выставлять Источник = 'теоретическая цена'
           Пр. {"RI125000BS0A":["125000", "3", "22", "0"], "RI125000BG0A":["127500", "2", "33", "0"]}  '''


        # Преобразовать собранную модуль в список компонентов
        model_list = self.model.split(',')

        # Цикл по компонентам
        pos_parameters = {}
        for component in model_list:
            component = component.strip()

            # Кол-во
            number = 1
            #if re.search(r'\(\d+\)', component):
            #    component = re.sub(r'\(\d+\)', '', component)
            if component.find("(") >-1:
                code = component.split("(")[0]
                n_temp = component.split("(")[1]
                number = n_temp.replace(")", '')
            else:
                code = component

            # Отрицательные значения number переводим в положительные и меняем тип транзакции (long/short)
            number_int = int(number)
            if (number_int < 0):
                number_int = abs(number_int)
                number = str(number_int)
                transaction = "2"     # (1=Long, 2=Short)
            else:
                transaction = "1"


            # Список параметров [страйк, тип_инструмента, тип_сделки, кол-во, цена] для каждого опциона
            # тип инструмента (1=FUT, 2=CALL, 3=PUT)
            if code[-3:] in PATTERNS['Calls']:      inst = "2"   # [-3:] - три последних элемента массива
            elif code[-3:] in PATTERNS['Puts']:     inst = "3"
            elif code[0:4] in PATTERNS['Futs']:      inst = "1"

            # Вытащим страйки
            if inst in ["2", "3"]:
                strike = code[2:(len(code)-3)]
            else:
                strike = "0"  # страйк для фьючерсов = 0

            opt_list = []
            opt_list.append(inst)         # инструмент
            opt_list.append(strike)       # страйк
            opt_list.append(transaction)  # long/short
            opt_list.append(number)       # кол-во
            opt_list.append("0")          # цена
            pos_parameters.update({code: opt_list})


        # Параметры стратегии
        self.pos_parameters = pos_parameters
        print(f"{pos_parameters}")

        return
# -*- coding: utf-8 -*-
# !/usr/bin/env python3

"""
@Author: Larisa Strikha

СОЗДАНИЕ ФАЙЛА ОПЦИОННОЙ СТРАТЕГИИ 'Моя_стратегия.str' ПО ЗАДАННОМУ PATTERN-ШАБЛОНУ (шаюлоны хранятся в файле "patterns.yaml"). 
Файл стратегии *.str будет загружаться в Quik, в модуль опционный аналитики: 
   Главное меню -> Расширения -> Стратегии (за работу модуля опционной аналитики отвечает StratVolat.dll).
ЗАПУСК КОДА С ПАРАМЕТРАМИ:
с параметром по-умолчанию
/> python createstrat.py
с указанием шаблона стратегии
/> python createstrat.py -p LongCall
/> python cretesrtat.py --pattern LongCall
с несколькими значениями аргумента pattern
/> python createstrat.py --strat LongCall LongPut ShortCall ShortPut
/> python cretesrtat.py --strat LongStraddle ShortPut --expiration 20200702 --baseprice 124540

"""

import sys
import yaml
import json
from src.quikstr import QuikStr
from src.models import Model, PATTERNS
import argparse
from termcolor import colored



def create_parser():
    '''Разбор параметров командной строки.'''
    parser = argparse.ArgumentParser()
    # можно задать длинное и короткое имя аргумента со значением = наименованию паттерна стратегии, и добавим
    # возможность передавать под одним pattern имена нескольких стратегий (nargs='+' ожидается одно или более значений)
    parser.add_argument('-s', '--strat', nargs='+', default='LongCall')
    # дата экспирации в формате 'yyymmdd'
    parser.add_argument('-e', '--expiration', default='20200917')
    # текущая цена базового актива (можно передавать любой страйк, который хотим сделать стартовым)
    parser.add_argument('-b', '--baseprice', default='120000')
    # максимальный убыток по стратегии в руб.
    parser.add_argument('-m', '--maxloss', default='5000')

    return parser




def main():

   # I. Получить входные параметры:
   # - название стратегии,
   # - дату экспирации,
   # - текущую цену базового актива, относительно которой будет строиться стратегия (по-умолчанию базовый актив всегда RTS)
   # - заданный максимальный убыток по стратегии

   parser = create_parser()
   namespace = parser.parse_args(sys.argv[1:])   # первый аргумент- всегда имя файла питон, поэтому его вырезаем из списка
   print(f"{namespace}")

   expir_date = namespace.expiration              # дата экспирации
   now_baseprice = namespace.baseprice            # текущая цена базового актива (либо стартовый страйк)
   max_loss = namespace.maxloss                   # максимальный убыток по стратегии
   print(colored(f"Дата эскпирации: {expir_date}", 'green', attrs=['bold']))
   print(colored(f"Текущая цена: {now_baseprice}", 'yellow', attrs=['bold']))
   print(colored(f"Максимальный убыток по стратегии: {max_loss} руб.", 'red'))


   # II. Построить стратегию(-ии) по шаблону

   # Цикл по стратегиям, переданным в командной строке
   for strat in namespace.strat:

       # 1) Выбрать шаблон (pattern) из файла *.yaml по названию переданной стратегии
       pattern = PATTERNS['Patterns'][strat]
       print(colored(f"\nСтратегия {strat} - '{pattern[0]}': {pattern[1]}", 'magenta', attrs=['bold']))

       rts_code = 'RIU0'                        # код базового актива
       rts_expir_date = '20200917'

       # 2) Собрать модель стратегии: инструменты и страйки в соответствии с шаблоном
       MODEL = Model(rts_code, rts_expir_date, now_baseprice, expir_date, pattern)
       MODEL.get_model_by_pattern()
       #print(f"модель = --- {MODEL.model}")
       #print(f"опционы = --- {MODEL.pos_codes}")


       # 3) Собрать параметры стратегии
       # параметры: {Код инструм.: [тип, (+-)кол-во, цена]} - тип инструмента (1=FUT, 2=CALL, 3=PUT)
       # цену можно не указывать, если выставлять Источник = теоретическая цена
       MODEL.get_parameters_by_model()
       #pos_parameters = {"RI125000BS0A":["3", "22", "0"], "RI125000BG0A":["2", "33", "0"]}
       pos_parameters = MODEL.pos_parameters

       # 4) Собрать строку в QUIK-формате с параметрами стратегии
       strat_file = strat +'_'+ now_baseprice +'_'+ expir_date[4:8] +'.str'
       STRAT = QuikStr(strat_file, rts_code, rts_expir_date, now_baseprice, expir_date, **pos_parameters)    # словарь с переменным количеством аргументов **kwargs
       #print(f"str= {str.strinfo}")


       # III. Сохранить стратегию (портфель стратегий) в отдельный текстовый файл 'Моя_стратегия.str'
       strat_file_path = 'str/' + strat_file
       STRAT.save_strat_to_file(strat_file_path)

       # Вывести содержимое, свериться с файлом квика
       quik_file_path = 'str/Quik_ДвеВершины_fut_short2_117500_0820.str'  #Quik_ДвеВершины_up_125000_0716.str'
       STRAT.check_file_content(strat_file_path, quik_file_path)

   return




if __name__ == '__main__':
    main()

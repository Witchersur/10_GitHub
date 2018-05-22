import os
import glob
import re


def cat_file(fl):  # объединение файлов по шаблону имени
    read_file = glob.glob(fl)  # поиск источников, файлы в нужном шаблоне fl
    lst = ''  # объявляем итоговый текст
    for x in read_file:  # перебор найденных файлов
        with open(x, 'r') as f:  # открываем через контекст, чтобы он сам закрыл файлы
            lst += f.read()  # добавление содержимого файла в общий текст
    return lst  # передача итогового текста


def list_check(chk, cng, garb):  # smb - разделитель текста на строки
    for pattern, replace in cng:  # цикл замен из change[(pattern, replace)]
        r = re.compile(pattern)  # компилируем для быстродействия
        chk = r.sub(replace, chk)  # замена в файле
    # test_ch = open('test_change.csv', 'w')  # 1. вывод для тестирования замен в файл test_change.csv
    # test_ch.write(chk)  # 1. заполняем тестовый файл, объединив все строки в один текст
    chk = chk.splitlines()  # делим файл на список строк
    num_line = 0
    while num_line < len(chk):  # Построчно проходим весь список
        if re.search('удаляем_строку', chk[num_line]):  # проверяем строки файла на 'удаляем_тракт' если да, то
            garb.writelines(chk[num_line] + ',\n')  # заполняем файл с исключениями и
            del chk[num_line]  # удаляем строку в списке
        else:  # если не было удалений, то
            num_line += 1  # на следующую строку
    # test_del = open('test_del.csv', 'w')  # 2. вывод для тестирования удалений в файл test_del.csv
    # test_del.write('\n'.join(chk))  # 2. заполняем итоговый файл, объединив все строки в один текст
    return chk  # возвращаем список без последнего элемента - ''


def inv_opt_hw():
    hw_ne = cat_file('Slot_Information_Report_*.csv')
    garb = open('garb.csv', 'w')  # файл исключений garb.csv
    fin_file = open('hw_inv_opt.txt', 'w')  # выходной файл hw_inv_opt.txt
    change = [('OptiX ', ''),
              ('155/622H\((Metro 1000)\)', r'\1'),
              ('155/622\((Metro 2050)\)', r'\1'),
              ('2500\+\((Metro 3000)\)', r'\1'),
              ('Shelf(\d)[^,]*-(\d{1,3},)', r'\1,\2')]  # убираем не нужное
    hw_ne = list_check(hw_ne, change, garb)  # обрабатываем замены и исключения
    ne_hw = {}  # словарь, ключ 202-102-SLH9037_625;0;03;13OBU1 значение 202-102;OSN 6800
    ln = 10
    while ln < len(hw_ne):
        n = re.split(',', hw_ne[ln])  # делим строку на слова
        if re.match('Metro [1235]0[05]|OSN [123]*500|Metro 6040V2|OSN 3800', n[2]):  # если нет шелфа, то
            ne_hw[n[1] + ';0;' + n[4].zfill(2) + ';' + n[5]] = n[3] + ';' + n[2]  # вставляем шелф ;0;
        elif re.match('OSN [168]800|BWS 1600G', n[2]):  # если есть шелф, то
            ne_hw[n[1] + ';' + n[4] + ';' + n[5].zfill(2) + ';' + n[6]] = n[3] + ';' + n[2]  # вставляем шелф
        else:
            garb.writelines(hw_ne[ln])  # если не нашли, мо в мусор
        del hw_ne[ln]  # удаляем обработанную строку
    garb.close()
    hw_opt = cat_file('Optical_Power_Management_*.csv')  # обработка файла уровней
    garb = open('garb.csv', 'a')  # файл исключений garb.csv
    change = [('Shelf(\d)[^,]*-(\d{1,3},)', r'\1-\2'),
              (',-,', ',,'), (',/,', ',-60.0,'), (',<-35.0,', ',,')]  # убираем не нужное
    hw_opt = list_check(hw_opt, change, garb)  # обрабатываем замены и исключения
    fin_file.writelines('ID_MUX;Тип_MUX;Мультиплексор;Шелф;Слот;Плата;Порт;Порт_СУ;Rx;Tx\n')
    opt = []  # список уровней
    ne = []
    ln = 10
    while ln < len(hw_opt):
        n = re.split(',', hw_opt[ln])  # делим строку на слова
        if re.match('^\d{1,3}$', n[1]):  # если нет шелфа, а только слот, то
            n[1] = '0;' + n[1].zfill(2)  # вставляем шелф 0;слот: 0;02
        elif re.match('^\d-\d{1,3}$', n[1]):  # если шелф-слот есть, то
            sl = re.findall('^(\d)-(\d{1,3})$', n[1])  # ищем шелф-слот
            n[1] = sl[0][0] + ';' + sl[0][1].zfill(2)  # делаем 1-2 вида 1;02
        sl = re.findall('^(\d{1,2})\(([^)]*)\)(.*)$', n[3])  # ищем порт и имя в СУ
        n[3] = sl[0][0].zfill(2) + ';' + sl[0][1] + sl[0][2]  # меняем вид: 1(SDH)-2 на 01;SDH-2
        n[4] = re.sub('\.', ',', n[4])  # для RX меняем . на ,
        n[5] = re.sub('\.', ',', n[26])  # для TX меняем . на ,
        tp = ne_hw[';'.join(n[:3])]  # ищем значение типа мукса и ID по получившемуся ключу
        ne.append(';'.join(n[:3]))  # создаем список найденых ключей, т.е. invent с опт. уровнями
        opt.append(tp + ';' + ';'.join(n[:6]))  # заполняем итоговый список
        # print(';'.join(n[:6]) + '\n')  # для тестирования
        del hw_opt[ln]  # удаляем обработанную строку
    ne = set(ne)  # удаляем повторяющиеся ключи
    for x in ne:  # удаляем из invent значения, которые были в opt
        del ne_hw[x]
    for key, val in ne_hw.items():
        opt.append(val + ';' + key + ';;;;')
    opt = sorted(opt)  # сортируем по ID
    fin_file.write('\n'.join(opt) + '\n')  # заполняем итоговый файл, объединив все строки в один текст
    garb.close()
    fin_file.close()


if os.path.isdir(r'D:\Scripts'):  # проверка, что я дома
    os.chdir(r'D:\Scripts\4_DWDM\Source')  # скрипт запускаю дома
elif os.path.isdir(r'G:\Scripts'):  # проверка, что я на работе
    os.chdir(r'G:\Scripts\4_DWDM\Source')  # скрипт запускаю на работе
inv_opt_hw()


# def invent_hw():
#     hw_ne = cat_file('Slot_Information_Report_*.csv')
#     garb_ne = open('garb_ne.csv', 'w')  # файл исключений garb_ne.csv
#     dwdm_ne = open('hw_dwdm_ne.csv', 'w')  # выходной файл hw_itog_ne.csv
#     sdh_ne = open('hw_sdh_ne.csv', 'w')  # выходной файл hw_itog_ne.csv
#     change = [('OptiX ', ''),
#               ('155/622H\((Metro 1000)\)', r'\1'),
#               ('155/622\((Metro 2050)\)', r'\1'),
#               ('2500\+\((Metro 3000)\)', r'\1'),
#               ('Shelf(\d)[^,]*-(\d{1,3},)', r'\1,\2')]  # убираем не нужное
#     hw_ne = list_check(hw_ne, change, garb_ne)  # обрабатываем замены и исключения и сортируем
#     hw_dwdm = []
#     hw_sdh = []
#     ln = 10
#     while ln < len(hw_ne):  #
#         n = re.split(',', hw_ne[ln])
#         type_ne = n[2]
#         if re.match('Metro [1235]0[05]|OSN [123]*500', type_ne):
#             hw_sdh.append(';'.join(n[1:4]) + ';' + n[4].zfill(2) + ';' + n[5])
#         elif re.match('Metro 6040V2|OSN 3800', type_ne):
#             hw_dwdm.append(';'.join(n[1:3]) + ';0;' + n[4].zfill(2) + ';' + n[5])
#         elif re.match('OSN [168]800|BWS 1600G', type_ne):
#             hw_dwdm.append(';'.join(n[1:5]) + ';' + n[5].zfill(2) + ';' + n[6])
#         else:
#             garb_ne.writelines(hw_ne[ln])
#         del hw_ne[ln]
#     hw_dwdm = sorted(hw_dwdm)
#     hw_sdh = sorted(hw_sdh)
#     dwdm_ne.write('\n'.join(hw_dwdm) + '\n')  # заполняем итоговый файл, объединив все строки в один текст
#     sdh_ne.write('\n'.join(hw_sdh) + '\n')  # заполняем итоговый файл, объединив все строки в один текст
#     garb_ne.close()
#     dwdm_ne.close()
#     sdh_ne.close()

# def opt_hw():
#     hw_opt = cat_file('Optical_Power_Management_*.csv')
#     garb_ne = open('garb_opt.csv', 'w')  # файл исключений garb_ne.csv
#     dwdm_opt = open('hw_dwdm_opt.csv', 'w')  # выходной файл hw_itog_ne.csv
#     sdh_opt = open('hw_sdh_opt.csv', 'w')  # выходной файл hw_itog_ne.csv
#     change = [('Shelf(\d)[^,]*-(\d{1,3},)', r'\1-\2'),
#               (',-,', ',,'), (',/,', ',-60.0,'), (',<-35.0,', ',,'),
#               ]  # убираем не нужное
#     hw_opt = list_check(hw_opt, change, garb_ne)  # обрабатываем замены и исключения и сортируем
#     opt = []
#     ln = 10
#     while ln < len(hw_opt):  #
#         n = re.split(',', hw_opt[ln])
#         if re.match('^\d{1,3}$', n[1]):
#             n[1] = '0;' + n[1].zfill(2)
#         elif re.match('^\d-\d{1,3}$', n[1]):
#             sl = re.findall('^(\d)-(\d{1,3})$', n[1])
#             n[1] = sl[0][0] + ';' + sl[0][1].zfill(2)
#         sl = re.findall('^(\d{1,2})\(([^)]*)\)(.*)$', n[3])
#         n[3] = sl[0][0].zfill(2) + ';' + sl[0][1] + sl[0][2]
#         n[4] = re.sub('\.', ',', n[4])
#         n[5] = re.sub('\.', ',', n[26])
#         opt.append(';'.join(n[:6]))
#         # print(';'.join(n[:6]) + '\n')
#         del hw_opt[ln]
#     opt = sorted(opt)
#     dwdm_opt.write('\n'.join(opt) + '\n')  # заполняем итоговый файл, объединив все строки в один текст
#     # sdh_opt.write('\n'.join(hw_sdh) + '\n')  # заполняем итоговый файл, объединив все строки в один текст
#     garb_ne.close()
#     dwdm_opt.close()
#     sdh_opt.close()
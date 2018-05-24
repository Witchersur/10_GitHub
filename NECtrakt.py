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


def ne_nec():  # обработка файлов nec17_ne.csv и nec18_ne.csv
    nec_ne = cat_file('nec1*_ne.csv')
    garb_ne = open('garb_ne.csv', 'w')  # файл исключений garb_ne.csv
    final_ne = open('nec_itog_ne.csv', 'w')  # выходной файл nec_itog_ne.csv
    change = [('(U-Node_B,)', r'\1,удаляем_строку'),
              (':EXTWB#(\d),U-Node_WB,', r'_\1,U-Node_BBM,'),  # :EXTWB#6 на _6
              ('C-Node S1', 'C-NodeS1'),  # убираем пробел в C-Node S1
              ('\d+,([^_]*)_([^,]*,)([^,]*),', r'\1,\2\3'),
              ('(,99|Name)', r'\1,удаляем_строку')]  # убираем не нужное
    nec_ne = sorted(list_check(nec_ne, change, garb_ne))  # обрабатываем замены и исключения и сортируем
    final_ne.write('\n'.join(nec_ne) + '\n')  # заполняем итоговый файл, объединив все строки в один текст
    garb_ne.close()
    final_ne.close()


def ne_alc():
    alc_ne = cat_file('*alcatel_ne.csv')
    garb_ne = open('garb_ne.csv', 'a')  # файл исключений garb_ne.csv
    final_ne = open('alc_itog_ne.csv', 'w')  # выходной файл alc_itog_ne.csv
    change = [(';', ','), (' ,([^_]*)_([^,]*,)([^,]*).*', r'\1,\2\3'),
              ('(User Label|External Network)', r'\1,удаляем_строку,')]  # убираем не нужное
    alc_ne = sorted(list_check(alc_ne, change, garb_ne))  # обрабатываем замены и исключения и сортируем
    final_ne.write('\n'.join(alc_ne) + '\n')  # заполняем итоговый файл, объединив все строки в один текст
    garb_ne.close()
    final_ne.close()


def itog_ne():
    ne = cat_file('*itog_ne.csv')
    final_ne = open('itog_ne.txt', 'w')  # выходной файл nec_itog_ne.txt
    ne = sorted(ne.splitlines())  # делим файл на список строк и сортируем
    final_ne.write('\n'.join(ne) + '\n')  # обратно объединяем в текст и заполняем итоговый файл
    final_ne.close()


def sec_nec():  # обработка файлов  nec17_sec.csv и nec18_sec.csv
    nec_sec = cat_file('nec1*_sec.csv')
    change = [(',STM1,', ',155M,'),
              (',STM4,', ',622M,'),
              (',STM16,', ',2.5G,'),
              (',STM64,', ',10G,'),
              ('Linear\(Unprotected\)', 'Оптика(без резерва)'),
              ('Linear\(Protected\)', 'Оптика(с резервом)'),
              # ('Wire', 'Коаксиал'),
              (r'\+0/0,', ''),
              (',-,', ',,'),
              ('(?<=,)[^,]*_99,[^,]*,', ',,'),
              ('\n[^,]*,', '\n'),
              ('(Name,|Virtual|Bus)', r'\1,удаляем_строку,')]  # убираем не нужное
    garb_sec = open('garb_sec.csv', 'w')  # файл исключений garb_sec.csv
    final_sec = open('nec_itog_sec.csv', 'w')  # выходной файл nec_itog_sec.csv
    nec_sec = sorted(list_check(nec_sec, change, garb_sec))  # обрабатываем замены и исключения и сортируем
    final_sec.write('\n'.join(nec_sec) + '\n')  # заполняем итоговый файл, объединив все строки в один текст
    garb_sec.close()
    final_sec.close()


def sec_alc():
    alc_sec = cat_file('*alcatel_sec.csv')
    change = [(';', ','),
              (' ,([^,]*,)([^/]*)/([^,]*,)([^/]*)/([^,]*,).*,(STM\d{1,2}),.*', r'\1\6,Оптика(без резерва),\2,\3\4,\5'),
              (',STM1,', ',155M,'),
              (',STM4,', ',622M,'),
              (',STM16,', ',2.5G,'),
              # (',STM64,', ',10G,'),
              ('r01s1b(\d\d)p(\d\d)', r'\1-\2'),
              ('HMS8097_4,[^,]*,', ',,'),
              ('[^,]*_999,[^,]*,', ',,'),
              ('(User Label)', r'\1,удаляем_строку,')]  # убираем не нужное
    garb_sec = open('garb_sec.csv', 'a')  # файл исключений garb_sec.csv
    final_sec = open('alc_itog_sec.csv', 'w')  # выходной файл alc_itog_sec.csv
    alc_sec = sorted(list_check(alc_sec, change, garb_sec))  # обрабатываем замены и исключения и сортируем
    final_sec.write('\n'.join(alc_sec) + '\n')  # заполняем итоговый файл, объединив все строки в один текст
    garb_sec.close()
    final_sec.close()


def itog_sec():
    sc = cat_file('*itog_sec.csv')
    garb_sec = open('garb_sec.csv', 'a')  # файл исключений garb_sec.csv
    final_sec = open('itog_sec.txt', 'w')  # выходной файл nec_itog_sec.txt
    sc = sorted(sc.splitlines())  # делим общий файл на список строк и сортируем
    for x, ln in enumerate(sc):
        if re.search(',,,', ln):  # если есть секция, в которой нет мукса и его порта, то
            sec = re.split(',', ln)  # делим строку на слова
            sec[3:7] = name_mx(sec[3:7], ln)  # ищем через функцию имя мукса из имени секции
            sc[x] = ','.join(sec)  # изменяем строку на полученные значения и склеиваем
    ln = 0
    while ln < len(sc) - 1:  # построчный цикл удаления одной из одинаковых секций из разных СУ
        if re.match('[^,]*', sc[ln]).group(0) == re.match('[^,]*', sc[ln + 1]).group(0):  # одно имя: ln=ln+1
            s1 = re.split(',', sc[ln])  # разбиваем одну строку
            s2 = re.split(',', sc[ln + 1])  # разбиваем следующую строку
            if s1[4] == '' and s1[6] == '':  # если в первой нет портов для обоих муксов, то
                garb_sec.writelines(sc[ln] + '\n')  # заполняем файл с исключениями
                del sc[ln]  # и ее удаляем
            else:
                for i in range(3, 6, 2):  # цикл заполнения порта А, а на следующем шаге порта B
                    if s1[i] != '' and s1[i + 1] == '':  # если для мукса А или B нет порта, то находим в следующей
                        s1[i + 1] = s2[s2.index(s1[i]) + 1]  # строке этот же мукс и по его индексу берем его порт
                        garb_sec.writelines(sc[ln + 1] + '\n')  # заполняем файл с исключениями
                        del sc[ln + 1]  # удаляем вторую секцию
                        sc[ln] = ','.join(s1)  # склеиваем строку через запятую
        else:
            final_sec.writelines(sc[ln] + '\n')  # заполняем финальный файл
            ln += 1  # на следующую строку
    final_sec.writelines(sc[len(sc) - 1] + '\n')  # добавляем в файл последнюю строку, т.к. сравнивали их парами
    garb_sec.close()
    final_sec.close()


def trib_nec():  # поиск трибов в файлах *nec17_user.csv и *nec18_user.csv
    nec_trib = cat_file('*nec1*_user.csv')
    change = [('Pair_surgut-inc,[^,]*,work,[^,]*,', ''),
              ('Pair_surgut-inc,[^,]*,[^,]*,', ''),
              ('[^,]*,[^,]*,work,[^,]*,', ''),  # для ver18, там нет Pair_surgut-inc
              ('[^,]*,\dWay,[^,]*ed', ''),
              (',ON,''|'',OFF,', ','),
              ('\*Comment.*', ''),
              ('\*SNCP.*', ''),
              (',AU4-[^,]*,', ','),
              (':EXTWB#', '_'),
              ('[^,]*_99_6,[^,]*,', ',,,'),
              (',LPT-.-.-(\d{1,2}-\d{1,2},)', r',\1'),
              (',VC12-[sub]*(\d{1,2}-\d{1,2},)', r',\1'),
              (',VC12-E1_(8-\d,)', r',\1'),  # C-NodeS1 материнка
              (',VC12-E1_16-sub-(\d{1,2},)', r',16-\1'),  # C-NodeS1 доп. плата на 16 Е1
              ('(,\d{1,2})-(\d,)', r'\1-0\2'),
              (',(\d-\d{1,2},)', r',0\1'),
              ('(,[AV][UC]4-[^,]*,[^,]*,[AV][UC]4-)', r'\1,удаляем_строку,'),
              ('(,VC\d{1,2}-\d{1,2}VC,)', r'\1,удаляем_строку,'),
              ('(,VC4[-(])', r'\1,удаляем_строку,')]
    garb_trib = open('garb_trib.csv', 'w')  # файл исключений garb_trib.csv
    final_trib = open('nec_itog_trib.csv', 'w')  # выходной файл nec_itog_trib.csv
    nec_trib = sorted(list_check(nec_trib, change, garb_trib))  # обрабатываем замены и исключения и сортируем
    trib = []
    ln = 0
    while ln < len(nec_trib):  # Построчно проходим весь список
        name_trakt = re.match('^([^,]*)(?=,)', nec_trib[ln]).group(0)  # имя тракта
        if re.search('[^,]*,\d\d-\d\d,', nec_trib[ln]):  # если есть мукс,порт вида HMS8095_651,08-02,
            mux = re.findall('[^,]*,\d\d-\d\d,', nec_trib[ln])  # ищем список всех муксов с портами в строке
            for x in mux:  # заполняем выходной файл
                trib.append(x + name_trakt)
        else:
            garb_trib.writelines(nec_trib[ln] + ',\n')  # если не нашли, то в мусорный файл
        del nec_trib[ln]  # удалить обработанную строку в списке
    trib = sorted(trib)  # сортируем итоговый список
    final_trib.write('\n'.join(trib) + '\n')  # заполняем итоговый файл, объединив все строки в один текст
    garb_trib.close()
    final_trib.close()


def trib_alc():  # поиск трибов в файле *_report_on_selected_out.txt
    alc_trib = cat_file('*_report_on_selected_out.txt')
    change = [('\*{5} SPARE ROUTE[^#]*#+\n', ''),  # удаляем всю резервную трассу
              ('\*{5} MAIN ROUTE[^\n]*\n', ''),  # удаляем строку с MAIN ROUTE
              ('PATH', ''),  # удаляем слово PATH
              ('=+\n', ''),  # удаляем строки ========
              ('\t', ''),  # удаляем табуляцию
              ('\n+', '\n'),  # удаляем пустые строки
              ('#+\n', ''),  # удаляем строки ########
              ('(?<=\n)[^\s]*\s\s\s\d\d/\d/\d\.\d\s+\n', ''),  # удаляем строки с tu вида 05/1/5.1
              ('([^/]*)/r01s1b(\d\d)p(\d\d)c01\n', r'\1,\2-\3\n')]  # меняем мукс/порт на HMS8095_651,08-02
    garb_trib = open('garb_trib.csv', 'a')  # файл исключений garb_trib.csv
    final_trib = open('alc_itog_trib.csv', 'w')  # выходной файл alc_itog_trib.csv
    alc_trib = list_check(alc_trib, change, garb_trib)  # обрабатываем замены и исключения
    trib = []
    ln = 0
    while ln < len(alc_trib):  # Построчно проходим весь список
        # print(alc_trib[ln])
        name_trakt = alc_trib[ln]  # имя тракта
        for x in range(2):
            if re.match('[^,]*,\d\d-\d\d', alc_trib[ln + 1]):  # если есть мукс,порт вида HMS8095_651,08-02
                trib.append(alc_trib[ln + 1] + ',' + name_trakt)  # добавляем в список мукс и тракт
            else:
                garb_trib.writelines(alc_trib[ln + 1] + ',' + name_trakt + ',\n')  # если не нашли, то в мусорный файл
            del alc_trib[ln + 1]  # удаляем строку мукса
        del alc_trib[ln]  # удалить обработанную строку имени тракта в списке
    trib = sorted(trib)  # сортируем итоговый список
    final_trib.write('\n'.join(trib) + '\n')  # заполняем итоговый файл, объединив все строки в один текст
    garb_trib.close()
    final_trib.close()


def itog_trib():
    num_port = ('01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17',
                '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34',
                '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51',
                '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63')
    trib = cat_file('*itog_trib.csv')
    exl_mux = cat_file('MUX.csv')  # файл MUX.csv - экспорт листа MUX файла INC-100MS
    garb_trib = open('garb_trib.csv', 'a')  # файл исключений garb_trib.csv
    final_trib = open('itog_trib.txt', 'w')  # выходной файл itog_trib.txt
    change = [(';', ','), ('(Географическое название)', r'\1,удаляем_строку,')]  # убираем не нужное
    exl_mux = sorted(list_check(exl_mux, change, garb_trib))  # обрабатываем замены и исключения и сортируем
    trib_trakt = {}
    trib = sorted(trib.splitlines())  # делим файл на список строк
    ln = 0
    while ln < len(trib):  # Построчно проходим весь список
        s = re.split(',', trib[ln])  # делим строку на слова
        trib_trakt[s[0] + ',' + s[1]] = s[2]  #
        del trib[ln]
    all_port = 0
    for line_mux in exl_mux:  # Построчно проходим весь файл
        mux = line_mux.split(',')  # заполняем список поделив строку по запятым
        type_mux = mux[2]  # тип мукса
        name_mux = (mux[0] + '_' + mux[1] + ',')  # имя мукса
        list_slot = list(filter(None, mux[3:21]))  # список установленных плат, удаляем пустые
        sl = 0
        while sl < len(list_slot):  # проходим по рабочим платам
            if type_mux in {'U-Node_BBM', 'U-Node_WBM'}:  # выбираем кол-во портов от типа мукса
                all_port = 63
            elif type_mux in {'C-Node', 'V-Node', 'V-NodeS'}:
                all_port = 32
            elif type_mux == '1660SM':
                all_port = 21
            elif type_mux == 'C-NodeS1' and list_slot[sl] == '16':
                all_port = 16
            elif type_mux == 'C-NodeS1' and list_slot[sl] == '08':
                all_port = 8
            for i in range(all_port):
                mux_port = (name_mux + list_slot[sl] + '-' + num_port[i])  # ключ (HMS8095_651,08-01)
                if trib_trakt.get(mux_port):  # если получили значение по ключу из словаря, то
                    final_trib.writelines(mux_port + ',' + trib_trakt[mux_port] + '\n')  # записываем в файл
                    del trib_trakt[mux_port]  # удаляем найденое значение из словаря
                else:
                    final_trib.writelines(mux_port + ',Свободен\n')  # если не нашли, то свободен
            sl += 1  # следующая плата
    final_trib.close()


def name_mx(mx, sec):  # ищем имя мукса из имени секций, mx-список муксы и порты; sec-текст секций
    s = []
    mxs = re.findall('(\w+)-(\w+)\DMS\d+', sec)  # из секций получаем список кортежей из пар названий муксов
    for num_sec in mxs:  # выделяем из кортежей список названий муксов
        for x in num_sec:  # переносим пары названий муксов в новый общий список s
            s.append(x)
    mxs = []
    for num_mx, name in enumerate(s):  # в список mxs помещаем уникальное имя мукса А и В (они по концам секций)
        if s.count(name) == 1:  # если имя мукса встречается в списке муксов только раз, то
            mxs.append(name)  # добавляем его в новый список
    if mx[0] == '' and mx[2] == '' and len(mxs) == 2:  # если мукс А и B пустые, то
        mx[0] = mxs[0]  # мукс А равен первому имени мукса в секции, а
        mx[2] = mxs[1]  # мукс B равен второму имени мукса в секции
    elif mx[0] == '' and mx[2] != '' and len(mxs) == 2:  # если нет только мукса А, то
        if re.match('^\w+_\w+_\d$', mx[2]):
            ext = re.sub('^(\w+_\w+)_\d$', r'\1', mx[2])
            mxs.remove(ext)
        else:
            mxs.remove(mx[2])  # удаляем из списка мукс B, т.е. там останется только мукс А
        mx[0] = mxs[0]  # мукс А равен оставшемуся в списке муксу А
    elif mx[2] == '' and mx[0] != '' and len(mxs) == 2:  # если нет только мукса B, то
        if re.match('^\w+_\w+_\d$', mx[0]):
            ext = re.sub('^(\w+_\w+)_\d$', r'\1', mx[0])
            mxs.remove(ext)  # удаляем из списка мукс А, т.е. там останется только мукс B
        else:
            mxs.remove(mx[0])  # удаляем из списка мукс А, т.е. там останется только мукс B
        mx[2] = mxs[0]  # мукс B равен оставшемуся в списке муксу B
    return mx


def port_nec(lv, ty, mx):
    # замена порта мукса согласно шаблону, относительно типа тракта
    for p in range(1, len(mx), 2):  # цикл прохода по списку муксов и портов
        if lv == 140 and ty == 2:  # тракты 140М, 2way
            mh = re.match(r'(\d\d)$', mx[p])
            if mh:  # замена для ЧГ '1' на 'VC4_01'
                mx[p] = 'VC4_' + mh.group(0)
            mh = re.findall(r'^VC4-....-(\d{1,2})$', mx[p])
            if mh:  # замена 'VC4-main-2 или VC4-sub3-2' на 'VC4_02'
                mx[p] = 'VC4_' + mh[0][0].zfill(2)
            mh = re.findall(r'^AU4-\d-\d-\d+-\d+-(\d{1,2})$', mx[p])
            if mh:  # замена 'AU4-1-1-10-5-1' на 'VC4_02'
                mx[p] = 'VC4_' + mh[0][0].zfill(2)
        elif lv == 150 and ty == 2:  # тракты GE 150М, 2way
            mh = re.findall(r'^(VC4-\d{1,2}-)(\d+)$', mx[p])
            if mh:  # замена для GE 'VC4-6-1' на 'VC4-6-AU01'
                mx[p] = mh[0][0] + 'AU' + mh[0][1].zfill(2)
            mh = re.findall(r'^AU4-\d-\d-\d+-\d-(\d{1,2})$', mx[p])
            if mh:  # замена для AU4 'AU4-1-1-4-1-4' на 'VC4_04'
                mx[p] = 'VC4_' + mh[0].zfill(2)
        elif lv == 0:  # тракты 2М, 2way
            mh = re.findall(r'^(\d\d)-(\d)-(\d)-(\d)$', mx[p])
            if mh:  # замена для VC12 '01-3-7-3' на 'VC4_01.TS_373'
                mx[p] = 'VC4_' + mh[0][0] + '.TS_' + mh[0][1] + mh[0][2] + mh[0][3]

            mh = re.findall(r'^[AV][UC]4-\d-\d-\d+-\d+-(\d{1,2})-(\d)-(\d)-(\d)$', mx[p])
            if mh:  # 'AU4-1-1-9-3-1-3-7-3' на ''
                mx[p] = ''
            # if mh:  # 'AU4-1-1-9-3-1-3-7-3' на 'VC4_01.TS_373'
            #     mx[p] = 'VC4_' + mh[0][0].zfill(2) + '.TS_' + mh[0][1] + mh[0][2] + mh[0][3]
            mh = re.findall(r'^VC12-....-(\d{1,2})-(\d)-(\d)-(\d)$', mx[p])
            if mh:  # 'VC12-sub1-2-1-1-1 или VC12-main-2-1-2-1' на ''
                mx[p] = ''
            # if mh:  # 'VC12-sub1-2-1-1-1 или VC12-main-2-1-2-1' на 'VC4_01.TS_373'
            #     mx[p] = 'VC4_' + mh[0][0].zfill(2) + '.TS_' + mh[0][1] + mh[0][2] + mh[0][3]
            mh = re.findall(r'^LPT-\d-\d-(\d{1,2})-(\d{1,2})$', mx[p])
            if mh:  # 'LPT-1-6-8-7' на '08-07'
                mx[p] = mh[0][0].zfill(2) + '-' + mh[0][1].zfill(2)
            mh = re.findall(r'^VC12-[sub]*(\d{1,2})-(\d{1,2})$', mx[p])
            if mh:  # 'VC12-[sub]4-7' на '04-07'
                mx[p] = mh[0][0].zfill(2) + '-' + mh[0][1].zfill(2)
            mh = re.findall(r'^VC12-E1_(\d{1,2})-[sub-]*(\d{1,2})$', mx[p])
            if mh:  # CnodeS1 'VC12-E1_8-1' или VC12-E1_16-sub-3 на '08-01'
                mx[p] = mh[0][0].zfill(2) + '-' + mh[0][1].zfill(2)
        elif 0 < lv < 64 and ty == 2:  # тракты 2М FE, 2way
            mh = re.findall(r'^(VC12-[sub]*)(\d{1,2})-(\d{1,2})-(\d{1,2})$', mx[p])
            if mh:  # 'VC12-sub4-1-6' на 'VC12-sub04-AU1_06'
                mx[p] = mh[0][0] + mh[0][1].zfill(2) + '-AU' + mh[0][2].zfill(2) + "_" + mh[0][3].zfill(2)
            mh = re.findall(r'^[AV][UC]4-\d-\d-\d+-\d+-(\d{1,2})-(\d)-(\d)-(\d)$', mx[p])
            if mh:  # 'AU4-1-1-9-3-1-3-7-3' на 'VC4_01.TS_373'
                mx[p] = 'VC4_' + mh[0][0].zfill(2) + '.TS_' + mh[0][1] + mh[0][2] + mh[0][3]
            mh = re.findall(r'^(VC3-[sub]*)(\d{1,2})-(\d{1,2})-(\d{1,2})$', mx[p])
            if mh:  # 'VC3-sub3-1-1' на 'VC3-sub03-AU01_01'
                mx[p] = mh[0][0] + mh[0][1].zfill(2) + '-AU' + mh[0][2].zfill(2) + "_" + mh[0][3].zfill(2)
            mh = re.findall(r'^(VC12-100BT2)-(\d{1,2})-(\d{1,2})$', mx[p])
            if mh:  # CnodeS1 'VC12-100BT2-1-20' на 'VC12-AU01_20'
                mx[p] = mh[0][0] + '-AU' + mh[0][1].zfill(2) + "_" + mh[0][2].zfill(2)
    return mx


def tu_nec(lv, ty, s):
    num = ('01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17',
           '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34',
           '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51',
           '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63')
    tu = ('111', '112', '113', '121', '122', '123', '131', '132', '133', '141', '142', '143', '151', '152', '153',
          '161', '162', '163', '171', '172', '173', '211', '212', '213', '221', '222', '223', '231', '232', '233',
          '241',
          '242', '243', '251', '252', '253', '261', '262', '263', '271', '272', '273', '311', '312', '313', '321',
          '322',
          '323', '331', '332', '333', '341', '342', '343', '351', '352', '353', '361', '362', '363', '371', '372',
          '373')
    tu_num = dict(zip(tu, num))
    num_tu = dict(zip(num, tu))
    for x in range(0, len(s), 2):
        if (lv == 140 or lv == 150) and ty == 2:  # тракты 140М, 150М 2way
            s[x + 1] = 'VC4_' + s[x + 1] + '-' + s[x + 1]
        elif lv == 0:  # тракты VC12, VC3, 2way
            mh = re.findall(r'^(\d\d)-(\d)-(\d)-(\d)$', s[x + 1])
            if mh:  # VC12
                tu12 = mh[0][1] + mh[0][2] + mh[0][3]
                s[x + 1] = 'VC4_' + mh[0][0] + '.TS_' + tu12 + '-' + mh[0][0] + '-0-0-' + tu_num[tu12]
            mh = re.findall(r'^(\d\d)-(\d)$', s[x + 1])
            if mh:  # VC3
                s[x + 1] = 'VC4_' + mh[0][0] + '.TS_' + mh[0][1] + '-' + mh[0][0] + '-' + mh[0][1].zfill(2)
        elif 0 < lv < 64 and ty == 2:  # тракты 2М или 48М FE, 2way
            mh = re.findall(r'^(\d\d)-1$', s[x + 1])
            if mh:  # VC3-1
                s[x + 1] = 'VC4_' + mh[0] + '.TS_1-' + mh[0] + '-01'
            mh = re.findall(r'^(\d\d)-22$', s[x + 1])
            if mh:  # VC3-2
                s[x + 1] = 'VC4_' + mh[0] + '.TS_2-' + mh[0] + '-02'
            mh = re.findall(r'^(\d\d)-43$', s[x + 1])
            if mh:  # VC3-3
                s[x + 1] = 'VC4_' + mh[0] + '.TS_3-' + mh[0] + '-03'
            mh = re.findall(r'^(\d\d)-\d-\d-(\d{1,2})$', s[x + 1])
            if mh:  # VC12
                tu12 = num_tu[mh[0][1].zfill(2)]
                s[x + 1] = 'VC4_' + mh[0][0] + '.TS_' + tu12 + '-' + mh[0][0] + '-0-0-' + tu_num[tu12]
    return s


def trakt_nec17usi():
    change = [(',[P-]*Commissioned,', ',ос,'),
              (',Reserved,', ',бр,'),
              (',,+', ','), ('  +', ' '),
              ('[^,]*,Virtual\d+,[^,]*,[^,]*,|[^,]*,[^,]*<>[^,]*,[^,]*,[^,]*,', ''),
              (',Vi[r]*\d+,[^,]*', ',,'),
              (':EXTWB#', '_'), (',ON,|,OFF,', ','),
              ('(,work),(\d)(?=\D)', r'\1,0\2'),
              ('Pair_surgut-inc,([^,]*,)work,', r'\1'),
              ('Pair_surgut-inc,[^,]*,[^,]*,', ''),
              (r'\*(SNCP-\d,)[^,]*,[^,]*,', r'\1'),
              ('(?<=,)[^,]*_99_\d,[^,]*,', ',,'),
              (r',VC4-1VC\(150M\),', ',150,'),
              (r',VC4\(140M\),', ',140,'),
              (r',VC3-(\d)VC,', r',\1,'),
              (',VC3,', ',0,'),
              (r',VC12-(\d+)VC,', r',\1,'),
              (r',VC12\(2M\),', ',0,'),
              (',PtoP,2Way,', ',2,'),
              (',PtoP,1Way,', ',2,'),
              (',Broadcast,1Way,', ',1,'),
              ('Planned', ',удаляем_строку,')]  # замены
    trakt_nec('*nec17_user.csv', 'nec17_itog_trakt.csv', change)


def trakt_nec18usi():
    change = [(',[P-]*Commissioned,', ',ос,'),
              (',Reserved,', ',бр,'),
              (',,+', ','), ('  +', ' '),
              ('Virtual\d+,[^,]*,[^,]*,|[^,]*<>[^,]*,[^,]*,[^,]*,', ''),
              (',Vi[r]*\d+,[^,]*', ',,'),
              (':EXTWB#', '_'), (',ON,|,OFF,', ','),
              ('(,work),(\d)(?=\D)', r'\1,0\2'),
              ('([^,]*,)work,', r'\1'),
              ('(,[об][ср],)[^,]*,[^,]*,([^,]*,[^,]*,)[^,]*,[^,]*,', r'\1\2'),
              (r'\*(SNCP-\d,)[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,', r'\1'),
              ('(?<=,)[^,]*_99_\d,[^,]*,', ',,'),
              (r',VC4-1VC\(150M\),', ',150,'),
              (r',VC4\(140M\),', ',140,'),
              (r',VC3-(\d)VC,', r',\1,'),
              (',VC3,', ',0,'),
              (r',VC12-(\d+)VC,', r',\1,'),
              (r',VC12\(2M\),', ',0,'),
              (',PtoP,2Way,', ',2,'),
              (',PtoP,1Way,', ',2,'),
              (',Broadcast,1Way,', ',1,'),
              ('Planned', ',удаляем_строку,')]  # замены
    trakt_nec('*nec18_user.csv', 'nec18_itog_trakt.csv', change)


def trakt_nec(source, destin, chng):
    nec_tr = cat_file(source)  # найти файл по шаблону
    garb_trakt = open('garb_trakt.csv', 'w')  # файл исключений garb_trakt.csv
    test_trakt = open('test_trakt.csv', 'w')  # вывод только занятых портов в файл test_trakt.scv
    final_trakt = open(destin, 'w')  # выходной файл *_itog_trakt.csv
    # nec_tr = sorted(list_check(nec_tr, chng, garb_trakt))  # обрабатываем замены, исключения и сортируем список
    nec_tr = list_check(nec_tr, chng, garb_trakt)  # обрабатываем замены и исключения
    test_trakt.write('\n'.join(nec_tr) + '\n')  # заполняем итоговый файл, объединив все строки в один текст
    trakt = []
    for ln in nec_tr:  # Построчно проходим весь файл
        bg = re.split(',', ln)
        lvl = int(bg[1])  # уровень тракта
        tp = int(bg[2])  # тракта PtoP или Broadcast
        com = bg[-1]  # сохраняем комментарий
        mux = [bg[4], bg[5], bg[6], bg[7]]  # мукс А, порт А, мукс В, порт В
        if tp == 1:  # если тракт Broadcast
            i = bg.index(r'*Z-2')  # ищем *Z-2
            mux.append(bg[i + 2])  # добавляем в mux мукс Z
            mux.append(bg[i + 3])  # добавляем в mux порт Z
            bg[i:i + 4] = []  # удаляем мукс и порт Z
            ln = bg[2 + len(mux):-2]  # присваиваем только секции
        else:
            ln = bg[8:-2]  # присваиваем только секции, если нет муксов Z
        sncp = []  # сброс списка для нового тракта
        if re.search('SNCP-\d', ','.join(ln)):  # если есть SNCP, то
            x = 0
            while x < len(ln):  # проходим по строке
                if re.match('SNCP-\d', ln[x]):  # находим SNCP
                    sncp.append(int(x))  # добавляем в список индекс списка (номер места) SNCP в строке
                    del ln[x]  # обновляем строку, оставляем только секции с tu (включая резервные)
                else:
                    x += 1
            sec_work = ','.join(ln[:sncp[0]])  # секции основного тракта, если есть SNCP
        else:
            sec_work = ','.join(ln)  # секции основного тракта, если нет SNCP
        if 1 < lvl < 65 and tp == 2:  # тракты 2М n-FE, 2way, цикл разделения на n отдельных трактов
            fe1 = re.split('\|', bg[5])  # разбить на список порты n-FE мукс-А
            fe2 = re.split('\|', bg[7])  # разбить на список порты n-FE мукс-B
            if len(fe1) > len(fe2):  # если один из списков пуст, то заполняем его '' посчитав первый список
                fe2 = [''] * len(fe1)
            elif len(fe1) < len(fe2):
                fe1 = [''] * len(fe2)
            ln = ','.join(ln)
            fms = []  # заводим список для итога секций n-FE
            if re.search(',\d\d-\d{1,2}(?=\|)', ln):  # n-VC3
                ln = re.sub('(,\d\d-)(\d{1,2})(?=\|)', r'\1|\2', ln)  # VC3 ,01-22|43 на ,01-|22|43
                mhs = re.findall(r'([^,]*,\d\d-)(?=\|)', ln)  # VC3 поиск всех HMS8097_4-HMS9093_651_MS1,01-
            else:
                ln = re.sub(r'(,\d\d-\d-\d-)(\d{1,2})(?=\|)', r'\1|\2', ln)  # VC12 ,1-3-6-60|61 на ,1-3-6-|60|61
                mhs = re.findall(r'([^,]*,\d\d-\d-\d-)(?=\|)', ln)  # VC12 поиск всех HMS8097_4-HMS9093_651_MS1,1-3-6-
            mhn = re.findall(r'(?<=\|)(\d{1,2})', ln)  # поиск всех |60|61
            for a in range(lvl):  # цикл пройти всё количество трактов n-FE
                fms.extend([bg[4] + ',' + fe1[a], bg[6] + ',' + fe2[a]])  # доб. муксы,порты для одного n-FE
                for b in range(len(mhs)):  # цикл пройти все секции отдельно для каждого тракта n-FE
                    fms.append(mhs[b] + mhn[(b * lvl) + a])  # добавляем секции и tu12 для каждого тракта n-FE
            for a in range(lvl):  # цикл создания отдельно тракта для каждого n-FE
                ln = ','.join(bg[:4]) + ',' + ','.join(fms[0:len(mhs) + 2])
                del fms[:len(mhs) + 2]
                bg = re.split(',', ln)  # список основной трассы тракта
                mux = [bg[4], bg[5], bg[6], bg[7]]  # муксы и порты
                sc = bg[8:]  # муксы и порты
                if mux[0] == '' or mux[2] == '':  # если нет мукса А или В, то
                    mux = name_mx(mux, sec_work)  # ищем через функцию имя мукса из имени секции
                port_nec(lvl, tp, mux)  # меняем вид порты муксов
                sc = tu_nec(lvl, tp, sc)  # меняем вид tu
                line = ','.join(bg[:4]) + ',' + ','.join(mux) + ',' + ','.join(sc) + ',' + com + '\n'  # отдельный тракт
                trakt.append(line)  # добавляем в итоговый список основную трассу
        else:  # тракт не составной
            if mux[0] == '' or mux[2] == '':  # если нет мукса А или В, то
                mux = name_mx(mux, sec_work)  # ищем через функцию имя мукса из имени секции
            port_nec(lvl, tp, mux)  # меняем вид порты муксов
            ln = tu_nec(lvl, tp, ln)  # меняем вид tu
            if len(sncp) > 0:  # если есть sncp, то
                for x, res in enumerate(sncp):
                    ln.insert(res + x, 'SNCP-' + str(x + 1))  # вставляем из списка SNCP-\d в строку
            line = ','.join(bg[:4]) + ',' + ','.join(mux) + ',' + ','.join(ln) + ',' + com + '\n'  # объединяем данные
            trakt.append(line)  # добавляем в итоговый список основную трассу
        # print(name + '\n')
    for x in trakt:
        final_trakt.writelines(x)  # заполняем итоговый файл, объединив все строки в один текст
    test_trakt.close()
    final_trakt.close()


def itog_trakt():
    nec17usi = open('nec17_itog_trakt.csv', 'r')  # вывод только занятых портов в файл nec17_itog_trakt.csv
    nec18usi = open('nec18_itog_trakt.csv', 'r')  # вывод только занятых портов в файл nec18_itog_trakt.csv
    final_trakt = open('itog_trakt.txt', 'w')  # вывод только занятых портов в файл itog_trakt.txt
    garb_trakt = open('garb_trakt.csv', 'a')  # файл исключений garb_ne.csv
    nec1 = nec17usi.read().splitlines()
    nec2 = nec18usi.read().splitlines()
    nec17usi.close()
    nec18usi.close()
    l2 = 0
    while l2 < len(nec2):  # доп. тракты
        bg2 = re.split(',', nec2[l2])
        ln2 = bg2[8:-1]  # выделяем секции и tu в список ln2
        sc2 = []  # список пар 'секция,tu' для доп. трактов
        x = 0
        while x < len(ln2):  # готовим список пар 'секция,tu' для доп. трактов
            if re.match('VC4_', ln2[x+1]):  # находим 'VC4_'
                sc2.append(ln2[x] + ',' + ln2[x+1])  # добавляем в список пару 'секция,tu'
                del ln2[x+1]  # удаляем 'VC4_*'
                del ln2[x]  # удаляем секцию
            else:
                del ln2[x]  # удаляем sncp
        lensc2 = len(sc2)
        for y in sc2:
            for l1, str1 in enumerate(nec1):  # основные тракты
                if y in str1:
                    bg1 = re.split(',', str1)
                    com1 = ','.join(bg1[-1:])  # сохраняем комментарий
                    ln1 = bg1[8:-1]  # выделяем секции и tu в список ln1
                    sc1 = []  # список пар 'секция,tu' для основных трактов
                    a = 0
                    while a < len(ln1):  # готовим список пар 'секция,tu' для основных трактов
                        if re.match('VC4_', ln1[a + 1]):  # находим 'VC4_'
                            sc1.append(ln1[a] + ',' + ln1[a + 1])  # добавляем в список пару 'секция,tu'
                            del ln1[a+1]  # удаляем 'VC4_*'
                            del ln1[a]  # удаляем секцию
                        else:
                            sc1.append(ln1[a])  # добавляем в список sncp
                            del ln1[a]  # удаляем sncp
                    sc1_ind = 0  # индекс места найденной пары 'секция,tu' в списке основного тракта
                    if bg1[4] == bg2[4] or bg1[6] == bg2[6]:  # муксы доп и осн тракта в одном месте
                        if bg1[4] == bg2[4] and bg1[5] == '':  # если у мукс А нет порта, то
                            bg1[5] = bg2[5]  # порт мукса А осн равен порту мукса А доп тракта
                        elif bg1[6] == bg2[6] and bg1[7] == '':  # если у мукс В нет порта, то
                            bg1[7] = bg2[7]  # порт мукса В осн равен порту мукса В доп тракта
                        x = 0
                        while x < len(sc2):  # ищем совпадения 'секция,tu' в списке осн и доп тракта
                            if sc2[x] in sc1:  # если доп 'секция,tu' есть в осн 'секция,tu', то
                                sc1_ind = sc1.index(sc2[x])  # запоминаем место в осн списке
                                del sc2[x]  # удаляем найденную доп 'секция,tu'
                            else:
                                x += 1  # иначе переходим далее по списку доп
                        if len(sc2) == 0:  # если все доп 'секция,tu' были найдены, то
                            garb_trakt.writelines(nec2[l2] + '\n')
                            del nec2[l2]  # удаляем весь доп тракт
                            nec1[l1] = ','.join(bg1[:8]) + ',' + ','.join(sc1[:]) + ',' + com1  # обновляем осн строку
                            break
                        else:
                            for x in range(len(sc2)):  # не найденные секции добавляем в осн список
                                sc1.insert(sc1_ind + x + 1, sc2[x])  # вставляем по индексу справа
                            nec1[l1] = ','.join(bg1[:8]) + ',' + ','.join(sc1[:]) + ',' + com1  # обновляем осн строку
                            l2 += 1
                            break
                    elif bg1[6] == bg2[4] or bg1[4] == bg2[6]:  # муксы доп и осн тракта в разных местах
                        if bg1[6] == bg2[4] and bg1[7] == '':  # если у мукс B нет порта, то
                            bg1[7] = bg2[5]  # порт мукса B осн равен порту мукса А доп тракта
                        elif bg1[4] == bg2[6] and bg1[5] == '':  # если у мукс A нет порта, то
                            bg1[5] = bg2[7]  # порт мукса A осн равен порту мукса B доп тракта
                        for x in range(len(sc2)-1, -1, -1):  # ищем 'секция,tu' в списке осн и доп тракта с конца
                            if sc2[x] in sc1:  # если доп 'секция,tu' есть в осн 'секция,tu', то
                                sc1_ind = sc1.index(sc2[x])  # запоминаем место в осн списке
                                del sc2[x]  # удаляем найденную доп 'секция,tu'
                        if len(sc2) == 0:  # если все доп 'секция,tu' были найдены, то
                            garb_trakt.writelines(nec2[l2] + '\n')
                            del nec2[l2]  # удаляем весь доп тракт
                            nec1[l1] = ','.join(bg1[:8]) + ',' + ','.join(sc1[:]) + ',' + com1  # обновляем осн строку
                            break
                        else:
                            for x in range(len(sc2)):  # не найденные секции добавляем в осн список
                                sc1.insert(sc1_ind - x - 1, sc2[x])  # вставляем по индексу слева
                            nec1[l1] = ','.join(bg1[:8]) + ',' + ','.join(sc1[:]) + ',' + com1  # обновляем осн строку
                            l2 += 1
                            break
        # print(nec2[l2] + '\n')
        if len(sc2) == lensc2:
            l2 += 1
    nec1 = sorted(nec1 + nec2)  # сортируем итоговый список
    final_trakt.write('\n'.join(nec1) + '\n')  # заполняем итоговый файл, объединив все строки в один текст
    garb_trakt.close()
    final_trakt.close()


if os.path.isdir(r'D:\Scripts'):  # проверка, что я дома
    os.chdir(r'D:\Scripts\1_NEC\Source')  # скрипт запускаю дома
elif os.path.isdir(r'G:\Scripts'):  # проверка, что я на работе
    os.chdir(r'G:\Scripts\1_NEC\Source')  # скрипт запускаю на работе
# ne_nec()
# ne_alc()
# itog_ne()
#
# sec_nec()
# sec_alc()
# itog_sec()
#
# trib_nec()
# trib_alc()
# itog_trib()
#
# trakt_nec17usi()
# trakt_nec18usi()
itog_trakt()

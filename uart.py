from itertools import count
import serial
from serial.tools import list_ports
import time
import struct
import plot
from plot import UartPlot
import numpy as np
import os


class UartHardware:
    def __init__(self, verbose=True):
        """
        Инициализация класса MyUart, позволяющего просто добавлять новые порты, и работать с ними
        :param verbose: True - есть поясняющие print, False - без подсказок
        """
        self.verbose = verbose
        self.port = serial.Serial()
        self.synchronization_time = 1
        self.time_list = []  # массив времени прихода данных
        self.start_read_time = 0

    @staticmethod
    def get_uarts():
        """
        Вывод найденых компортов
        :return: возвращяет список найденых портов
        """
        ports = list_ports.comports()
        count = 0
        if ports:
            print("Доступные порты:")
            while ports:
                print("порт номер", count, ":", ports.pop().device)
                count += 1
            print("")
            return ports
        else:
            print("нет портов")
            return 0

    def connect_uart(self, uart_n: [str, int] = 0, speed=115200, synchronization_time=0.1):
        """
        Функция подключается к конкретному компорту
        :param uart_n: можно передать номер в списке полученному из функции get_uarts, так же можно ввести
        напрямую строку, например "COM7", по умолчанию берется первый найденый порт
        :param speed: бодрейт: 9600, 115200 и т.д. по умолчанию 115200
        :param synchronization_time: пауза между данными для синхронизации
        """
        self.synchronization_time = synchronization_time
        ports = list_ports.comports()
        if self.verbose:
            self.get_uarts()

        if ports:
            # if type(uart_n) == str:  # если пришел номер порта строкой, то переводим его в номер в списке
            if isinstance(uart_n, str):
                for i, p in enumerate(ports):
                    if uart_n == p.device:
                        uart_n = i
            if uart_n > len(ports) - 1:
                print("номера порта {} не существует".format(uart_n))
            else:
                if self.verbose:
                    print("подключение к порту:", ports[uart_n].device)
                try:
                    self.port = serial.Serial(ports[uart_n].device, speed)
                    # self.port.flushInput()
                except Exception:
                    print("порт недоступен")
                    return False
                else:
                    if self.verbose:
                        print("подключение успешно")
                    return True
        else:
            if not self.verbose:
                print("нет портов")

    def disconnect_uart(self):
        """
        Отключение от подключенного компорта
        """
        try:
            self.port.close()
            if self.verbose:
                print("порт отключен")
        except Exception:
            print("ошибка закрытия порта")

    def get_data(self, in_data_count=1000):
        self.port.flushInput()
        wait_synchronization = 1
        t = 0
        print("Ждем паузы в данных для синхронизации")
        while wait_synchronization:
            if self.port.inWaiting() != 0:
                t = time.clock()
                self.port.flushInput()

            if (time.clock() - t) > self.synchronization_time:
                self.port.flushInput()
                wait_synchronization = 0
                print("синхронизация")

        while self.port.inWaiting() == 0:
            self.start_read_time = time.clock()

        data = self.port.read()
        while in_data_count - len(data) > 0:
            data = data + self.port.read()
            self.time_list.append(time.clock())
        return data


class UartParser:
    def __init__(self, verbose=True):
        self.verbose = verbose
        self.str_len = 0
        self.data_list = []  # список переменных в одной пачке данных
        self.name_list = []

    def add_u8(self, name=""):
        self.str_len += 1
        self.data_list.append([0, 1, 'u8'])
        self.name_list.append(name)

    def add_u16(self, name=""):
        self.str_len += 2
        self.data_list.append([0, 2, 'u16'])
        self.name_list.append(name)

    def add_u32(self, name=""):
        self.str_len += 4
        self.data_list.append([0, 4, 'u32'])
        self.name_list.append(name)

    def add_s8(self, name=""):
        self.str_len += 1
        self.data_list.append([0, 1, 's8'])
        self.name_list.append(name)

    def add_s16(self, name=""):
        self.str_len += 2
        self.data_list.append([0, 2, 's16'])
        self.name_list.append(name)

    def add_s32(self, name=""):
        self.str_len += 4
        self.data_list.append([0, 4, 's32'])
        self.name_list.append(name)

    def add_float(self, name=""):
        self.str_len += 4
        self.data_list.append([0, 4, 'float'])
        self.name_list.append(name)

    def raw_pars(self, data: bytes, length):
        val_count = 0
        out_list = []
        for j in range(length):
            line = []
            for i in range(len(self.data_list)):
                val = data[val_count:val_count + self.data_list[i][1]]
                if self.data_list[i][2] == 'u8':
                    line.append(struct.unpack('B', val)[0])
                if self.data_list[i][2] == 'u16':
                    line.append(struct.unpack('H', val)[0])
                if self.data_list[i][2] == 'u32':
                    line.append(struct.unpack('I', val)[0])
                if self.data_list[i][2] == 's8':
                    line.append(struct.unpack('b', val)[0])
                if self.data_list[i][2] == 's16':
                    line.append(struct.unpack('h', val)[0])
                if self.data_list[i][2] == 's32':
                    line.append(struct.unpack('i', val)[0])
                if self.data_list[i][2] == 'float':
                    line.append(struct.unpack('f', val)[0])
                val_count = val_count + self.data_list[i][1]
            out_list.append(line)
        return out_list

    def get_datalist_len(self):
        return self.str_len

    def get_names(self):
        return self.name_list


class Uart(UartHardware, UartParser, UartPlot):
    def __init__(self, verbose=True):
        self.verbose = verbose
        UartHardware.__init__(self, verbose)
        UartParser.__init__(self, verbose)
        UartPlot.__init__(self)
        self.data = []

    def data_pars(self, n_lines):
        """
        Основная функция. Считывание данных из уарта
        :param n_lines: Количество пачек данных, пачки состоят из add_s32 и тд
        :return:
        """
        print("чисел в пакете:", self.get_datalist_len() * n_lines)
        self.data = self.raw_pars(self.get_data(self.get_datalist_len() * n_lines), n_lines)
        return self.data

    def data_save(self, dir_name='raw', name='data', fmt='csv'):
        """
        Сохранить данные в файл
        :param file_name: название файла с расширением
        :return:
        """
        print("Сохранение данных в файл")
        pwd = os.getcwd()
        path = pwd + '/' + dir_name
        print(path)
        if not os.path.exists(path):
            os.mkdir(path)
        os.chdir(path)
        # if data.any():
        #     np.savetxt('{}.{}'.format(name, fmt), data, fmt='%6d', delimiter=',')
        # else:
        np.savetxt('{}.{}'.format(name, fmt), self.data, fmt='%6d', delimiter=',')
        os.chdir(pwd)
        f = open('{}.{}'.format(name, fmt), 'w')
        # if data.any():
        #     f.write(str(data))
        # else:
        f.write(str(self.data))
        f.close()

    def plt(self, xlable='время', ylable='ускорение'):
        """
        Отрисовать полученные данные в виде графика
        :return:
        """
        times = []
        # получаем время начала каждой пачки данных
        for index in range(0, len(self.time_list), self.str_len):
            times.append(self.time_list[index] - self.start_read_time)
        self.plot(self.data, times, xlable, ylable, name=self.get_names())
        self.show()


def main():
    print("библиотека работы с уартом")
    my_uart = Uart()
    my_uart.connect_uart(synchronization_time=0.15)
    my_uart.add_s16("X")
    my_uart.add_s16("Y")
    my_uart.add_s16("Z")
    line = my_uart.data_pars(26)
    print(line)
    my_uart.plt()


if __name__ == "__main__":
    main()

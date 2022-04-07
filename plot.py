import os
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
import numpy as np


class UartPlot:
    def __init__(self):
        self.fig, self.ax = plt.subplots()  # Создание объекта

    def plot(self, data, times=0, xlable="", ylable="", name=[]):
        """
        Генерация графика с данными
        :param data: данные (возмножно многомерные вида x[n,m], где n количество пакетов, m переменных в пакете
        :param times: временной ряд, если есть
        :param xlable: подпись оси х, если есть
        :param ylable: подпись оси y, если есть
        :param name: список подписей осей
        :return:
        """
        if name:
            for i, name in enumerate(name):
                graph = []
                if times == 0:
                    for j, val in enumerate(data):
                        graph.append(val[i])
                    self.ax.plot(graph, '.-', label=name)
                else:
                    for j, val in enumerate(data):
                        graph.append(val[i])
                    self.ax.plot(times, graph, '.-', label=name)
            self.ax.legend()
        else:
            if times == 0:
                self.ax.plot(data, '.-')
            else:
                self.ax.plot(times, data, '.-')
        self.ax.set_xlabel(xlable)
        self.ax.set_ylabel(ylable)
        self.ax.xaxis.set_minor_locator(AutoMinorLocator(2))
        self.ax.grid(True, which='both')
        self.ax.tick_params(which='both', width=2)

    def show(self):
        plt.show()

    def save(self, dir_name='plots', name='', fmt='png'):
        pwd = os.getcwd()
        print(pwd)
        iPath = pwd + '/pictures/' + dir_name
        if not os.path.exists(iPath):
            os.mkdir(iPath)
        os.chdir(iPath)
        plt.savefig('{}.{}'.format(name, fmt), fmt='png')
        os.chdir(pwd)


def main():
    sample_data = [0, 1], [2, 3]
    print("библиотека работы с графиками")
    p = UartPlot()
    p.plot(sample_data)
    p.save(name='pic_1_4_1', fmt='png')
    p.show()


if __name__ == "__main__":
    main()

# смотри преамбулу
# save(name='pic_1_4_1', fmt='pdf')

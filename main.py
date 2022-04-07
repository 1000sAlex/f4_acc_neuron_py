import uart
import os
import numpy as np
import matplotlib.pyplot as plt


def make_db(data, base=1, k=10):
    return k * np.log10(data/base)


def data_save(data, dir_name='raw', name='data', fmt='csv'):
    """
    Сохранить данные в файл
    """
    print("Сохранение данных в файл")
    pwd = os.getcwd()
    path = pwd + '/' + dir_name
    if not os.path.exists(path):
        os.mkdir(path)
    os.chdir(path)
    np.savetxt('{}.{}'.format(name, fmt), data, fmt='%6d', delimiter=',')
    os.chdir(pwd)


if __name__ == "__main__":
    my_uart = uart.Uart()
    my_uart.connect_uart(synchronization_time=0.1)
    my_uart.add_float("fft data")
    # line = my_uart.data_pars(256)
    # print(line)
    # my_uart.data_save()
    # my_uart.plt()

    # !!! Включить интерактивный режим для анимации
    plt.ion()
    # Создание окна и осей для графика
    fig = plt.figure()
    ax_1 = fig.add_subplot(2, 1, 1)
    ax_2 = fig.add_subplot(2, 1, 2)
    ax_1.set(title='линейный маштаб')
    ax_2.set(title='логарифмический маштаб')

    # график фукнции в начальный момент времени
    data = np.array(my_uart.data_pars(256))
    data_save(data)
    l1, = ax_1.plot(data)
    l2, = ax_2.plot(make_db(data))

    for i in range(100):
        data = np.array(my_uart.data_pars(256))
        data_db = make_db(data)
        # Обновить данные на графике
        l1.set_ydata(data)
        l2.set_ydata(data_db)
        data_save(data_db, dir_name='dataset/test', name=('измерение_' + str(i)))
        # Отобразить новые данный
        fig.canvas.draw()
        fig.canvas.flush_events()

    # Отключить интерактивный режим по завершению анимации
    plt.ioff()
    plt.show()
    my_uart.disconnect_uart()

import matplotlib.pyplot as plt
import numpy as np
import os


def file_get(dir_name='raw', name='data', fmt='csv'):
    pwd = os.getcwd()
    path = pwd + '/' + dir_name
    print(path)
    if not os.path.exists(path):
        print("ошибка файла")
    else:
        os.chdir(path)
        data = np.genfromtxt('{}.{}'.format(name, fmt), delimiter=',')
        return data
    return 0


def make_db(data, base=1, k=10):
    return k * np.log10(data / base)


if __name__ == "__main__":
    data = file_get()
    # print(data)
    fig = plt.figure()
    ax_1 = fig.add_subplot(2, 1, 1)
    ax_2 = fig.add_subplot(2, 1, 2)
    # ax_1.set(title='ax_1')
    # ax_2.set(title='ax_2')
    ax_1.plot(data)
    print(type(data))
    ax_2.plot(make_db(data + 1, base=10))
    plt.show()

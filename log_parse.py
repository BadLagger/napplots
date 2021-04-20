#! /bin/python3
import sys
import os
import math
import time
from pprint import pprint
from matplotlib import pyplot
from multiprocessing import Process

def draw_progress_bar(bgn_offset:int, end_val:int, add_str: str):
    brick = chr(9606)
    parts = 100
    current_fill = int((bgn_offset / end_val) * parts)
    fill_line = '|' + current_fill*brick + (parts - current_fill)*' ' + '|'
    print(fill_line + f"{bgn_offset} / {end_val} {add_str}", end='\r')

def toSigned16(n):
    n = n & 0xffff
    return (n ^ 0x8000) - 0x8000

def save_data_in_file(val_list_accel, val_list_gyro, val_list_magn, name):
    with open(name, 'w') as file:
        size = min(len(val_list_accel), len(val_list_gyro), len(val_list_magn))
        for i in range(size):
            accel = val_list_accel[i]
            gyro = val_list_gyro[i]
            magn = val_list_magn[i]
            line = "%d %d %d %d %d %d %d %d %d\n" % (accel['x'], accel['y'], accel['z'], gyro['x'], gyro['y'], gyro['z'], magn['x'], magn['y'], magn['z'])
            #line = "%.4f %.4f %.4f %.4f %.4f %.4f %.4f %.4f %.4f\n" % (accel['x'], accel['y'], accel['z'], gyro['x'], gyro['y'], gyro['z'], magn['x'], magn['y'], magn['z'])
            file.write(line)


def draw_plot(val_list, title):
    #v_l = val_list.copy()
    total_len = len(val_list)
    x_line = []
    y_line = []
    z_line = []
    for cur in val_list:
        x_line.append(cur['x'])
        y_line.append(cur['y'])
        z_line.append(cur['z'])
    pyplot.title(title)
    pyplot.plot(range(total_len), x_line, label="x")
    pyplot.plot(range(total_len), y_line, label="y")
    pyplot.plot(range(total_len), z_line, label="z")
    pyplot.legend()
    pyplot.show()

def draw_3d(val_list, title):
    #v_l = val_list.copy()
    x_line = []
    y_line = []
    z_line = []
    for cur in val_list:
        x_line.append(cur['x'])
        y_line.append(cur['y'])
        z_line.append(cur['z'])
    #pyplot.title(title)
    fig = pyplot.figure()
    ax = fig.gca(projection='3d')
    ax.plot(x_line, y_line, z_line, label=title)
    ax.legend()
    pyplot.show()

def create_in_process(func, val_list, title):
    return Process(target=func, args=(val_list,title,))

def start_all_process(pr_list):
    for i in pr_list:
        i.start()

def wait_all_process(pr_list):
    for i in pr_list:
        i.join()

STR_LEN = 79
file_path = sys.argv[1]
file_size = os.stat(file_path).st_size
blocks_size = file_size // STR_LEN
if file_size % STR_LEN:
    blocks_size += 1
print(f"{file_path} size {file_size} Bytes & bloks {blocks_size}")
accel_list = []
gyro_list = []
magn_list = []


with open(file_path) as file:
    for cur_block in range(blocks_size):
        draw_progress_bar(cur_block, blocks_size - 1, "blocks")
        line = file.readline()
        dump = []
        element = {}
        if(len(line) == STR_LEN):
            dump = line.strip().split()[2:9]
            if dump[0] != '40' and len(accel_list) == 0:
                continue
            element['x'] = toSigned16(int((dump[2])+dump[1], 16))
            element['y'] = toSigned16(int((dump[4])+dump[3], 16))
            element['z'] = toSigned16(int((dump[6])+dump[5], 16))

            if dump[0] == '40':
                element['x'] /= 8192.0
                element['y'] /= 8192.0
                element['z'] /= 8192.0
                accel_list.append(element)
            elif dump[0] == '20':
                element['x'] /= 65.6
                element['y'] /= 65.6
                element['z'] /= 65.6
                gyro_list.append(element)
            elif dump[0] == '10':
                #element['x'] *= 0.317421
                #element['y'] *= 0.317421
                #element['x'] *= 0.3
                #element['y'] *= 0.3
                #element['z'] *= 0.15
                magn_list.append(element)
            else:
                continue

process_list = []

save_data_in_file(accel_list, gyro_list, magn_list, f"{file_path}_str.log")
process_list.append(create_in_process(draw_plot, accel_list, "Accel"))
process_list.append(create_in_process(draw_plot, gyro_list, "Gyro"))
process_list.append(create_in_process(draw_plot, magn_list, "Magn"))
process_list.append(create_in_process(draw_3d, accel_list, "Accel3D"))
process_list.append(create_in_process(draw_3d, gyro_list, "Gyro3D"))
process_list.append(create_in_process(draw_3d, magn_list, "Magn3D"))
start_all_process(process_list)
wait_all_process(process_list)

print('\n')

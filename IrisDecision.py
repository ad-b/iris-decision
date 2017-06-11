# -*- coding: utf-8 -*-

import datetime
import itertools
import os
import re
import statistics
import subprocess
import sys
import time
import argparse
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import csv
from multiprocessing.pool import Pool

irisExePath = ''
hammingExePath = ''
databasePath = ''
regex = ''
files = []
images = []
date = ''
database = []
hdInsAll = []
hdOutAll = []
configPath = ''
resultsPath = ''
howManyShifts = 8
results = []
parameters = []
dec = 0.0
meanIntra = 0.0
meanInter = 0.0
stdevIntra = 0.0
stdevInter = 0.0
count_criterion = False
results_filename = ''
csv_row = []
parametersList = []
multithreading = False
threads = 1
create_csv = False
times = []
iris_name = 'Iris'
hd_inside_name = 'Hamming intraclass'
hd_outside_name = 'Hamming interclass'


def log_time(process_name):
    """
    Outputs the time a funcion f takes to execute
    :param process_name: name of process
    :return: time of execution
    """
    def log(f):
        def wrapper():
            global times
            start_time = time.time()
            f()
            end_time = time.time()
            runtime = str(end_time - start_time)
            results.append('Runtime of {0}: {1}'.format(process_name, runtime))
            print("Runtime: {0} seconds".format(runtime))
            times.append(runtime)
        return wrapper
    return log


def run_iris(iris_arg):
    """
    Run Iris.exe to generate code and mask for image
    :param iris_arg: list with paths to Iris.exe, database and name of image
    :return: 0 if no errors, name of image if an error occured
    """
    cmd_line = [iris_arg[0], os.path.join(iris_arg[1], iris_arg[2])]
    try:
        output = subprocess.check_output(cmd_line, universal_newlines=True, stderr=subprocess.STDOUT)
        print(str(output)[:-1])
        return 0
    except subprocess.CalledProcessError:
        return iris_arg[2]


@log_time(iris_name)
def iris():
    """
    Prepare images to run Iris.exe and inform about errors
    :return:
    """
    print("Iris.exe - generate code and mask for every image")
    iris_arg = []
    iris_results = []
    for image in images:
        iris_arg.append([irisExePath, databasePath, image])
    if multithreading:
        p = Pool(processes=threads)
        iris_results = p.map(run_iris, iris_arg)
        p.close()
        p.join()
    else:
        for arg in iris_arg:
            iris_results.append(run_iris(arg))
    removed = 0
    for result in iris_results:
        if result != 0:
            line = "Error Iris.exe for image {0}, removing image from list".format(result)
            print(line)
            results.append(line)
            images.remove(result)
            removed += 1
    line = "Removed {0} images".format(removed)
    print(line)
    results.append(line)
    if not images:
        print("Removed all images")
        sys.exit(-1)
    line = "Number of images: {0}".format(str(len(images)))
    print(line)
    results.append(line)


def nested():
    """
    Create nested list of persons and pictures
    :return:
    """
    m = re.compile(regex)
    person_num = 0
    global database
    db_person = []
    new_name = ''
    person = 0
    images.sort()
    for image in images:
        image, _ = os.path.splitext(image)
        mo = m.search(image)
        try:
            person = int(mo.group(1))
        except ValueError:
            name_of_person = str(mo.group(1))
            if new_name != name_of_person:
                person += 1
                new_name = name_of_person
        if person_num != person - 1:
            database.append(db_person)
            db_person = db_person[:]
            db_person.clear()
            person_num += 1
        db_person.append(image)
    database.append(db_person)


def run_hamming(arg_images):
    """
    Run Hamming.exe for one comparsion
    :param arg_images: list with names of images, path to database and Hamming.exe, number of shifts
    :return: value of Hamming distance, information about comparsion
    """
    image1, image2, db_path1, db_path2, hamming_path, how_many_shifts = arg_images
    code_r1 = os.path.join(db_path1, image1 + "_code_re.png")
    code_i1 = os.path.join(db_path1, image1 + "_code_im.png")
    mask_1 = os.path.join(db_path1, image1 + "_mask.png")
    code_r2 = os.path.join(db_path2, image2 + "_code_re.png")
    code_i2 = os.path.join(db_path2, image2 + "_code_im.png")
    mask_2 = os.path.join(db_path2, image2 + "_mask.png")

    arg = [hamming_path, code_r1, code_i1, mask_1, code_r2, code_i2, mask_2, str(how_many_shifts)]
    hd = subprocess.check_output(arg, universal_newlines=True)
    line = "{0} + {1} = {2}".format(image1, image2, hd[:-1])
    print(line)
    try:
        return [float(hd[:-1]), line]
    except Exception:
        print("Error with Hamming.exe")
        sys.exit(-1)


def hd_process(comparisons, hd_db, suffix='.txt'):
    """
    Prepare for making comparisons and save results
    :param comparisons: comparisons to make
    :param hd_db: Hamming distances results database
    :param suffix: suffix for file with results
    :return:
    """
    hd_results = []
    if multithreading:
        p = Pool(processes=threads)
        hd_results = p.map(run_hamming, comparisons)
        p.close()
        p.join()
    else:
        for comparison in comparisons:
            hd_results.append(run_hamming(comparison))
    savefile = open(results_filename + suffix, 'w')
    for result in hd_results:
        hd_db.append(result[0])
        savefile.write(result[1] + '\n')
    savefile.close()


@log_time(hd_inside_name)
def hd_inside():
    """
    Prepare intraclass comparisons for running Hamming.exe
    :return:
    """
    print("Hamming.exe - calculate intraclass Hamming distances")
    global hdInsAll
    comparisons = []
    for person in database:  # choose person
        for pic1_num, pic1 in enumerate(person):  # choose image 1
            # print("{0} - {1}".format(pic1_num, pic1))
            for pic2_num in range(pic1_num + 1, len(person)):  # choose image 2
                arg = [str(person[pic1_num]), str(person[pic2_num]),
                       databasePath, databasePath, hammingExePath, howManyShifts]
                comparisons.append(arg)

    hd_process(comparisons, hd_db=hdInsAll, suffix="_intra.txt")
    line = "{0} tests".format(len(hdInsAll))
    print(line)
    results.append(line)


@log_time(hd_outside_name)
def hd_outside():
    """
    Prepare interclass comparisons for running Haminng.exe
    :return:
    """
    print("Hamming.exe - calculate interclass Hamming distances")
    global hdOutAll, howManyShifts
    comparisons = []
    for person1_num, person1 in enumerate(database):  # choose person 1
        for person2_num in range(person1_num + 1, len(database)):  # choose person 2
            for image1 in person1:  # choose image1 from person 1
                for image2 in database[person2_num]:  # choose image2 from person 2
                    arg = [image1, image2, databasePath, databasePath, hammingExePath, howManyShifts]
                    comparisons.append(arg)

    hd_process(comparisons, hd_db=hdOutAll, suffix="_inter.txt")
    line = "{0} tests".format(len(hdOutAll))
    print(line)
    results.append(line)


def decidability():
    """
    Calculate decidability
    """
    global dec, meanIntra, meanInter, stdevIntra, stdevInter, hdInsAll, hdOutAll
    meanIntra = statistics.mean(hdInsAll)
    meanInter = statistics.mean(hdOutAll)
    print("mean ins: {0} - out: {1}".format(meanIntra, meanInter))
    stdevIntra = statistics.stdev(hdInsAll)
    stdevInter = statistics.stdev(hdOutAll)
    print("stdev ins: {0} - out: {1}".format(stdevIntra, stdevInter))
    dec = (abs(meanInter - meanIntra)) / (((stdevInter ** 2 + stdevIntra ** 2) / 2) ** 0.5)
    print("Decidability: {0}".format(dec))

    results.append('\n')
    results.append('Decidability: {0}'.format(dec))
    results.append('Mean intraclass: {0}'.format(meanIntra))
    results.append('Mean interclass: {0}'.format(meanInter))
    results.append('Standard deviation intraclass: {0}'.format(stdevIntra))
    results.append('Standard deviation interclass: {0}'.format(stdevInter))
    results.append('\n')

    csv_row.extend([dec, meanIntra, meanInter, stdevIntra, stdevInter])


def list_of_parameters():
    global parametersList
    parametersList.append('howManyShifts')
    parameters_file = open(configPath, 'r')
    for line in parameters_file:
        if not (line.startswith('-') or line.startswith('#') or line.startswith('\n')):
            line = line.partition(' = ')
            parametersList.append(line[0])
    parameters_file.close()


def check_parameter(parameter_name):
    if parameter_name in parametersList:
        pass
    else:
        print("Coundn't find parameter {0}".format(parameter_name))
        sys.exit(-1)


def change_parameter(param_name, value=0.0):
    """
    Change parameter
    :param param_name: name of parameter to change
    :param value: value to change to
    """
    global howManyShifts
    if param_name == "howManyShifts":
        if howManyShifts != int(value):
            howManyShifts = value
            results.append("Changed parameter {0} to: {1}".format(param_name, value))
            print("Changed")
        else:
            results.append("No changes to parameter {0}, value left: {1}".format(param_name, value))
            print("No changes")
    else:
        parameters_file = open(configPath, 'r')
        new_lines = []
        change = False
        for line in parameters_file:
            if param_name in line:
                print("Found line: {0}".format(line[:-1]))
                new_line = line.partition(' = ')
                if new_line[2] == (str(value) + '\n'):
                    print("No changes")
                    results.append("No changes to parameter {0}, value left: {1}".format(param_name, value))
                    break
                else:
                    change = True
                    line = line.replace(str(new_line[2]), str(value) + '\n')
                    print("Changed to: {0}".format(line))
                    results.append("Changed parameter {0} to: {1}".format(param_name, value))
            new_lines.append(line)
        if change:
            parameters_file = open(configPath, 'w')
            parameters_file.writelines(new_lines)
        parameters_file.close()


def save_parameters():
    global csv_row
    results.append('Current parameters:')
    results.append('Hamming distance - howManyShifts: {0}'.format(howManyShifts))
    csv_row.append(str(len(images)))
    csv_row.extend(times)
    csv_row.append(howManyShifts)
    parameters_file = open(configPath, 'r')
    for line in parameters_file:
        results.append(line[:-1])
        line = line.partition(' = ')
        if line[0] in parametersList:
            csv_row.append(str(line[2][:-1]))
    parameters_file.close()


def csv_generate(parameters_dict):
    values_list = []
    results_csv = []
    first_csv_row = []
    global resultsPath, results_filename, results, csv_row
    subfolder = date + "_csv"
    saved_results = results[:]
    all_results = saved_results[:]
    if not os.path.isdir(subfolder):
        os.makedirs(subfolder)
        print("Created {0}".format(subfolder))
    all_results_line = "Parameters to change: "
    for parameter in parameters_dict:
        name, value1, resolution, value2 = parameter
        print("* {0} = from {1}, resolution {2}, to {3}".format(name, value1, resolution, value2))
        values = np.linspace(float(value1), float(value2), num=int(resolution))
        values_list.append(values)
        all_results_line += name + " "
        first_csv_row.append(name)
    all_results.append(all_results_line)
    values_dict = list(itertools.product(*values_list))

    canny_flag_l = False
    canny_flag_h = False
    canny_low = 0
    canny_high = 0
    for num_parameter, parameter in enumerate(parameters_dict):
        if 'cannyLowThreshold' in parameter:
            canny_low = num_parameter
            canny_flag_l = True
        elif 'cannyHighThreshold' in parameter:
            canny_high = num_parameter
            canny_flag_h = True
    if canny_flag_h and canny_flag_l:
        for values_set in values_dict[:]:
            if values_set[canny_low] > values_set[canny_high]:
                values_dict.remove(values_set)

    all_results.append("Possible values of parameters: {0}".format(str(values_dict)))
    print("Possible values of parameters: {0}".format(str(values_dict)))
    all_results.append("\n-------CSV-------\n")
    first_csv_row.extend(['dec', 'mean_intra', 'mean_inter', 'stdev_intra', 'stdev_inter', 'images'])
    first_csv_row.extend([iris_name, hd_inside_name, hd_outside_name])
    first_csv_row.extend(parametersList)
    results_csv.append(first_csv_row)
    for values_set in values_dict:
        results = results[:]
        results.clear()
        csv_row = csv_row[:]
        csv_row.clear()
        results_filename = os.path.join(subfolder, date)
        results.extend(saved_results)
        for par_id, par_val in enumerate(values_set):
            name = parameters_dict[par_id][0]
            change_parameter(name, int(par_val))
            results_filename += "_" + str(int(par_val))
            csv_row.append(int(par_val))
        count_dec_process()
        results_csv.append(csv_row)
        resultsPath = results_filename + '_results.txt'
        results_file = open(resultsPath, 'a')
        results_file.write("\n".join(results))
        results_file.close()
        all_results.extend(results)
        all_results.append('\n\n-----***-----\n')

    resultsPath = os.path.join(subfolder, date + '_results_all.txt')
    results_file = open(resultsPath, 'a')
    results_file.write("\n".join(all_results))
    results_file.close()

    csv_path = os.path.join(subfolder, date + '_results.csv')
    csv_file = open(csv_path, 'w', newline='')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerows(results_csv)
    csv_file.close()


def criterion():
    line = "Calculate criterion, FRR and FAR"
    results.append(line)
    floatingpoint = 4
    step = 1 / (10 ** (floatingpoint - 1))
    res = int(np.ceil((meanInter - meanIntra) / step))
    possible_crit = np.linspace(meanIntra + stdevIntra, meanInter - stdevInter, num=res)
    hd_all = len(hdOutAll) + len(hdInsAll)
    lowest_frr_num = hd_all
    far_for_lowest_frr = hd_all
    lowest_far_num = hd_all
    frr_for_lowest_far = hd_all
    best_crit_frr = 0.0
    best_crit_far = 0.0
    best_crits = []
    for crit in possible_crit:
        crit = round(crit, floatingpoint)
        frr_num = 0
        far_num = 0
        for hd in hdInsAll:
            if hd > crit:
                frr_num += 1
        for hd in hdOutAll:
            if hd < crit:
                far_num += 1
        if frr_num < lowest_frr_num:
            best_crit_frr = crit
            lowest_frr_num = frr_num
            far_for_lowest_frr = far_num
        if far_num <= lowest_far_num:
            best_crit_far = crit
            lowest_far_num = far_num
            frr_for_lowest_far = frr_num
        if far_num == frr_num == 0:
            best_crits.append(crit)
    line = "Lowest criterion considering FRR: {0}, FRR = {1}%, FAR = {2}%\n" \
           "Biggest criterion considering FAR: {3}, FAR = {4}%, FRR = {5}%\n" \
           "Max hd intraclass: {6}\n" \
           "Min hd interclass: {7}\n" \
        .format(best_crit_frr, round(lowest_frr_num * 100 / hd_all, 4), round(far_for_lowest_frr * 100 / hd_all, 4),
                best_crit_far, round(lowest_far_num * 100 / hd_all, 4), round(frr_for_lowest_far * 100 / hd_all, 4),
                str(max(hdInsAll)), str(min(hdOutAll)))
    print(line)
    results.append(line)


def plotting():
    print("Plotting")
    matplotlib.rc('font', family='Arial')
    fig = plt.figure()
    ax = fig.add_subplot(111)

    plt.interactive(False)
    n, bins, patches = plt.hist([hdInsAll, hdOutAll], bins=500, range=(0.0, 1.0), histtype="stepfilled",
                                color=['0.25', '0.75'], label=['Intra-class distribution', 'Inter-class distribution'])

    max_y = int(np.amax(n))
    max_y_size = len(str(max_y))
    plt.grid(which="both")
    x_major_ticks = np.arange(0.0, 1.01, 0.1)
    x_minor_ticks = np.arange(0.0, 1.01, 0.05)
    y_major_ticks = np.arange(0.0, max_y + max_y_size * 10, 10 * max_y_size * np.ceil(max_y / (max_y_size * 100)))
    y_minor_ticks = np.arange(0.0, max_y + max_y_size * 10, 5 * max_y_size * np.ceil(max_y / (max_y_size * 100)))
    ax.set_xticks(x_major_ticks)
    ax.set_xticks(x_minor_ticks, minor=True)
    ax.set_yticks(y_major_ticks)
    ax.set_yticks(y_minor_ticks, minor=True)

    plt.grid(which='minor', alpha=0.3)
    plt.grid(which='major', alpha=0.6)
    plt.xlabel("Hamming distance")
    plt.ylabel("Count")
    plt.title('Intra-class and inter-class Hamming distance distributions')

    handles, labels = ax.get_legend_handles_labels()
    intra_label = '$Comparisons={0}$\n$\mu={1}$\n$\sigma={2}$' \
        .format(len(hdInsAll), round(meanIntra, 4), round(stdevIntra, 4))
    inter_label = '$Comparisons={0}$\n$\mu={1}$\n$\sigma={2}$' \
        .format(len(hdOutAll), round(meanInter, 4), round(stdevInter, 4))
    dec_label = 'Decidability\n$dec={0}$\n$Pictures={1}$'.format(round(dec, 4), str(len(images)))

    empty_handle = mpatches.Patch(color='white')
    handle = [handles[1], empty_handle, handles[0], empty_handle, empty_handle]
    label = [labels[1], intra_label, labels[0], inter_label, dec_label]
    ax.legend(handle, label, fontsize='medium')

    plt.savefig(results_filename + "_chart.png", bbox_inches='tight')
    plt.yscale('log')
    plt.title('Intra-class and inter-class Hamming distance distributions in log scale')
    plt.savefig(results_filename + "_chart_log.png", bbox_inches='tight')
    plt.close()


def count_dec_process():
    global database, hdInsAll, hdInsAll, images, times
    images.clear()
    database.clear()
    hdInsAll.clear()
    hdOutAll.clear()
    times.clear()
    images = [file for file in files if os.path.isfile((os.path.join(databasePath, file))) and
              not (file.endswith("_code_re.png") or file.endswith("_code_im.png") or
                   file.endswith("_mask.png") or file.endswith("_rubber.png") or file.endswith("_segmentation.png"))]
    iris()
    nested()
    hd_inside()
    hd_outside()
    decidability()
    if count_criterion:
        criterion()
    if not create_csv:
        plotting()
    save_parameters()


def read_settings():
    if os.path.exists('settings.txt'):
        file_settings = open('settings.txt', 'r')
        settings = file_settings.read().splitlines()
        global irisExePath, hammingExePath, databasePath, regex, files, configPath
        irisExePath = settings[0]
        hammingExePath = settings[1]
        databasePath = settings[2]
        regex = settings[3]
        configPath = settings[4]
        file_settings.close()
    else:
        print("settings.txt doesn't exist")
        sys.exit(-1)


def main():
    global date, resultsPath, howManyShifts, results_filename, multithreading, \
        threads, count_criterion, create_csv, files
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--parameter", action="append",
                        nargs=2, metavar=('name', 'value'),
                        help="change parameter value")
    parser.add_argument("-c", "--csv", action="append",
                        nargs=4, metavar=('name', 'value_from', 'resolution', 'value_to'),
                        help="csv mode, change parameter value multiple times")
    parser.add_argument("-m", "--multithreading", type=int,
                        metavar='number_of_threads',
                        help='run using multithreading')
    parser.add_argument("-k", "--kryterium", action="store_true",
                        help="calculate criterion, FRR and FAR")
    args = parser.parse_args()

    read_settings()

    now = datetime.datetime.now()
    date = "{0}{1}{2}_{3}{4}{5}".format(str(now.year), str(now.month).zfill(2), str(now.day).zfill(2),
                                        str(now.hour).zfill(2), str(now.minute).zfill(2), str(now.second).zfill(2))
    results_filename = date
    results.append(date)
    results.append(databasePath)
    results.append('\n')

    list_of_parameters()

    if len(sys.argv) > 1:
        if args.parameter:
            print("Got parameters: ")
            for name, value in args.parameter:
                check_parameter(name)
                print("{0} = {1}".format(name, value))
        if args.csv:
            print("CSV mode")
            for name, value1, resolution, value2 in args.csv:
                check_parameter(name)
                if int(resolution) == 0 or int(resolution) == 1:
                    print("{0} - Resolution can't be equal to 0 or 1. "
                          "If you want to change parameter and make it const, use -p".format(name))
                    sys.exit(-1)
                else:
                    print("{0} = from {1}, resolution {2}, to {3}".format(name, value1, resolution, value2))
        if args.kryterium:
            count_criterion = True
        if args.multithreading:
            multithreading = True
            threads = args.multithreading
            line = "Multithreading ON, number of threads: {0}".format(threads)
            print(line)
            results.append(line)

    start_time = time.time()

    files = os.listdir(databasePath)

    if len(sys.argv) > 1 and args.parameter:
        for name, value in args.parameter:
            change_parameter(name, value)

    if args.csv:
        print("MASOWA ZMIANA PARAMETRÓW")
        create_csv = True
        csv_generate(args.csv)

    else:
        print("STANDARDOWA PROCEDURA")
        count_dec_process()
        resultsPath = results_filename + '_results.txt'
        results_file = open(resultsPath, 'a')
        results_file.write("\n".join(results))
        results_file.close()

    print("Finished")
    print("Runtime of whole process: {0} seconds".format(time.time() - start_time))


if __name__ == "__main__":
    main()

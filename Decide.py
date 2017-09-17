# -*- coding: utf-8 -*-

import datetime
import os
import re
import subprocess
import sys
import time
import argparse
from operator import itemgetter
from multiprocessing.pool import Pool
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import statistics

irisExePath = ''
hammingExePath = ''
databasePath = ''
regex = ''
files = []
images = []
date = ''
database = []
configPath = ''
howManyShifts = 8
results = []
parameters = []
hd_smallest = 1.0
person_picked = ''
databaseCompare = ''
filesCompare = []
imagesCompare = []
picture = ''
criterion = 0.41
multiple = True
multithreading = False
threads = 1
hdResults = []
hd_compare_name = 'Hamming compare'
iris_name = 'Iris'
results_path = ''
matched_hd = []


def log_time(process_name):
    """
    Outputs the time a funcion f takes to execute
    :param process_name: name of process
    :return:
    """
    def log(f):
        def wrapper():
            start_time = time.time()
            f()
            end_time = time.time()
            runtime = str(end_time - start_time)
            results.append('\nRuntime of {0}: {1}'.format(process_name, runtime))
            print("Runtime: {0} seconds".format(runtime))
        return wrapper
    return log


def run_iris(iris_arg):
    """
    Run Iris.exe to generate code and mask for image
    :param iris_arg: list with paths to Iris.exe, database and name of image
    :return: 0 if no errors, name of image if errors
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
    for image in imagesCompare:
        iris_arg.append([irisExePath, databaseCompare, image])

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
            imagesCompare.remove(result)
            removed += 1
    line = "Removed {0} images".format(removed)
    print(line)
    results.append(line)
    if not imagesCompare:
        print("Removed all images")
        sys.exit(-1)

    line = "Number of images: {0}".format(str(len(imagesCompare)))
    print(line)
    results.append(line)


def nested():
    """
    Create nested list of persons and pictures
    :return:
    """
    m = re.compile(regex)  # regex for file name
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

    with open(results_path + 'decide_' + suffix + '.txt', 'w') as savefile:
        for result in hd_results:
            hd_db.append(result[0])
            savefile.write(result[1] + '\n')


@log_time(hd_compare_name)
def hd_compare():
    print("Hamming.exe - calculate Hamming distances with input pictures")
    global date, howManyShifts, hdResults
    for person1 in imagesCompare:  # choose first person
        hdResults.clear()
        comparisons = []
        person1, _ = os.path.splitext(person1)
        for person2 in database:  # iterate through persons - pick person
            for picNum, pic in enumerate(person2):  # iterate through person
                arg = [person1, person2[picNum], databaseCompare, databasePath, hammingExePath, howManyShifts]
                comparisons.append(arg)
        hd_process(comparisons, hd_db=hdResults, suffix=person1)
        decide(person1)
    line = "{0} tests".format(len(hdResults))
    print(line)


def save_parameters():
    results.append('\nCurrent parameters:')
    results.append('Hamming distance - howManyShifts: {0}'.format(howManyShifts))
    with open(configPath, 'r') as parameters_file:
        for line in parameters_file:
            results.append(line[:-1])


def read_settings():
    if os.path.exists('settings.txt'):
        with open('settings.txt', 'r') as file_settings:
            settings = file_settings.read().splitlines()
            global irisExePath, hammingExePath, databasePath, regex, files, configPath
            irisExePath = settings[0]
            hammingExePath = settings[1]
            databasePath = settings[2]
            regex = settings[3]
            configPath = settings[4]
    else:
        print("settings.txt doesn't exist")
        sys.exit(-1)


def plotting(image, intra, inter):
    print("Plotting")

    matplotlib.rc('font', family='Arial')
    fig = plt.figure()
    ax = fig.add_subplot(111)

    plt.interactive(False)
    n, bins, patches = plt.hist([intra, inter], bins=100, range=(0.0, 1.0), histtype="stepfilled",
                                color=['g', 'r'], label=['Rozkład wewnątrzklasowy', 'Rozklad zewnątrzklasowy'])

    max_y = int(np.amax(n))
    max_y_size = len(str(max_y))
    plt.grid(which="both")
    x_major_ticks = np.arange(0.0, 1.01, 0.1)
    x_minor_ticks = np.arange(0.0, 1.01, 0.05)
    y_major_ticks = np.arange(0.0, max_y+max_y_size*10, 10*max_y_size*np.ceil(max_y/(max_y_size*100)))
    y_minor_ticks = np.arange(0.0, max_y+max_y_size*10, 5*max_y_size*np.ceil(max_y/(max_y_size*100)))
    ax.set_xticks(x_major_ticks)
    ax.set_xticks(x_minor_ticks, minor=True)
    ax.set_yticks(y_major_ticks)
    ax.set_yticks(y_minor_ticks, minor=True)

    plt.grid(which='minor', alpha=0.3)
    plt.grid(which='major', alpha=0.6)
    plt.xlabel("Odległość Hamminga")
    plt.ylabel("Liczebność")
    plt.title('Porownania - {0}'.format(image))

    plt.savefig(results_path + image + "_chart.png", bbox_inches='tight')


def plotting_matched():
    print("Plotting")

    matplotlib.rc('font', family='Arial')
    fig = plt.figure()
    ax = fig.add_subplot(111)

    plt.interactive(False)
    n, bins, patches = plt.hist(matched_hd, bins=100, range=(0.0, 1.0), histtype="stepfilled",
                                color='g', label='Rozkład wewnątrzklasowy')

    max_y = int(np.amax(n))
    max_y_size = len(str(max_y))
    plt.grid(which="both")
    x_major_ticks = np.arange(0.0, 1.01, 0.1)
    x_minor_ticks = np.arange(0.0, 1.01, 0.05)
    y_major_ticks = np.arange(0.0, max_y+max_y_size*10, 10*max_y_size*np.ceil(max_y/(max_y_size*100)))
    y_minor_ticks = np.arange(0.0, max_y+max_y_size*10, 5*max_y_size*np.ceil(max_y/(max_y_size*100)))
    ax.set_xticks(x_major_ticks)
    ax.set_xticks(x_minor_ticks, minor=True)
    ax.set_yticks(y_major_ticks)
    ax.set_yticks(y_minor_ticks, minor=True)

    handles, labels = ax.get_legend_handles_labels()
    intra_label = '$l. dobrych porównań={0}$\n$\mu={1}$\n$\sigma={2}$' \
        .format(len(matched_hd), round(statistics.mean(matched_hd), 4), round(statistics.stdev(matched_hd), 4))

    empty_handle = mpatches.Patch(color='white')
    handle = [handles[0], empty_handle]
    label = [labels[0], intra_label]
    ax.legend(handle, label, fontsize='medium')

    plt.grid(which='minor', alpha=0.3)
    plt.grid(which='major', alpha=0.6)
    plt.xlabel("Odległość Hamminga")
    plt.ylabel("Liczebność")
    plt.title('Wyniki poprawnych porównań')

    plt.savefig(results_path + "matched_chart.png", bbox_inches='tight')


def decide(image):
    global hd_smallest, person_picked
    matched = [(images[ind], hd) for ind, hd in enumerate(hdResults) if hd <= criterion]
    if matched:
        (person_picked, hd_smallest) = min(matched, key=itemgetter(1))
        line = '\n{0} - best match for image {1}, hd = {2}' \
               '\nAll matched images: {3}'.format(image, person_picked, hd_smallest, matched)
        print(line)
        results.append(line)
    else:
        line = '\n{0} - no best match!'.format(image)
        print(line)
        results.append(line)
    matched_hd.extend([hd for hd in hdResults if hd <= criterion])


def main():
    global date, howManyShifts, picture, images, files, filesCompare, imagesCompare, databaseCompare, \
            results, criterion, multiple, multithreading, threads, results_path

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True,
                        metavar='image path', type=str,
                        help="input picture")
    parser.add_argument("-c", "--criterion", type=float,
                        metavar='value of criterion',
                        help="determine value of criterion, if not, k=0.41")
    parser.add_argument("-m", "--multithreading", type=int,
                        metavar='number_of_threads',
                        help='run using multithreading')
    args = parser.parse_args()

    if len(sys.argv) > 1:
        if args.input:
            print("Input: {0}".format(args.input))
            if os.path.isfile(args.input):
                picture = args.input
                multiple = False
            elif os.path.isdir(args.input):
                databaseCompare = args.input
                multiple = True
            else:
                print("Wrong input")
                sys.exit(-1)
        if args.criterion:
            print("Criterion value: {0}".format(args.criterion))
            criterion = args.criterion
        if args.multithreading:
            multithreading = True
            threads = args.multithreading
            line = "Multithreading ON, number of threads: {0}".format(threads)
            print(line)
            results.append(line)

    read_settings()

    now = datetime.datetime.now()
    date = "{0}{1}{2}_{3}{4}{5}".format(str(now.year), str(now.month).zfill(2), str(now.day).zfill(2),
                                        str(now.hour).zfill(2), str(now.minute).zfill(2), str(now.second).zfill(2))
    results.append(date)
    results.append(databasePath)
    results.append(args.input)
    results.append('\n')

    files = os.listdir(databasePath)
    images = [file for file in files if os.path.isfile((os.path.join(databasePath, file))) and
              not (file.endswith("_code_re.png") or file.endswith("_code_im.png") or
                   file.endswith("_mask.png") or file.endswith("_rubber.png")
                   or file.endswith("_segmentation.png"))]

    start_time = time.time()

    if multiple:
        filesCompare = os.listdir(databaseCompare)
        imagesCompare = [file for file in filesCompare if os.path.isfile((os.path.join(databaseCompare, file))) and
                         not (file.endswith("_code_re.png") or file.endswith("_code_im.png") or
                              file.endswith("_mask.png") or file.endswith("_rubber.png")
                              or file.endswith("_segmentation.png"))]

        subfolder = date + '_decide'
        if not os.path.isdir(subfolder):
            os.makedirs(subfolder)
            print("Created {0}".format(subfolder))
        results_path = os.path.join(subfolder, date + '_')
    else:
        databaseCompare, picture = os.path.split(picture)
        imagesCompare.append(picture)
        results_path = date + '_'

    iris()
    nested()

    line = '\nCriterion set to: {0}'.format(criterion)
    results.append(line)
    print(line)

    hd_compare()
    save_parameters()

    with open(results_path + 'decide_results.txt', 'a') as results_file:
        results_file.write("\n".join(results))

    print("Runtime of whole process: {0} seconds".format(time.time() - start_time))
    sys.exit(0)

if __name__ == "__main__":
    main()

# iris-decision
Part of the iris recognition system developed on Raspberry Pi 3 (Windows implemented version).

## Iris recognition system
It is a Python-part of a thesis project _Segmentation and encoding of iris images taken in infrared light_.
Iris recognition system was developed on Raspberry Pi 3 (with Raspbian Jessie). Process of iris encoding and comparing was written C++ using OpenCV library. Python part was implemented to manipulate with data, images and parameter values. Project is still evolving (GUI in development). Due to this and possible licensing problems, only Python part is shared.
Python part was designed to consist of two seperate files `Decide.py` and `IrisDecision.py`. Both files have some part of similarities, but due to requirements of a system, they have to be disjoined as they are designed to work on a separate embedded systems.

### `Decide.py`
This script encodes iris from an image of an eye and compares it with all iris codes in database. Given criterion treshold, information about recognition is returned. Information about comparisions and results are saved in .txt. Comparisons can be run with multithreading.

### `IrisDecision.py`
This script performes testing of whole sytem using given algorithm parameters. It encodes irises from all images of eyes in database, creates sets of intra-class (the same irises) and inter-class (different irises) comparisions, performes them and as a result information about decidability is returned. Decidability parameter defines how wide distributions of both classes are. Bigger decidability provides less errors during comparisons.
Additional features: 
- saving charts of class distributions, results of comparisions and results of testing whole system
- changing multiple algorithm parameters in given range and testing whole system for each given set of parameters
- using multithreading to generate codes of irises and to compare them
- calculating error rates and proposing criterion threshold

### GUI
In development. What works: opening an image, encoding iris form image, running `Decide.py`, showing results.

## Used libraries
- (Python Standard Library)
- matplotlib 2.0.2
- numpy 1.12.1
- PyQt5

## Additional installation info
To work, files `Iris.exe` (encoding irises), `Hamming.exe` (comparing codes) and `config.txt` (file with names and values of algorithm paramteres) are needed. Additionally, file `settings.txt` defines paths to these files and to irises database:
```
[Iris.exe path]
[Hamming.exe path]
[irises database path]
[regex for filename of iris images]
[config.txt path]
```
`settings.txt` stays the same for both `Decide.py` and `IrisDecision.py`.

## Running
Both `Decide.py` and `IrisDecision.py` run with arguments as described below.

### `Decide.py`
- (required) `-i [name]` input image `[name]`
- (optional) `-m [number]` run with multithreading with `[number]` threads (recommended: `-m8`)
- (optional) `-c [value]` determine value of criterion threshold at `[value]`, default: 0.41 


### `IrisDecision.py`
- (optional) `-m [number]` run with multithreading with `[number]` threads (recommended: `-m8`)
- (optional) `-k` calculate error rates and propose value of criterion threshold
- (optional) `-p [name] [value]` change parameter `[name]` value to `[value]` and then run
- (optional) `-c [name] [value_from] [resolution] [value_to]` create set of parameter `[name]` values form `[value_from]` to `[value_to]` with resolution `[resolution]` and run for every value from set, create `.csv` file for all runs with results

Parameters `-p` and `-c` can be given multiple times. 
Example of usage:
- `python IrisDecision.py -m8 -c width 200 3 300` creates set of values of parameter `width`, values: `200, 250, 300`, then for every parameter value (here: 3 times) runs `IrisDecision.py` with multithreading (with 8 threads)
- `python IrisDecision.py -m8 -c width 200 3 300 -c height 10 4 40` creates sets of values of parameters `width` (values: `200, 250, 300`) and height (values: `10, 20, 30, 40`), creates cartesian product to have all parametes combinations, then for every combination of parameters values (here: 12 times) runs `IrisDecision.py` with multithreading (with 8 threads)

"""
Copyright (c) 2016 Gianluca Gerard

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Portions of the code are
Copyright (c) 2010--2015, Deep Learning Tutorials Development Team
All rights reserved.
"""

from __future__ import print_function
import os
import sys
import getopt
import gzip
import numpy
import theano
from scipy import stats
from scipy.spatial import distance

def import_TCGA_data(file, datadir, dtype):
    # Load the data, each column is originally a single person
    # Return a row representation with the data for each person
    # on a single row.

    root_dir = os.getcwd()
    os.chdir(datadir)

    if file.endswith('.gz'):
        with gzip.open(file) as f:
            ncols = len(f.readline().split('\t'))
    else:
        with open(file) as f:
            ncols = len(f.readline().split('\t'))

    data = numpy.loadtxt(file,
                         dtype=dtype,
                         delimiter='\t',
                         skiprows=1,
                         usecols=range(1, ncols))

    os.chdir(root_dir)
    return (data.shape[1], data.T)


def get_minibatches_idx(n, batch_size, rng=None):
    """
    Used to shuffle the dataset at each iteration.
    """

    idx_list = numpy.arange(n, dtype="int32")

    if rng:
        rng.shuffle(idx_list)

    minibatches = []
    minibatch_start = 0
    for i in range(n // batch_size):
        minibatches.append(idx_list[minibatch_start:
        minibatch_start + batch_size])
        minibatch_start += batch_size

    if (minibatch_start != n):
        # Make a minibatch out of what is left
        minibatches.append(idx_list[minibatch_start:])

    return range(len(minibatches)), minibatches


def load_n_preprocess_data(datafile,
                           holdout_fraction=0.0,
                           repeats=1,
                           clip=None,
                           transform_fn=None,
                           exponent=1.0,
                           datadir='data',
                           rng=None,
                           dtype=theano.config.floatX):

    n_data, data = import_TCGA_data(datafile, datadir, dtype)

    if transform_fn is not None:
        data = transform_fn(data, exponent)

    # Normalize the data so that each measurement on our population has zero
    # mean and zero variance
    zdata = stats.zscore(data, axis=0)
    not_nan_ix = ~numpy.isnan(zdata).any(axis=1)
    zdata = zdata[not_nan_ix]

    if clip is not None:
        zdata = numpy.clip(zdata, clip[0], clip[1])

    # replicate the samples
    if repeats > 1:
        zdata = numpy.repeat(zdata, repeats=repeats, axis=0)

    validation_set_size = int(n_data * holdout_fraction)

    # pre shuffle the data if we have a validation set
    _, indexes = get_minibatches_idx(n_data, n_data -
                                     validation_set_size, rng=rng)

    train_set = theano.shared(zdata[indexes[0]], borrow=True)
    if validation_set_size > 0:
        validation_set = theano.shared(zdata[indexes[1]], borrow=True)
    else:
        validation_set = None

    return train_set, validation_set


# The following function help reduce the number of classes based on highest
# frequency and lowest Hamming distance

def remap_class(classified_samples, distance_matrix, n_classes):
    def class_by_frequency(a):
        classes = range(int(numpy.max(a)) + 1)
        frequency = [numpy.sum(a == idx) for idx in classes]
        idx_sort0 = reversed(numpy.argsort(frequency).tolist())
        idx_sort1 = reversed(numpy.argsort(frequency).tolist())

        return [{classes[i]: (r, frequency[i]) for r, i in enumerate(idx_sort0)},
                {r: (classes[i], frequency[i]) for r, i in enumerate(idx_sort1)}]

    def merge_classes(map, D, n_classes):
        new_map = {}
        n_initial_classes = D.shape[0]

        for i in range(n_classes):
            new_map[map[1][i][0]] = i

        to_be_merged_classes = [map[1][i][0] for i in range(n_classes, n_initial_classes)]
        for c in to_be_merged_classes:
            for i in numpy.argsort(D[c]):
                r = map[0][i][0]
                if r < n_classes and r != c:
                    new_map[c] = r

        return new_map

    # Order the classes by frequency and create an ordered list of those
    map = class_by_frequency(classified_samples)

    # Reduce the number of classes to retain only the fist n_classes by frequency
    # Samples belonging to lower frequency classes will be reassigned to the nearest
    # permitted class by hamming distance
    # TODO: evaluate if hierarchical clustering leads to better results

    new_classification = merge_classes(map=map, D=distance_matrix, n_classes=n_classes)
    return numpy.array([new_classification[i] for i in classified_samples])


def find_unique_classes(dbn_output):
    # Find the unique node patterns present in the output
    tmp = numpy.ascontiguousarray(dbn_output).view(numpy.dtype(
        (numpy.void, dbn_output.dtype.itemsize * dbn_output.shape[1])))
    _, idx = numpy.unique(tmp, return_index=True)
    class_representation = dbn_output[idx]
    # Find the Hamming distances among all the classes
    distance_matrix = distance.cdist(class_representation, class_representation, metric='hamming')
    # Assign each sample to a class
    classified_samples = numpy.zeros((dbn_output.shape[0]))
    output_nodes = dbn_output.shape[1]
    for idx, pattern in enumerate(class_representation):
        classified_samples = classified_samples + \
                             (numpy.sum(dbn_output == pattern, axis=1) == output_nodes) * idx

    return classified_samples, distance_matrix

def read_cmdline(argv, config_filename):
    log_enabled = False
    verbose = False
    daemonized = False
    port = 5000

    try:
        opts, args = getopt.getopt(argv, "hc:dlp:v", ["help", "config=", "daemon", "log", "port=", "verbose"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-v", "--verbose"):
            verbose = True
        elif opt in ("-c", "--config"):
            config_filename = arg
        elif opt in ("-l", "--log"):
            log_enabled = True
        elif opt in ("-d", "--dameon"):
            log_enabled = True
            daemonized = True
        elif opt in ("-p", "--port"):
            try:
                port = int(arg)
            except ValueError:
                raise ValueError('port must be a number beween 0 and 65535')
            if port < 0 or port > 65535:
                raise ValueError('port must be a number beween 0 and 65535')
        else:
            assert False, "unhandled option"

    return daemonized, port, config_filename, log_enabled, verbose

def usage():
    print("--help usage summary")
    print("--config=filename configuration file")
    print("--daemon listen for a JSON config")
    print("--port=port change the default listening port")
    print("--log=filename output file")
    print("--verbose print additional information during training")
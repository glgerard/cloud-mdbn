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

from __future__ import print_function, division

import os
import sys
import datetime
import traceback
import logging
import mdbnlogging
import getopt

from hashlib import md5

import numpy
import theano

from utils import load_n_preprocess_data
from utils import find_unique_classes
from utils import usage

from dbn import DBN

from six.moves import cPickle

def train_dbn(train_set, validation_set,
              name="",
              gauss=True,
              batch_size=20,
              k=1, layers_sizes=[40],
              pretraining_epochs=[800],
              pretrain_lr=[0.005],
              lambdas = [0.01, 0.1],
              rng=None,
              run=0,
              persistent=False,
              verbose=False,
              graph_output=False
              ):
    mdbnlogging.info('RUN:%i:DBN:%s:visible nodes:%i' % (run, name, train_set.get_value().shape[1]))
    mdbnlogging.info('RUN:%i:DBN:%s:output nodes:%i' % (run, name, layers_sizes[-1]))
    dbn = DBN(name=name, numpy_rng=rng, n_ins=train_set.get_value().shape[1],
              gauss=gauss,
              hidden_layers_sizes=layers_sizes[:-1],
              n_outs=layers_sizes[-1])

    dbn.training(train_set,
                 batch_size, k,
                 pretraining_epochs,
                 pretrain_lr,
                 lambdas,
                 persistent=persistent,
                 run=run,
                 verbose=verbose,
                 validation_set_x=validation_set,
                 graph_output=graph_output)

    output_train_set = dbn.get_output(train_set)
    if validation_set is not None:
        output_val_set = dbn.get_output(validation_set)
    else:
        output_val_set = None

    return dbn, output_train_set, output_val_set

def train_MDBN(datafiles,
               config,
               datadir='data',
               holdout=0,
               repeats=1,
               run=0,
               verbose=False,
               graph_output=False,
               output_folder='MDBN_run',
               network_file='network.npz',
               tmp_folder='tmp',
               rng=None):
    """
    :param datafiles: a dictionary with the path to the unimodal datasets

    :param datadir: directory where the datasets are located

    :param holdout: percentage of samples used for validation. By default there
                    is no validation set

    :param repeats: repeat each sample repeats time to artifically increase the size
                    of each dataset. By default data is not repeated

    :param graph_output: if True it will output graphical representation of the
                        network parameters

    :param output_folder: directory where the results are stored

    :param network_file: name of the file where the parameters are saved at the end
                        of the training

    :param log_file: file handle to log the run intermediate ouput

    :param rng: random number generator, by default is None and it is initialized
                by the function
    """

    if rng is None:
        rng = numpy.random.RandomState(123)

    if not os.path.isdir(tmp_folder):
        os.mkdir(tmp_folder)

    #################################
    #     Training the RBM          #
    #################################

    dbn_dict = dict()
    output_t_list = []
    output_v_list = []

    for pathway in config["pathways"]:
        mdbnlogging.info('RUN:%i:DBN:%s:start training' % (run, pathway))

        train_set, validation_set = load_n_preprocess_data(datafiles[pathway],
                                                       holdout=holdout,
                                                       repeats=repeats,
                                                       datadir=datadir,
                                                       rng=rng)

        netConfig = config['dbns'][pathway]
        netConfig['inputNodes'] = train_set.get_value().shape[1]

        config_hash = md5(str(netConfig.values())).hexdigest()

        dump_file = '%s/dbn_%s_%s_%d.save' % (tmp_folder, pathway, config_hash, run)
        if os.path.isfile(dump_file):
            with open(dump_file, 'rb') as f:
                dbn_dict[pathway] = cPickle.load(f)
        else:
            dbn_dict[pathway], _, _ = train_dbn(
                train_set, validation_set,
                name=pathway,
                gauss=True,
                batch_size=netConfig["batchSize"],
                k=netConfig["k"],
                layers_sizes=netConfig["layersNodes"],
                pretraining_epochs=netConfig["epochs"],
                pretrain_lr=netConfig["lr"],
                lambdas=netConfig["lambdas"],
                rng=rng,
                persistent=netConfig["persistent"],
                run=run,
                verbose=verbose,
                graph_output=graph_output)
            with open(dump_file, 'wb') as f:
                cPickle.dump(dbn_dict[pathway], f, protocol=cPickle.HIGHEST_PROTOCOL)

        output_t, output_v = dbn_dict[pathway].MLP_output_from_datafile(datafiles[pathway],
                                                                    holdout=holdout,
                                                                    repeats=repeats)
        output_t_list.append(output_t)
        output_v_list.append(output_v)

        for layer in range(dbn_dict[pathway].n_layers):
            rbm = dbn_dict[pathway].rbm_layers[layer]
            mdbnlogging.info('RUN:%i:DBN:%s:layer:%i:epoch:%i:minimum cost:%f' %
                             (run, rbm.name, layer, rbm.training_end_state[0], rbm.training_end_state[1]))

    mdbnlogging.info('RUN:%i:DBN:top:start training' % run)

    joint_train_set = theano.shared(numpy.hstack(output_t_list), borrow=True)

    if holdout > 0:
        joint_val_set = theano.shared(numpy.hstack(output_v_list), borrow=True)
    else:
        joint_val_set = None

    netConfig = config['top']
    netConfig['inputNodes'] = joint_train_set.get_value().shape[1]

    config_hash = md5(str(config)).hexdigest()

    dump_file = 'tmp/dbn_top_%s_%d.save' % (config_hash, run)
    if os.path.isfile(dump_file):
        with open(dump_file, 'rb') as f:
            dbn_dict['top'] = cPickle.load(f)
    else:
        dbn_dict['top'], _, _ = train_dbn(joint_train_set, joint_val_set,
                                          name='top',
                                          gauss=False,
                                          batch_size=netConfig["batchSize"],
                                          k=netConfig["k"],
                                          layers_sizes=netConfig["layersNodes"],
                                          pretraining_epochs=netConfig["epochs"],
                                          pretrain_lr=netConfig["lr"],
                                          rng=rng,
                                          persistent=netConfig["persistent"],
                                          run=run,
                                          verbose=verbose,
                                          graph_output=graph_output)
        with open(dump_file, 'wb') as f:
            cPickle.dump(dbn_dict['top'], f, protocol=cPickle.HIGHEST_PROTOCOL)

    # Computing the top-level output

    unimodal_dbn_output_list = []
    for pathway in config["pathways"]:
        dbn_output, _ = dbn_dict[pathway].MLP_output_from_datafile(datafiles[pathway])
        unimodal_dbn_output_list.append(dbn_output)

    joint_layer = theano.shared(numpy.hstack(unimodal_dbn_output_list), borrow=True)

    final_outuput = dbn_dict['top'].get_output(joint_layer)

    save_network(final_outuput, config, dbn_dict,
                 holdout, network_file, output_folder, repeats)

    return final_outuput

def save_network(top_output, config, dbn_dict, holdout, network_file, output_folder, repeats):
    if not os.path.isdir(output_folder):
        os.makedirs(output_folder)
    root_dir = os.getcwd()
    os.chdir(output_folder)
    dbn_params = {}
    for n in config['pathways']+['top']:
        dbn = dbn_dict[n]
        params = {}
        for p in dbn.params:
            if p.name in params:
                params[p.name].append(p.get_value())
            else:
                params[p.name] = [p.get_value()]
        dbn_params[n] = params

    numpy.savez(network_file,
                holdout=holdout,
                repeats=repeats,
                config=config,
                classes=top_output,
                dbn_params=dbn_params
                )
    os.chdir(root_dir)

def load_network(input_file, input_folder):
    root_dir = os.getcwd()
    # TODO: check if the input_folder exists
    os.chdir(input_folder)
    npz = numpy.load(input_file)

    config = npz['config'].tolist()
    dbn_params = npz['dbn_params'].tolist()

    dbn_dict = {}
    for key in config['pathways']+["top"]:
        params=dbn_params[key]
        if key != "top":
            netConfig = config['dbns'][key]
        else:
            netConfig = config['top']
        layer_sizes = netConfig['layersNodes']
        dbn_dict[key] = DBN(n_ins=netConfig['inputNodes'],
                            hidden_layers_sizes=layer_sizes[:-1],
                            gauss=key!='top',
                            n_outs=layer_sizes[-1],
                            W_list=params['W'],b_list=params['hbias'],c_list=params['vbias'])

    os.chdir(root_dir)

    return config, dbn_dict

def init(argv, batch_dir_prefix, config_filename, output_dir='MDBN_run'):
    global batch_output_dir
    global batch_start_date_str
    log_enabled = False
    verbose = False
    daemonized = False
    port = 5000

    try:
        opts, args = getopt.getopt(argv, "hc:dl:p:v", ["help", "config=", "daemon", "log=", "port=", "verbose"])
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

    batch_start_date = datetime.datetime.now()
    batch_start_date_str = batch_start_date.strftime("%Y-%m-%d_%H%M")

    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    batch_output_dir = '%s/%s_%s' % \
                       (output_dir, batch_dir_prefix, batch_start_date_str)
    if not os.path.isdir(batch_output_dir):
        os.mkdir(batch_output_dir)

    if verbose:
        log_level = mdbnlogging.DEBUG
    else:
        log_level = mdbnlogging.INFO

    if log_enabled:
        mdbnlogging.basicConfig(filename=batch_output_dir + '/batch.log', log_level=log_level)
    else:
        mdbnlogging.basicConfig(log_level=log_level)

    return daemonized, port, config_filename, verbose

def run(config, datafiles, verbose):
    numpy_rng = numpy.random.RandomState(config["seed"])

    results = []
    for run in range(config["runs"]):
        try:
            run_start_date = datetime.datetime.now()
            mdbnlogging.info('RUN:%i:start date:%s:start time:%s' % (run,
                                                                     run_start_date.strftime("%Y.%m.%d"),
                                                                     run_start_date.strftime("%H.%M.%S")))
            dbn_output = train_MDBN(datafiles,
                                    config,
                                    output_folder=batch_output_dir,
                                    network_file='Exp_%s_run_%d.npz' %
                                                 (batch_start_date_str, run),
                                    holdout=0.0, repeats=1,
                                    run=run,
                                    verbose=verbose,
                                    rng=numpy_rng)
            current_date_time = datetime.datetime.now()
            classes = find_unique_classes((dbn_output > 0.5) * numpy.ones_like(dbn_output))
            mdbnlogging.info('RUN:%i:classes identified:%d' % (run, numpy.max(classes[0])))
            results.append(classes[0])
            mdbnlogging.info('RUN:%i:stop date:%s:stop time:%s' % (run,
                                                                   current_date_time.strftime("%Y.%m.%d"),
                                                                   current_date_time.strftime("%H.%M.%S")))
        except:
            logging.error('RUN:%i:unexpected error:%s' % (run, sys.exc_info()[0]))
            logging.error('RUN:%i:unexpected error:%s' % (run, sys.exc_info()[1]))
            traceback.print_exc()
    root_dir = os.getcwd()
    os.chdir(batch_output_dir)
    numpy.savez('Results_%s.npz' % batch_start_date_str,
                results=results)
    os.chdir(root_dir)
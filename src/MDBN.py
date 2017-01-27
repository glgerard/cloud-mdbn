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
import datetime
import traceback
import logging

import numpy
import theano

from utils import load_n_preprocess_data
from utils import find_unique_classes
from dbn import DBN

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
    logging.info('RUN:%i:DBN:%s:visible nodes:%i' % (run,name,train_set.get_value().shape[1]))
    logging.info('RUN:%i:DBN:%s:output nodes:%i' % (run,name,layers_sizes[-1]))
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

    #################################
    #     Training the RBM          #
    #################################

    dbn_dict = dict()
    output_t_list = []
    output_v_list = []

    for pathway in config["pathways"]:
        logging.info('RUN:%i:DBN:%s:start training' % (run, pathway))

        train_set, validation_set = load_n_preprocess_data(datafiles[pathway],
                                                       holdout=holdout,
                                                       repeats=repeats,
                                                       datadir=datadir,
                                                       rng=rng)

        netConfig = config[pathway]
        netConfig['inputNodes'] = train_set.get_value().shape[1]

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

        output_t, output_v = dbn_dict[pathway].MLP_output_from_datafile(datafiles[pathway],
                                                                    holdout=holdout,
                                                                    repeats=repeats)
        output_t_list.append(output_t)
        output_v_list.append(output_v)

    logging.info('RUN:%i:DBN:top:start training' % run)

    joint_train_set = theano.shared(numpy.hstack(output_t_list), borrow=True)

    if holdout > 0:
        joint_val_set = theano.shared(numpy.hstack(output_v_list), borrow=True)
    else:
        joint_val_set = None

    netConfig = config['top']
    netConfig['inputNodes'] = joint_train_set.get_value().shape[1]

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

    # Identifying the classes

    dbn_output_list = []
    for pathway in config["pathways"]:
        dbn_output, _ = dbn_dict[pathway].MLP_output_from_datafile(datafiles[pathway])
        dbn_output_list.append(dbn_output)

    joint_output = theano.shared(numpy.hstack(dbn_output_list), borrow=True)

    classes = dbn_dict['top'].get_output(joint_output)

    save_network(classes, config, dbn_dict,
                 holdout, network_file, output_folder, repeats)

    return classes

def save_network(classes, config, dbn_dict, holdout, network_file, output_folder, repeats):
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
                classes=classes,
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
        netConfig = config[key]
        layer_sizes = netConfig['layersNodes']
        dbn_dict[key] = DBN(n_ins=netConfig['inputNodes'],
                            hidden_layers_sizes=layer_sizes[:-1],
                            gauss=key!='top',
                            n_outs=layer_sizes[-1],
                            W_list=params['W'],b_list=params['hbias'],c_list=params['vbias'])

    os.chdir(root_dir)

    return config, dbn_dict

def run_mdbn(batch_output_dir, batch_start_date_str, config, datafiles, numpy_rng, results, verbose):
    for run in range(config["runs"]):
        try:
            run_start_date = datetime.datetime.now()
            logging.info('RUN:%i:start date:%s:start time:%s' % (run,
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
            logging.info('RUN:%i:classes identified:%d' % (run, numpy.max(classes[0])))
            results.append(classes[0])
            logging.info('RUN:%i:stop date:%s:stop time:%s' % (run,
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
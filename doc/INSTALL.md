## Install Ubuntu 16.04 LTS

* Either [download](https://www.ubuntu.com/download/desktop) the image
and burn a DVD or download [UNetbootin](http://unetbootin.github.io/)
and prepare a Live CD
* Make sure the system is connected to Internet
* Start the installation
* Select install updates during installation
* DO NOT install 3rd party drivers.
* Choose a partition where to install Ubuntu
* Wait for the installation to complete

Reboot and select the Ubuntu install you just completed from the Grub menu

Open a terminal and at the prompt type

	sudo apt-get update
	sudo apt-get upgrade

If you get an error while running one of the two commands above,
wait for 10/20 seconds and retry.

Restart the Linux host

For further information refer to [Install Ubuntu 16.04 LTS](
https://www.ubuntu.com/download/desktop/install-ubuntu-desktop)

## Install CUDA

### Install the Nvidia display driver

Open a terminal and install the Nvidia Driver by typing

    sudo apt-get install nvidia-367

(you can check the available 3rd party drivers by typing $ sudo ubuntu-drivers devices)

As of January 2017 this will install the version 367.57

Restart the Linux host

### Install the CUDA Toolkit

Open a terminal and at the prompt type

    wget https://developer.nvidia.com/compute/cuda/8.0/prod/local_installers/cuda-repo-ubuntu1604-8-0-local_8.0.44-1_amd64-deb

Wait for the download to complete and then at the terminal prompt, from the directory where the previous file has been stored, type

	sudo dpkg -i cuda-repo-ubuntu1604-8-0-local_8.0.44-1_amd64-deb
	sudo apt-get update
	sudo apt-get install cuda

For further information refer to [CUDA Quick Start Guide](http://developer.download.nvidia.com/compute/cuda/8.0/secure/Prod2/docs/sidebar/CUDA_Quick_Start_Guide.pdf)

### Install CUDNN (Optional)

Register or Login in [Nvidia CUDNN](https://developer.nvidia.com/cudnn)

* Click on “Download”
* Accept the T&C
* Click on Download cuDNN v5 (May 27, 2016), for CUDA 8.0
* Click on cuDNN v5 Library for Linux

Wait for the download to complete and then at the terminal prompt,
from the directory where the previous file has been stored, type

	sudo tar --extract --directory /usr/local -f cudnn-8.0-linux-x64-v5.0-ga.tgz

Add `/usr/local/cuda/lib64` to the `LD_LIBRARY_PATH`. At the command prompt
type

	echo ‘export LD_LIBRARY_PATH=/usr/local/cuda/lib64:\$LD_LIBRARY_PATH’ >> .bashrc

## Install Enthought Canopy

Log-in and access [Download Canopy](
https://store.enthought.com/downloads/)

Select Canopy for Linux 64-bit

Open a terminal and from the directory where you have downloaded Canopy (typically ~/Downloads) type

	bash canopy-1.7.4-rh5-64.sh 

Read and accept the T&C and proceed.

Confirm the default installation directory (typically ~/Canopy)
Finalize and update the Canopy install

Start the Canopy GUI by typing at the command prompt

	~/Canopy/canopy

Press “Continue”

Select “Yes”

Select “Package Manager”

Select “Updates” and then “Update all”

For further information refer to [Linux Installation](
http://docs.enthought.com/canopy/quick-start/install_linux.html)

## Install Theano

Open a new terminal and at the prompt type. Make sure
that you are using Enthought Canopy python (verify with
`which python`)

	pip install Theano


Create a file `~/.theanorc` with the following content

    [global]
    device = gpu
    floatX = float32
    mode = FAST_RUN

    [cuda]
    root = /usr/local/cuda

    [nvcc]
    flags=-D_FORCE_INLINES

    [lib]
    cnmem = 0.75

Test the install with

	python
	>>> import theano
	Using gpu device 0: GeForce GTX 1070 (CNMeM is enabled with initial size: 75.0% of memory, cuDNN 5005)
	>>> from theano import tensor as T
	>>> x = T.matrix('x')
	>>> y = T.vector('y')
    >>> z = y * x
    >>> fn = theano.function([x,y],z)
    >>> import numpy as np
    >>> xv = np.ones((3,5),dtype=theano.config.floatX)
    >>> yv = np.ones((5),dtype=theano.config.floatX)
    >>> fn(xv,yv)
    array([[ 1.,  1.,  1.,  1.,  1.],
          [ 1.,  1.,  1.,  1.,  1.],
          [ 1.,  1.,  1.,  1.,  1.]], dtype=float32)
	>>> exit()

import tensorflow as tf


# see https://github.com/tensorflow/tpu/blob/master/tools/colab/keras_mnist_tpu.ipynb
def get_strategy():
    # Detect hardware
    try:
        # TPU detection
        tpu = tf.distribute.cluster_resolver.TPUClusterResolver()
    except ValueError:
        tpu = None
        gpus = tf.config.experimental.list_logical_devices("GPU")

    # Select appropriate distribution strategy
    if tpu:
        tf.tpu.experimental.initialize_tpu_system(tpu)
        # Going back and forth between TPU and host is expensive.
        # Better to run 128 batches on the TPU before reporting back.
        strategy = tf.distribute.experimental.TPUStrategy(tpu, steps_per_run=128)
        print('Running on TPU:', tpu.cluster_spec().as_dict()['worker'])
    elif len(gpus) > 1:
        strategy = tf.distribute.MirroredStrategy([gpu.name for gpu in gpus])
        print('Running on multiple GPUs:', [gpu.name for gpu in gpus])
    elif len(gpus) == 1:
        # default strategy that works on CPU and single GPU
        strategy = tf.distribute.get_strategy()
        print('Running on single GPU:', gpus[0].name)
    else:
        # default strategy that works on CPU and single GPU
        strategy = tf.distribute.get_strategy()
        print('Running on CPU')

    print("Number of accelerators:", strategy.num_replicas_in_sync)
    return strategy


def load_data(xmin=0, xmax=1):
    (X_train, y_train), (X_test, y_test) = tf.keras.datasets.mnist.load_data()
    image_shape = (28, 28, 1)

    # add channel to images (required by tensorflow)
    X_train = X_train.reshape(X_train.shape[0], *image_shape)
    X_test = X_test.reshape(X_test.shape[0], *image_shape)

    # convert images to floats
    X_train = X_train.astype('float32')
    X_test = X_test.astype('float32')

    # normalize images to [xmin,xmax]
    X_train = X_train * (xmax - xmin) / 255 + xmin
    X_test = X_test * (xmax - xmin) / 255 + xmin

    return (X_train, y_train), (X_test, y_test)


# coding: utf-8

# # Face Generation
# In this project, you'll use generative adversarial networks to generate new images of faces.
# ### Get the Data
# You'll be using two datasets in this project:
# - MNIST
# - CelebA
# 
# Since the celebA dataset is complex and you're doing GANs in a project for the first time, we want you to test your neural network on MNIST before CelebA.  Running the GANs on MNIST will allow you to see how well your model trains sooner.
# 
# If you're using [FloydHub](https://www.floydhub.com/), set `data_dir` to "/input" and use the [FloydHub data ID](http://docs.floydhub.com/home/using_datasets/) "R5KrjnANiKVhLWAkpXhNBe".

# In[1]:

data_dir = './data'

# FloydHub - Use with data ID "R5KrjnANiKVhLWAkpXhNBe"
#data_dir = '/input'


"""
DON'T MODIFY ANYTHING IN THIS CELL
"""
import helper

helper.download_extract('mnist', data_dir)
helper.download_extract('celeba', data_dir)


# ## Explore the Data
# ### MNIST
# As you're aware, the [MNIST](http://yann.lecun.com/exdb/mnist/) dataset contains images of handwritten digits. You can view the first number of examples by changing `show_n_images`. 

# In[2]:

show_n_images = 25

"""
DON'T MODIFY ANYTHING IN THIS CELL
"""
get_ipython().magic('matplotlib inline')
import os
from glob import glob
from matplotlib import pyplot

mnist_images = helper.get_batch(glob(os.path.join(data_dir, 'mnist/*.jpg'))[:show_n_images], 28, 28, 'L')
pyplot.imshow(helper.images_square_grid(mnist_images, 'L'), cmap='gray')


# In[83]:

# Find the minimum and maximum values in the MNIST images.
# First load the MNIST images and reshape them into one very long vector.
mnist_images = helper.get_batch(glob(os.path.join(data_dir, 'mnist/*.jpg')), 28, 28, 'L')
print(mnist_images.shape)
print(type(mnist_images))


# In[84]:

# MNIST images have values between 0 and 255.
print('Minimum =',np.min(mnist_images))
print('Maximum =',np.max(mnist_images))


# In[80]:

# Delete MNIST_IMAGES variable to clear memory.
mnist_images = None
del mnist_images


# ### CelebA
# The [CelebFaces Attributes Dataset (CelebA)](http://mmlab.ie.cuhk.edu.hk/projects/CelebA.html) dataset contains over 200,000 celebrity images with annotations.  Since you're going to be generating faces, you won't need the annotations.  You can view the first number of examples by changing `show_n_images`.

# In[3]:

show_n_images = 25

"""
DON'T MODIFY ANYTHING IN THIS CELL
"""
mnist_images = helper.get_batch(glob(os.path.join(data_dir, 'img_align_celeba/*.jpg'))[:show_n_images], 28, 28, 'RGB')
pyplot.imshow(helper.images_square_grid(mnist_images, 'RGB'))


# In[77]:

# Find the minimum and maximum values in the CelebA images.
# First load the CelebA images and reshape them into one very long vector.
celeba_images = helper.get_batch(glob(os.path.join(data_dir, 'img_align_celeba/*.jpg')), 28, 28, 'RGB')
print(celeba_images.shape)
print(type(celeba_images))


# In[78]:

print('Minimum =',np.min(celeba_images))
print('Maximum =',np.max(celeba_images))


# In[81]:

# Delete CELEBA_IMAGES variable to clear memory.
celeba_images = None
del celeba_images


# ## Preprocess the Data
# Since the project's main focus is on building the GANs, we'll preprocess the data for you.  The values of the MNIST and CelebA dataset will be in the range of -0.5 to 0.5 of 28x28 dimensional images.  The CelebA images will be cropped to remove parts of the image that don't include a face, then resized down to 28x28.
# 
# The MNIST images are black and white images with a single [color channel](https://en.wikipedia.org/wiki/Channel_(digital_image%29) while the CelebA images have [3 color channels (RGB color channel)](https://en.wikipedia.org/wiki/Channel_(digital_image%29#RGB_Images).
# ## Build the Neural Network
# You'll build the components necessary to build a GANs by implementing the following functions below:
# - `model_inputs`
# - `discriminator`
# - `generator`
# - `model_loss`
# - `model_opt`
# - `train`
# 
# ### Check the Version of TensorFlow and Access to GPU
# This will check to make sure you have the correct version of TensorFlow and access to a GPU

# In[4]:

"""
DON'T MODIFY ANYTHING IN THIS CELL
"""
from distutils.version import LooseVersion
import warnings
import tensorflow as tf

# Check TensorFlow Version
assert LooseVersion(tf.__version__) >= LooseVersion('1.0'), 'Please use TensorFlow version 1.0 or newer.  You are using {}'.format(tf.__version__)
print('TensorFlow Version: {}'.format(tf.__version__))

# Check for a GPU
if not tf.test.gpu_device_name():
    warnings.warn('No GPU found. Please use a GPU to train your neural network.')
else:
    print('Default GPU Device: {}'.format(tf.test.gpu_device_name()))


# ### Input
# Implement the `model_inputs` function to create TF Placeholders for the Neural Network. It should create the following placeholders:
# - Real input images placeholder with rank 4 using `image_width`, `image_height`, and `image_channels`.
# - Z input placeholder with rank 2 using `z_dim`.
# - Learning rate placeholder with rank 0.
# 
# Return the placeholders in the following the tuple (tensor of real input images, tensor of z data)

# In[5]:

import problem_unittests as tests

def model_inputs(image_width, image_height, image_channels, z_dim):
    """
    Create the model inputs
    :param image_width: The input image width
    :param image_height: The input image height
    :param image_channels: The number of image channels
    :param z_dim: The dimension of Z
    :return: Tuple of (tensor of real input images, tensor of z data, learning rate)
    """
    # Real input images placeholder with rank 4 using image_width, image_height, and image_channels.
    inputs_real = tf.placeholder(tf.float32, (None,image_width, image_height, image_channels), name='input_real')
    
    # Z input placeholder with rank 2 using z_dim.
    inputs_z = tf.placeholder(tf.float32, (None, z_dim), name='input_z')
    
    # Learning rate placeholder with rank 0.
    learn_rate  = tf.placeholder(tf.float32,name='learning_rate')
    return inputs_real, inputs_z, learn_rate


"""
DON'T MODIFY ANYTHING IN THIS CELL THAT IS BELOW THIS LINE
"""
tests.test_model_inputs(model_inputs)


# ### Discriminator
# Implement `discriminator` to create a discriminator neural network that discriminates on `images`.  This function should be able to reuse the variabes in the neural network.  Use [`tf.variable_scope`](https://www.tensorflow.org/api_docs/python/tf/variable_scope) with a scope name of "discriminator" to allow the variables to be reused.  The function should return a tuple of (tensor output of the generator, tensor logits of the generator).

# In[44]:

def discriminator(images, reuse=False):
    """
    Create the discriminator network
    :param image: Tensor of input image(s)
    :param reuse: Boolean if the weights should be reused
    :return: Tuple of (tensor output of the discriminator, tensor logits of the discriminator)
    """
    # Use tf.variable_scope with a scope name of "discriminator" to allow the variables to be reused.
    # 
    # In the 2016 ICLR conference paper entitled "Unsupervised Representational
    # Learning with Deep Convolutional Generative Adversarial Networks", authors
    # Radford, Metz, and Chintala introduce DCGANs to the literature, and provide
    # guidance on architectural topology and hyperparameter settings.
    # See especially Sections 3 and 4 of the paper.
    # Regarding the discriminator, Radford et al. suggest replacing any pooling
    # layers with strided convolutions, using batch normalization, removing
    # fully connected hidden layers, and using Leaky ReLUs.
    alpha = 0.2 # Radford et al. set the leak slope to 0.2 (Section 4).
    with tf.variable_scope('discriminator', reuse=reuse):
        # Input layer can be either 28x28x1 [MNIST] or 28x28x3 [CelebA]
        x1 = tf.layers.conv2d(images, 64, 5, strides=2, padding='same')
        relu1 = tf.maximum(alpha * x1, x1) # Leaky ReLU
        # 14x14x64
        
        x2 = tf.layers.conv2d(relu1, 128, 5, strides=2, padding='same')
        bn2 = tf.layers.batch_normalization(x2, training=True)
        relu2 = tf.maximum(alpha * bn2, bn2) # Leaky ReLU
        # 7x7x128
        
        x3 = tf.layers.conv2d(relu2, 256, 5, strides=2, padding='same')
        bn3 = tf.layers.batch_normalization(x3, training=True)
        relu3 = tf.maximum(alpha * bn3, bn3) # Leaky ReLU
        # 4x4x256

        # Flatten it
        flat = tf.reshape(relu3, (-1,4*4*256))
        logits = tf.layers.dense(flat, 1, activation=None)
        out = tf.sigmoid(logits)

    return out, logits


"""
DON'T MODIFY ANYTHING IN THIS CELL THAT IS BELOW THIS LINE
"""
tests.test_discriminator(discriminator, tf)


# ### Generator
# Implement `generator` to generate an image using `z`. This function should be able to reuse the variabes in the neural network.  Use [`tf.variable_scope`](https://www.tensorflow.org/api_docs/python/tf/variable_scope) with a scope name of "generator" to allow the variables to be reused. The function should return the generated 28 x 28 x `out_channel_dim` images.

# In[45]:

def generator(z, out_channel_dim, is_train=True):
    """
    Create the generator network
    :param z: Input z
    :param out_channel_dim: The number of channels in the output image
    :param is_train: Boolean if generator is being used for training
    :return: The tensor output of the generator
    """
    # Use tf.variable_scope with a scope name of "generator" to allow the variables to be reused.
    # 
    # In the 2016 ICLR conference paper entitled "Unsupervised Representational
    # Learning with Deep Convolutional Generative Adversarial Networks", authors
    # Radford, Metz, and Chintala introduce DCGANs to the literature, and provide
    # guidance on architectural topology and hyperparameter settings.
    # See especially Sections 3 and 4 of the paper.
    # Regarding the generator, Radford et al. suggest replacing any pooling
    # layers with fractional-strided convolutions, using batch normalization,
    # removing fully connected hidden layers, and using ReLU activation for all
    # layers except for the output, which uses Tanh.
    # According to the following two web pages
    # https://stackoverflow.com/questions/39373230/what-does-tensorflows-conv2d-transpose-operation-do
    # https://datascience.stackexchange.com/questions/6107/what-are-deconvolutional-layers
    # transpose convolution is the same thing as fractional-strided convolution,
    # and is the new (and better) name for what used to be called "deconvolution"
    # ("deconvolution" means recovering a filter kernel in signal processing, which
    # is something different from what we're doing here!).
    alpha = 0.2 # Radford et al. set the leak slope to 0.2 (Section 4).
    with tf.variable_scope('generator', reuse=not is_train):
        # First fully connected layer
        x1 = tf.layers.dense(z, 7*7*512)

        # Reshape it to start the convolutional stack
        # Note that Radford et al. did NOT use leakly ReLUs in their generators,
        # but they were used in the DCGAN notebook. I will try Leaky ReLU s here.
        x1 = tf.reshape(x1, (-1, 7, 7, 512))
        x1 = tf.layers.batch_normalization(x1, training=is_train)
        #x1 = tf.nn.relu(x1);
        x1 = tf.maximum(alpha * x1, x1) # Leaky ReLU
        # 7x7x512 now

        # Note use of transpose convolution (fractional convolution).
        # I had been wondering whether we ought to be using nearest
        # neighbor upsampling instead. Perhaps checkerboard pattern
        # artifacts secondary to transpose convolution is not so much
        # of an issue in GANs as it is in convolutional autoencoders.
        x2 = tf.layers.conv2d_transpose(x1, 256, 5, strides=2, padding='same')
        x2 = tf.layers.batch_normalization(x2, training=is_train)
        #x2 = tf.nn.relu(x2);
        x2 = tf.maximum(alpha * x2, x2) # Leaky ReLU
        # 14x14x256 now

        # Extra convolutional layer, if we want to try deepening the generator network.
        x3 = tf.layers.conv2d_transpose(x2, 128, 5, strides=2, padding='same')
        x3 = tf.layers.batch_normalization(x3, training=is_train)
        x3 = tf.maximum(alpha * x3, x3)
        # 28x28x128 now

        # Output layer
        logits = tf.layers.conv2d_transpose(x3, out_channel_dim, 5, strides=1, padding='same')
        # 28x28xout_channel_dim now

        out = tf.tanh(logits)

    return out

"""
DON'T MODIFY ANYTHING IN THIS CELL THAT IS BELOW THIS LINE
"""
tests.test_generator(generator, tf)


# ### Loss
# Implement `model_loss` to build the GANs for training and calculate the loss.  The function should return a tuple of (discriminator loss, generator loss).  Use the following functions you implemented:
# - `discriminator(images, reuse=False)`
# - `generator(z, out_channel_dim, is_train=True)`

# In[46]:

def model_loss(input_real, input_z, out_channel_dim, smooth = 0.1):
    """
    Get the loss for the discriminator and generator
    :param input_real: Images from the real dataset
    :param input_z: Z input
    :param out_channel_dim: The number of channels in the output image
    :return: A tuple of (discriminator loss, generator loss)
    """
    # Implement model_loss to build the GANs for training and calculate the loss.
    # Use the following functions you implemented:
    # discriminator(images, reuse=False)
    # generator(z, out_channel_dim, is_train=True)
    g_model = generator(input_z, out_channel_dim)
    d_model_real, d_logits_real = discriminator(input_real)
    d_model_fake, d_logits_fake = discriminator(g_model, reuse=True)

    # Compute sigmoid cross-entropy from the logits.
    # 
    # In the 2016 ICLR conference paper entitled "Unsupervised Representational
    # Learning with Deep Convolutional Generative Adversarial Networks", authors
    # Radford, Metz, and Chintala introduce DCGANs to the literature, and provide
    # guidance on architectural topology and hyperparameter settings.
    # See especially Sections 3 and 4 of the paper. Radford et al. say nothing
    # about using label smoothing with DCGANs, so I will not do so here.
    d_loss_real = tf.reduce_mean(
        tf.nn.sigmoid_cross_entropy_with_logits(logits=d_logits_real, labels=tf.ones_like(d_model_real)))
    d_loss_fake = tf.reduce_mean(
        tf.nn.sigmoid_cross_entropy_with_logits(logits=d_logits_fake, labels=tf.zeros_like(d_model_fake)))
    g_loss = tf.reduce_mean(
        tf.nn.sigmoid_cross_entropy_with_logits(logits=d_logits_fake, labels=tf.ones_like(d_model_fake)))

    # Below is commented out code for label smoothing, not being used at this time.
    #d_loss_real = tf.reduce_mean(
    #    tf.nn.sigmoid_cross_entropy_with_logits(logits=d_logits_real, labels=tf.ones_like(d_logits_real)*(1-smooth)))
    # Compute total discriminator loss as the sum of losses from real and fake images.
    d_loss = d_loss_real + d_loss_fake

    # Return a tuple of (discriminator loss, generator loss)
    return d_loss, g_loss


"""
DON'T MODIFY ANYTHING IN THIS CELL THAT IS BELOW THIS LINE
"""
tests.test_model_loss(model_loss)


# ### Optimization
# Implement `model_opt` to create the optimization operations for the GANs. Use [`tf.trainable_variables`](https://www.tensorflow.org/api_docs/python/tf/trainable_variables) to get all the trainable variables.  Filter the variables with names that are in the discriminator and generator scope names.  The function should return a tuple of (discriminator training operation, generator training operation).

# In[53]:

def model_opt(d_loss, g_loss, learning_rate, beta1):
    """
    Get optimization operations
    :param d_loss: Discriminator loss Tensor
    :param g_loss: Generator loss Tensor
    :param learning_rate: Learning Rate Placeholder
    :param beta1: The exponential decay rate for the 1st moment in the optimizer
    :return: A tuple of (discriminator training operation, generator training operation)
    """
    # Filter the variables with names that are in the discriminator and generator scope names.
    t_vars = tf.trainable_variables()
    d_vars = [var for var in t_vars if var.name.startswith('discriminator')]
    g_vars = [var for var in t_vars if var.name.startswith('generator')]

    # Optimize
    with tf.control_dependencies(tf.get_collection(tf.GraphKeys.UPDATE_OPS)):
        d_train_opt = tf.train.AdamOptimizer(learning_rate, beta1=beta1).minimize(d_loss, var_list=d_vars)
        g_train_opt = tf.train.AdamOptimizer(learning_rate, beta1=beta1).minimize(g_loss, var_list=g_vars)
    
    # The function should return a tuple of (discriminator training operation, generator training operation).
    return d_train_opt, g_train_opt


"""
DON'T MODIFY ANYTHING IN THIS CELL THAT IS BELOW THIS LINE
"""
tests.test_model_opt(model_opt, tf)


# ## Neural Network Training
# ### Show Output
# Use this function to show the current output of the generator during training. It will help you determine how well the GANs is training.

# In[10]:

"""
DON'T MODIFY ANYTHING IN THIS CELL
"""
import numpy as np

def show_generator_output(sess, n_images, input_z, out_channel_dim, image_mode):
    """
    Show example output for the generator
    :param sess: TensorFlow session
    :param n_images: Number of Images to display
    :param input_z: Input Z Tensor
    :param out_channel_dim: The number of channels in the output image
    :param image_mode: The mode to use for images ("RGB" or "L")
    """
    cmap = None if image_mode == 'RGB' else 'gray'
    z_dim = input_z.get_shape().as_list()[-1]
    example_z = np.random.uniform(-1, 1, size=[n_images, z_dim])

    samples = sess.run(
        generator(input_z, out_channel_dim, False),
        feed_dict={input_z: example_z})

    images_grid = helper.images_square_grid(samples, image_mode)
    pyplot.imshow(images_grid, cmap=cmap)
    pyplot.show()


# ### Train
# Implement `train` to build and train the GANs.  Use the following functions you implemented:
# - `model_inputs(image_width, image_height, image_channels, z_dim)`
# - `model_loss(input_real, input_z, out_channel_dim)`
# - `model_opt(d_loss, g_loss, learning_rate, beta1)`
# 
# Use the `show_generator_output` to show `generator` output while you train. Running `show_generator_output` for every batch will drastically increase training time and increase the size of the notebook.  It's recommended to print the `generator` output every 100 batches.

# In[50]:

def train(epoch_count, batch_size, z_dim, learning_rate, beta1, get_batches, data_shape, data_image_mode):
    """
    Train the GAN
    :param epoch_count: Number of epochs
    :param batch_size: Batch Size
    :param z_dim: Z dimension
    :param learning_rate: Learning Rate
    :param beta1: The exponential decay rate for the 1st moment in the optimizer
    :param get_batches: Function to get batches
    :param data_shape: Shape of the data
    :param data_image_mode: The image mode to use for images ("RGB" or "L")
    """
    # Build Model. Use the following functions you implemented:
    # model_inputs(image_width, image_height, image_channels, z_dim)
    # model_loss(input_real, input_z, out_channel_dim)
    # model_opt(d_loss, g_loss, learning_rate, beta1)
    #tf.reset_default_graph()
    out_channel_dim = data_shape[3]
    if data_image_mode == "L":
        out_channel_dim = 1
    else:
        out_channel_dim = 3
    input_real, input_z, learn_rate = model_inputs(data_shape[1], data_shape[2], data_shape[3], z_dim)
    d_loss, g_loss = model_loss(input_real, input_z, out_channel_dim)
    d_opt, g_opt = model_opt(d_loss, g_loss, learn_rate, beta1)

    # Perform training.
    batch_count = round(data_shape[0]/batch_size) # Number of batches per epoch
    num_batches = 0
    train_loss_d = 0
    train_loss_g = 1
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        for epoch_i in range(epoch_count):
            batch_j = 0
            for batch_images in get_batches(batch_size):
                # Keep track of the number of batches
                batch_j += 1     # Number of batches WITHIN epoch
                num_batches += 1 # Number of batches ACROSS epochs

                # I tried various rescaling of pixel values, but they
                # seem to make things worse!
                # As per information in the Preprocess the Data section, the
                # values of the MNIST and CelebA dataset will be in the
                # range of -0.5 to 0.5 of 28x28 dimensional images.
                # Multiply them by 2 to bring them to the range of [-1,1].
                # The generator output is from the TANH function, so it
                # has a theoretical range of [-1,1].
                batch_images = 2 * batch_images
                #batch_images = ( batch_images / 255 )
                #batch_images = ( batch_images / 255 ) - 0.5
                #batch_images = ( 2 * batch_images / 255 ) - 1

                # Sample random noise for Generator
                batch_z = np.random.uniform(-1, 1, size=(batch_size, z_dim))

                # Run optimizers.
                # Here I am trying the idea of training the generator twice for
                # every 
                ## See pradau's commen posted 5/31/2017 at 11:46 AM.
                # https://github.com/llSourcell/Generative_Adversarial_networks_LIVE
                _ = sess.run(d_opt, feed_dict={input_real: batch_images, input_z: batch_z, learn_rate: learning_rate})
                _ = sess.run(g_opt, feed_dict={input_real: batch_images, input_z: batch_z, learn_rate: learning_rate})
                
                # I also tried the idea of conditional optimization
                # where one selectively trains either the discriminator or
                # the generator if one or the other is doing badly.
                # See Siraj's EZGAN notebook from his YouTube presentation
                # and his implementation of a "controller". My implementation
                # here isn't exactly the same, but is the same idea.
                # https://github.com/llSourcell/Generative_Adversarial_networks_LIVE
                #if train_loss_d > train_loss_g:
                #    _ = sess.run(d_opt, feed_dict={input_real: batch_images, input_z: batch_z, learn_rate: learning_rate})
                #if train_loss_g > train_loss_d or train_loss_g > 0.5:
                #    _ = sess.run(g_opt, feed_dict={input_real: batch_images, input_z: batch_z, learn_rate: learning_rate})

                train_loss_d = d_loss.eval({input_z: batch_z, input_real: batch_images})
                train_loss_g = g_loss.eval({input_z: batch_z})
                
                # Show losses every 10 batches.
                if num_batches % 10 == 0:
                    # Get the losses and print them out.
                    #train_loss_d = d_loss.eval({input_z: batch_z, input_real: batch_images})
                    #train_loss_g = g_loss.eval({input_z: batch_z})
                    print("Batch {}/{}, Epoch {}/{}...".format(batch_j,batch_count,epoch_i+1,epoch_count),
                          "Discriminator Loss: {:.4f}...".format(train_loss_d),
                          "Generator Loss: {:.4f}".format(train_loss_g))

                # It's recommended to print the generator output every 100 batches.
                if num_batches % 100 == 0:
                    # Show generator output.
                    show_generator_output(sess, 25, input_z, out_channel_dim, data_image_mode)
            


# ### MNIST
# Test your GANs architecture on MNIST.  After 2 epochs, the GANs should be able to generate images that look like handwritten digits.  Make sure the loss of the generator is lower than the loss of the discriminator or close to 0.

# In[ ]:

# In the 2016 ICLR conference paper entitled "Unsupervised Representational
# Learning with Deep Convolutional Generative Adversarial Networks", authors
# Radford, Metz, and Chintala introduce DCGANs to the literature, and provide
# guidance on architectural topology and hyperparameter settings.
# See especially Sections 3 and 4 of the paper. Radford et al. say that
# the suggested learning rate of 0.001 was too high, and used 0.0002 instead.
# They also found that leaving the momentum term BETA1 at the suggested value
# of 0.9 resulted in training oscillation and instability, while reducing it
# to 0.5 helped stabilize training.
batch_size = 128
z_dim = 100
learning_rate = 0.0002
beta1 = 0.5

tf.reset_default_graph()

"""
DON'T MODIFY ANYTHING IN THIS CELL THAT IS BELOW THIS LINE
"""
epochs = 2

mnist_dataset = helper.Dataset('mnist', glob(os.path.join(data_dir, 'mnist/*.jpg')))
with tf.Graph().as_default():
    train(epochs, batch_size, z_dim, learning_rate, beta1, mnist_dataset.get_batches,
          mnist_dataset.shape, mnist_dataset.image_mode)


# ### CelebA
# Run your GANs on CelebA.  It will take around 20 minutes on the average GPU to run one epoch.  You can run the whole epoch or stop when it starts to generate realistic faces.

# In[ ]:

# In the 2016 ICLR conference paper entitled "Unsupervised Representational
# Learning with Deep Convolutional Generative Adversarial Networks", authors
# Radford, Metz, and Chintala introduce DCGANs to the literature, and provide
# guidance on architectural topology and hyperparameter settings.
# See especially Sections 3 and 4 of the paper. Radford et al. say that
# the suggested learning rate of 0.001 was too high, and used 0.002 instead.
# They also found that leaving the momentum term BETA1 at the suggested value
# of 0.9 resulted in training oscillation and instability, while reducing it
# to 0.5 helped stabilize training.
batch_size = 64
z_dim = 100
learning_rate = 0.0002
beta1 = Non0.5


"""
DON'T MODIFY ANYTHING IN THIS CELL THAT IS BELOW THIS LINE
"""
epochs = 1

celeba_dataset = helper.Dataset('celeba', glob(os.path.join(data_dir, 'img_align_celeba/*.jpg')))
with tf.Graph().as_default():
    train(epochs, batch_size, z_dim, learning_rate, beta1, celeba_dataset.get_batches,
          celeba_dataset.shape, celeba_dataset.image_mode)


# ### Submitting This Project
# When submitting this project, make sure to run all the cells before saving the notebook. Save the notebook file as "dlnd_face_generation.ipynb" and save it as a HTML file under "File" -> "Download as". Include the "helper.py" and "problem_unittests.py" files in your submission.

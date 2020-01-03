# coding=utf-8
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import tensorflow as tf


# From tensor2tensor/data_generators/imagenet.py
def preprocess_image(image,
                     mode,
                     resize_size=None,
                     normalize=True,
                     image_statistics=None,
                     crop_area_min=0.50,
                     contrast_lower=0.2,
                     contrast_upper=0.6,
                     brightness_delta_min=-0.2,
                     brightness_delta_max=0.2):

  if normalize:
    if not image_statistics:
      raise ValueError("If `normalize`, then `image_statistics` is required.")
    mean_rgb = image_statistics["mean"]
    stddev_rgb = image_statistics["sd"]

  resize_size = resize_size or [299, 299]
  assert resize_size[0] == resize_size[1]
  image_size = resize_size[0]

  if normalize:
    image = tf.to_float(image) / 255.0

  brightness_delta = tf.random.uniform(shape=(),
                                       minval=brightness_delta_min,
                                       maxval=brightness_delta_max,
                                       dtype=tf.dtypes.float32,
                                       seed=None,
                                       name=None)

  if mode == tf.estimator.ModeKeys.TRAIN:
    image = _random_crop(image, size=image_size, area_min=crop_area_min)
    if normalize:
      image = _normalize(image, mean_rgb, stddev_rgb)
    image = _flip(image)

    image = tf.image.adjust_brightness(image, delta=brightness_delta)

    image = tf.image.random_contrast(image,
                                     lower=contrast_lower,
                                     upper=contrast_upper,
                                     seed=None)

  else:
    image = _do_scale(image, image_size + 32)

    # Might want to remove this at inference time as it may not be
    # applicable whereas we intend to have trained models that are
    # invariant to this...
    if normalize:
      image = _normalize(image, mean_rgb, stddev_rgb)

    image = _center_crop(image, image_size)

  image = tf.reshape(image, [image_size, image_size, 3])
  return image


# The following preprocessing functions were taken from
# cloud_tpu/models/resnet/resnet_preprocessing.py
# ==============================================================================
def _crop(image, offset_height, offset_width, crop_height, crop_width):
  """Crops the given image using the provided offsets and sizes.
  Note that the method doesn't assume we know the input image size but it does
  assume we know the input image rank.
  Args:
    image: `Tensor` image of shape [height, width, channels].
    offset_height: `Tensor` indicating the height offset.
    offset_width: `Tensor` indicating the width offset.
    crop_height: the height of the cropped image.
    crop_width: the width of the cropped image.
  Returns:
    the cropped (and resized) image.
  Raises:
    InvalidArgumentError: if the rank is not 3 or if the image dimensions are
      less than the crop size.
  """
  original_shape = tf.shape(image)

  rank_assertion = tf.Assert(tf.equal(tf.rank(image), 3),
                             ["Rank of image must be equal to 3."])
  with tf.control_dependencies([rank_assertion]):
    cropped_shape = tf.stack([crop_height, crop_width, original_shape[2]])

  size_assertion = tf.Assert(
      tf.logical_and(tf.greater_equal(original_shape[0], crop_height),
                     tf.greater_equal(original_shape[1], crop_width)),
      ["Crop size greater than the image size."])

  offsets = tf.to_int32(tf.stack([offset_height, offset_width, 0]))

  # Use tf.slice instead of crop_to_bounding box as it accepts tensors to
  # define the crop size.
  with tf.control_dependencies([size_assertion]):
    image = tf.slice(image, offsets, cropped_shape)
  return tf.reshape(image, cropped_shape)


def distorted_bounding_box_crop(image,
                                bbox,
                                min_object_covered=0.1,
                                aspect_ratio_range=(0.75, 1.33),
                                area_range=(0.05, 1.0),
                                max_attempts=100,
                                scope=None):
  """Generates cropped_image using a one of the bboxes randomly distorted.
  See `tf.image.sample_distorted_bounding_box` for more documentation.
  Args:
    image: `Tensor` of image (it will be converted to floats in [0, 1]).
    bbox: `Tensor` of bounding boxes arranged `[1, num_boxes, coords]`
        where each coordinate is [0, 1) and the coordinates are arranged
        as `[ymin, xmin, ymax, xmax]`. If num_boxes is 0 then use the whole
        image.
    min_object_covered: An optional `float`. Defaults to `0.1`. The cropped
        area of the image must contain at least this fraction of any bounding
        box supplied.
    aspect_ratio_range: An optional list of `float`s. The cropped area of the
        image must have an aspect ratio = width / height within this range.
    area_range: An optional list of `float`s. The cropped area of the image
        must contain a fraction of the supplied image within in this range.
    max_attempts: An optional `int`. Number of attempts at generating a cropped
        region of the image of the specified constraints. After `max_attempts`
        failures, return the entire image.
    scope: Optional `str` for name scope.
  Returns:
    (cropped image `Tensor`, distorted bbox `Tensor`).
  """
  with tf.name_scope(scope,
                     default_name="distorted_bounding_box_crop",
                     values=[image, bbox]):
    # Each bounding box has shape [1, num_boxes, box coords] and
    # the coordinates are ordered [ymin, xmin, ymax, xmax].

    # A large fraction of image datasets contain a human-annotated bounding
    # box delineating the region of the image containing the object of interest.
    # We choose to create a new bounding box for the object which is a randomly
    # distorted version of the human-annotated bounding box that obeys an
    # allowed range of aspect ratios, sizes and overlap with the human-annotated
    # bounding box. If no box is supplied, then we assume the bounding box is
    # the entire image.
    sample_distorted_bounding_box = tf.image.sample_distorted_bounding_box(
        tf.shape(image),
        bounding_boxes=bbox,
        min_object_covered=min_object_covered,
        aspect_ratio_range=aspect_ratio_range,
        area_range=area_range,
        max_attempts=max_attempts,
        use_image_if_no_bounding_boxes=True)
    bbox_begin, bbox_size, distort_bbox = sample_distorted_bounding_box

    # Crop the image to the specified bounding box.
    cropped_image = tf.slice(image, bbox_begin, bbox_size)
    return cropped_image, distort_bbox


def _random_crop(image, size, area_min=0.08):
  """Make a random crop of (`size` x `size`)."""
  bbox = tf.constant([0.0, 0.0, 1.0, 1.0], dtype=tf.float32, shape=[1, 1, 4])
  random_image, bbox = distorted_bounding_box_crop(image,
                                                   bbox,
                                                   min_object_covered=0.1,
                                                   aspect_ratio_range=(3. / 4,
                                                                       4. / 3.),
                                                   area_range=(area_min, 1.0),
                                                   max_attempts=1,
                                                   scope=None)
  bad = _at_least_x_are_true(tf.shape(image), tf.shape(random_image), 3)

  image = tf.cond(
      bad, lambda: _center_crop(_do_scale(image, size), size),
      lambda: tf.image.resize_bicubic([random_image], [size, size])[0])
  return image


def _flip(image):
  """Random horizontal image flip."""
  image = tf.image.random_flip_left_right(image)
  return image


def _at_least_x_are_true(a, b, x):
  """At least `x` of `a` and `b` `Tensors` are true."""
  match = tf.equal(a, b)
  match = tf.cast(match, tf.int32)
  return tf.greater_equal(tf.reduce_sum(match), x)


def _do_scale(image, size):
  """Rescale the image by scaling the smaller spatial dimension to `size`."""
  shape = tf.cast(tf.shape(image), tf.float32)
  w_greater = tf.greater(shape[0], shape[1])
  shape = tf.cond(w_greater,
                  lambda: tf.cast([shape[0] / shape[1] * size, size], tf.int32),
                  lambda: tf.cast([size, shape[1] / shape[0] * size], tf.int32))

  return tf.image.resize_bicubic([image], shape)[0]


def _center_crop(image, size):
  """Crops to center of image with specified `size`."""
  image_height = tf.shape(image)[0]
  image_width = tf.shape(image)[1]

  offset_height = ((image_height - size) + 1) / 2
  offset_width = ((image_width - size) + 1) / 2
  image = _crop(image, offset_height, offset_width, size, size)
  return image


def _normalize(image, mean_rgb, stddev_rgb):
  """Normalize the image to zero mean and unit variance."""
  offset = tf.constant(mean_rgb, shape=[1, 1, 3])
  image -= offset

  scale = tf.constant(stddev_rgb, shape=[1, 1, 3])
  image /= scale
  return image

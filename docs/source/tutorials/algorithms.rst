Using Ethical Gardeners with Custom Algorithms
==============================================

This tutorial explains how to integrate your own reinforcement learning algorithms with the Ethical Gardeners environment.

Compatibility with Custom Algorithms
------------------------------------

The Ethical Gardeners environment is designed to work with various reinforcement learning algorithms, including custom
ones. While we provide built-in support for `Stable Baselines 3 <https://stable-baselines3.readthedocs.io/en/master/>`__,
you can use your own algorithms by following these guidelines.

Requirements for Custom Algorithms
----------------------------------

To use your algorithm with the utility functions provided by Ethical Gardeners:

1. For the :py:func:`~ethical_gardeners.algorithms.train` function, your algorithm should have:

   - a ``learn()`` method that accepts a ``total_timesteps`` parameter
   - a ``save()`` method to persist the trained model

2. For the :py:func:`~ethical_gardeners.algorithms.evaluate` and the :py:func:`~ethical_gardeners.algorithms.predict_action` functions, your algorithm should have:

   - a ``predict()`` method that takes observations and if you want action masks and returns actions

Using the Core Utility Functions
--------------------------------

The following code snippet is a minimal example of how to use the training, evaluation, and prediction functions with a custom algorithm. The example
uses the `MaskablePPO algorithm from sb3-contrib <https://sb3-contrib.readthedocs.io/en/master/modules/ppo_mask.html>`__
for an example of an algorithm that supports action masking and the `DQN algorithm from
Stable Baselines 3 <https://stable-baselines3.readthedocs.io/en/master/modules/dqn.html>`__ for an example of an
algorithm that does not support action masking.

For training, the :py:func:`~ethicalgardeners.algorithms.train` function accepts a model so the model must be instantiated
beforehand. In the example, we instantiate the model with the environment and a policy. The environment is either a default
Ethical Gardeners environment made with the :py:func:`~ethicalgardeners.main.make_env` function or a vectorized one with
multiple environments.

For training, evaluation and prediction, you must say whether your algorithm supports action masking or not. If it does, the
``needs_action_mask`` parameter should be set to ``True``. If it does not, it should be set to ``False``.

.. literalinclude:: /examples/trainevaluatepredict.py
   :language: python
   :caption: trainevaluatepredict.py
   :name: trainevaluatepredict
   :encoding: utf-8
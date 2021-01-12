import unittest
from GCEm.nn_model import NNModel
from GCEm.utils import get_uniform_params
from tests.mock import *
from numpy.testing import assert_allclose


class NNTest(unittest.TestCase):
    """
    Tests on the GPModel class and its methods. The actual model is setup
     independently in the concrete test classes below. This abstracts the
     different test cases out and allows the model to only be created once
     for each test case.
    """

    @classmethod
    def setUpClass(cls) -> None:
        params, test = pop_elements(get_uniform_params(3), 50)

        ensemble = get_three_param_cube(params)
        m = NNModel(params, ensemble)
        m.train(epochs=50)

        cls.model = m
        cls.params = params
        cls.test_params = test
        cls.eval_fn = eval_cube

    def test_simple_predict(self):

        # Get the actual test data
        #  Use the class method `eval_fn` so 'self' doesn't get passed
        expected = type(self).eval_fn(self.test_params[0])

        pred_m, pred_var = self.model._predict(self.test_params[0:1])

        # This is a very loose tolerance, I'm not really interested in
        #  exactly fitting the data for this test
        assert_allclose(expected.data, pred_m, rtol=1)

    def test_simple_predict_with_time_1(self):
        params, test = pop_elements(get_uniform_params(3), 50)

        ensemble = get_three_param_cube(params, time_len=1)
        model = NNModel(params, ensemble)
        model.train(epochs=50)

        # Get the actual test data
        #  Use the class method `eval_fn` so 'self' doesn't get passed
        expected = eval_cube(self.test_params[0], time_len=1)

        pred_m, pred_var = model._predict(self.test_params[0:1])

        # This is a very loose tolerance, I'm not really interested in
        #  exactly fitting the data for this test
        assert_allclose(expected.data, pred_m, rtol=1)

    def test_simple_predict_with_invalid_shape(self):
        params, test = pop_elements(get_uniform_params(2), 50)

        # The ConvNet won't work with a 1D cube
        ensemble = get_1d_two_param_cube(params)
        with self.assertRaises(ValueError):
            model = NNModel(params, ensemble)

    def test_simple_predict_with_time(self):
        params, test = pop_elements(get_uniform_params(3), 50)

        ensemble = get_three_param_cube(params, time_len=12)
        model = NNModel(params, ensemble)
        model.train(epochs=50)

        # Get the actual test data
        #  Use the class method `eval_fn` so 'self' doesn't get passed
        expected = eval_cube(self.test_params[0], time_len=12)

        pred_m, pred_var = model._predict(self.test_params[0:1])

        # This is a very loose tolerance, I'm not really interested in
        #  exactly fitting the data for this test
        assert_allclose(expected.data, pred_m, rtol=1)

    def test_simple_predict_with_different_optimizer(self):
        params, test = pop_elements(get_uniform_params(3), 50)

        ensemble = get_three_param_cube(params, time_len=12)
        model = NNModel(params, ensemble, optimizer='Adam')
        model.train(epochs=50)

        # Get the actual test data
        #  Use the class method `eval_fn` so 'self' doesn't get passed
        expected = eval_cube(self.test_params[0], time_len=12)

        pred_m, pred_var = model._predict(self.test_params[0:1])

        # This is a very loose tolerance, I'm not really interested in
        #  exactly fitting the data for this test
        assert_allclose(expected.data, pred_m, rtol=1)

    def test_predict_interface(self):

        # Get the actual test data
        #  Use the class method `eval_fn` so 'self' doesn't get passed
        expected = type(self).eval_fn(self.test_params[0])

        pred_m, pred_var = self.model.predict(self.test_params[0:1])

        # This is a very loose tolerance, I'm not really interested in
        #  exactly fitting the data for this test
        assert_allclose(expected.data, pred_m.data, rtol=1)
        assert pred_m.name() == 'Emulated ' + expected.name()
        assert pred_var is None
        assert pred_m.units == expected.units

    def test_predict_interface_multiple_samples(self):
        from iris.cube import CubeList
        # Get the actual test data
        #  Use the class method `eval_fn` so 'self' doesn't get passed
        expected = CubeList([type(self).eval_fn(p, job_n=i) for i, p in enumerate(self.test_params)])
        expected = expected.concatenate_cube()

        pred_m, pred_var = self.model.predict(self.test_params)

        assert_allclose(expected.data, pred_m.data, rtol=1)
        assert pred_m.name() == 'Emulated ' + (expected.name() or 'data')
        assert pred_var is None
        assert pred_m.units == expected.units

    def test_batch_stats(self):
        from iris.cube import CubeList
        from GCEm.utils import get_random_params
        # Test that the sample_mean function returns the mean of the sample

        sample_params = get_random_params(self.params.shape[1], 1000)

        expected = CubeList([type(self).eval_fn(p, job_n=i) for i, p in enumerate(sample_params)])
        expected_ensemble = expected.concatenate_cube()

        mean, std_dev = self.model.batch_stats(sample_params, batch_size=1)

        # This is a really loose test but it needs to be because of the
        #  stochastic nature of the model and the ensemble points
        assert_allclose(mean.data, expected_ensemble.data.mean(axis=0), rtol=1.)
        assert_allclose(std_dev.data, expected_ensemble.data.std(axis=0), rtol=5.)


if __name__ == '__main__':
    unittest.main()

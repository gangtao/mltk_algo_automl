import pandas as pd
import os
from algos_contrib.AutoRegressor import AutoRegressor
from test.contrib_util import AlgoTestUtils

def test_fit_apply():
    path = os.path.join(os.path.dirname(__file__), 'iris.csv')
    input_df = pd.read_csv(path)

    options = {}
    options['target_variable'] = ['sepal_length']
    options['feature_variables'] = [
        'sepal_width', 'petal_length', 'petal_width']

    algo = AutoRegressor(options)

    algo.fit(input_df, options)

    prediction = algo.apply(input_df, options)
    assert prediction.shape == (150, 5)

from sklearn import datasets
import sklearn.decomposition
import sklearn.linear_model
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline

from baikal.core.model import Model
from baikal.core.step import Input
from baikal.sklearn import SKLearnWrapper

from tests.helpers.sklearn_steps import PCA, LogisticRegression

iris = datasets.load_iris()


def test_grid_search_cv():
    x_data = iris.data
    y_data = iris.target
    random_state = 123
    verbose = 0

    param_grid = {'pca__n_components': [2, 4],
                  'logreg__C': [0.1, 1.0, 10],
                  'logreg__penalty': ['l1', 'l2']}
    cv = StratifiedKFold(3)  # cv will default to KFold if the estimator is a baikal Model

    # baikal way
    def build_fn():
        x = Input()
        h = PCA(random_state=random_state, name='pca')(x)
        y = LogisticRegression(random_state=random_state, name='logreg')(h)
        model = Model(x, y)
        return model

    sk_model = SKLearnWrapper(build_fn)
    gscv_baikal = GridSearchCV(sk_model, param_grid, cv=cv, scoring='accuracy', verbose=verbose)
    gscv_baikal.fit(x_data, y_data)

    # traditional way
    pca = sklearn.decomposition.PCA(random_state=random_state)
    logreg = sklearn.linear_model.LogisticRegression(random_state=random_state)
    pipe = Pipeline([('pca', pca), ('logreg', logreg)])

    gscv_traditional = GridSearchCV(pipe, param_grid, cv=cv, scoring='accuracy', verbose=verbose)
    gscv_traditional.fit(x_data, y_data)

    assert gscv_traditional.best_params_ == gscv_baikal.best_params_
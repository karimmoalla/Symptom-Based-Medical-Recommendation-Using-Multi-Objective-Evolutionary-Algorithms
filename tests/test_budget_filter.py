import pandas as pd
from src.filtering import ProviderFilter


class DummyMapper:
    def __init__(self, mapping):
        self.mapping = mapping

    def get_id_by_name(self, name):
        return self.mapping.get(name)


def test_budget_filter_excludes_over_budget():
    df = pd.DataFrame([
        {'provider_id': 1, 'provider_name': 'A', 'specialty': 10, 'quality_score': 4.0, 'average_cost': 50},
        {'provider_id': 2, 'provider_name': 'B', 'specialty': 10, 'quality_score': 4.5, 'average_cost': 150},
        {'provider_id': 3, 'provider_name': 'C', 'specialty': 10, 'quality_score': 3.5, 'average_cost': 80},
    ])

    pf = ProviderFilter.__new__(ProviderFilter)
    pf.df_providers = df
    pf.mapper = DummyMapper({'Gastroenterologist': 10})

    # Apply budget filter of 100 -> B (150) should be excluded
    res = pf.filter_by_specialty_name('Gastroenterologist', top_n=10, budget=100, location=None)

    names = set(res['provider_name'])
    assert names == {'A', 'C'}
    assert res['average_cost'].max() <= 100

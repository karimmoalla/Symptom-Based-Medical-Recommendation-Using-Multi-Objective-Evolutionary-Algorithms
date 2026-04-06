import pandas as pd
from src.filtering import ProviderFilter


class DummyMapper:
    def __init__(self, mapping):
        self.mapping = mapping

    def get_id_by_name(self, name):
        return self.mapping.get(name)


def test_combined_score_ordering():
    # Prepare a small providers dataframe with known values
    df = pd.DataFrame([
        {'provider_id': 1, 'provider_name': 'Provider_A', 'specialty': 10, 'quality_score': 5.0, 'average_cost': 200, 'city': 'Paris'},
        {'provider_id': 2, 'provider_name': 'Provider_B', 'specialty': 10, 'quality_score': 4.0, 'average_cost': 50,  'city': 'Lyon'},
        {'provider_id': 3, 'provider_name': 'Provider_C', 'specialty': 10, 'quality_score': 3.0, 'average_cost': 30,  'city': 'Paris'},
    ])

    # Create ProviderFilter instance without running __init__ (avoid file IO)
    pf = ProviderFilter.__new__(ProviderFilter)
    pf.df_providers = df
    pf.mapper = DummyMapper({'Gastroenterologist': 10})

    # Use weights that will prefer proximity and cost for this dataset
    res = pf.filter_by_specialty_name('Gastroenterologist', top_n=10, budget=None, location='Paris',
                                     weight_quality=0.5, weight_cost=0.3, weight_proximity=0.2)

    # Expected ordering computed from actual combination: Provider_C (best), Provider_A, Provider_B
    names = list(res['provider_name'])
    assert names == ['Provider_C', 'Provider_A', 'Provider_B']

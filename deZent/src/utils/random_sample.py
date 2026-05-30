from scipy.stats import truncnorm  # type: ignore[import-untyped]
import numpy as np
from enum import StrEnum
from typing import cast

# strong typed version of https://stackoverflow.com/questions/36894191/how-to-get-a-normal-distribution-within-a-range-in-numpy
def sample_truncnorm(mean: float, sd: float, low: float, upp: float) -> float:
    sample: np.float64 = cast(np.float64, truncnorm((low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd).rvs()) # type: ignore
    return float(sample)

class DistributionType(StrEnum):
    UNIFROM = "uniform"
    NORMAL = "normal"
    POISSON = "poisson"

def sample_distribution_int(dist_type: DistributionType, low: int = 0, upp: int = 0):
    sample_f: float = 0
    match dist_type:
        case DistributionType.UNIFROM:
            sample_f = np.random.uniform(low,upp)
        case DistributionType.NORMAL:
            sample_f = sample_truncnorm(mean=upp / 2, sd=2, low=low, upp=upp)
        case DistributionType.POISSON:
            raise ValueError(f"DistributionType {dist_type} is inherently unbound!")
        case _:
            raise ValueError(f"DistributionType {dist_type} is invalid!")
    
    # round first, then cast -> just a cast would cause a down shift, never sampling upp (sample <= (upp - 1))
    return int(round(sample_f, 0))
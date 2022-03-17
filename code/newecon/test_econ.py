from math import pi
from references import u
from decimal import Decimal, getcontext
from definitions import (
    cylinder_volume,
    sphere_volume,
    cone_volume,
    square_pyramid_volume,
    triangular_prism_volume,
    truncated_cone_volume,
)

getcontext().prec = 6


def test_volumes():
    x = Decimal(1) * u.ft
    y = Decimal(1) * u.ft
    z = Decimal(1) * u.ft
    assert cylinder_volume(x, y) == Decimal(3.14159) * u.cuft
    assert sphere_volume(x) == Decimal(4.188) * u.cuft
    assert cone_volume(x, y) == Decimal(1.0472) * u.cuft
    assert triangular_prism_volume(x, y, z) == Decimal(0.5) * u.cuft
    assert square_pyramid_volume(x, y) == (Decimal(1) / Decimal(3)) * u.cuft
    assert truncated_cone_volume(x, y, z) == Decimal(1) / Decimal(3) * Decimal(pi) * 3

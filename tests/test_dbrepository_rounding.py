from app.data.DBrepository import round_calculated_product_cost


def test_round_calculated_product_cost_to_integer() -> None:
    assert round_calculated_product_cost(1234.56789) == 1235


def test_round_calculated_product_cost_uses_half_up_rule() -> None:
    assert round_calculated_product_cost(1234.5) == 1235

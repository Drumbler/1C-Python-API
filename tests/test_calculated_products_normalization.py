import pytest

from app.data.DBrepository import (
    prepare_calculated_product_parameters,
    build_calculated_product_parameters,
    normalize_calculated_product_parameters,
    normalize_calculated_product_series,
    round_calculated_product_cost,
)


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("  звн-01   премиум ", "ЗВН-01 ПРЕМИУМ"),
        ("ЗПВН-04/03", "ЗПВН-04/03"),
        ("  стеллаж   стпп  ", "СТЕЛЛАЖ СТПП"),
    ],
)
def test_normalize_calculated_product_series(source: str, expected: str) -> None:
    assert normalize_calculated_product_series(source) == expected


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("/ 1000 / 700 / 400 /", "1000/700/400"),
        ("1000/ 700 /400", "1000/700/400"),
        ("///1000/700/400///", "1000/700/400"),
    ],
)
def test_normalize_calculated_product_parameters(source: str, expected: str) -> None:
    assert normalize_calculated_product_parameters(source) == expected


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (1234, 1234),
        (1234.4, 1234),
        (1234.5, 1235),
        (1234.56789, 1235),
    ],
)
def test_round_calculated_product_cost(source: float | int, expected: int) -> None:
    assert round_calculated_product_cost(source) == expected


def test_build_calculated_product_parameters_for_zvn_standard_filters() -> None:
    assert build_calculated_product_parameters("ЗВН-01", "1000х700х400") == (
        "1000/700/400/н.ст.08/задн.ст.ОЦИНК/не.краш/"
        "ст.фильтры/врез.выт/-/без.подсв/вент.нет/сборн"
    )


def test_build_calculated_product_parameters_for_zpvn_premium_filters() -> None:
    assert build_calculated_product_parameters("зпвн-01 премиум", "1000x700x400") == (
        "1000/700/400/н.ст.08/задн.ст.НЕРЖ/не.краш/"
        "премиум.жир/врез.выт/-/врез.прит/-/без.подсв/вент.нет/сборн"
    )


def test_build_calculated_product_parameters_for_zvn_premium_filters() -> None:
    assert build_calculated_product_parameters("ЗВН-01 ПРЕМИУМ", "2000x1000x400") == (
        "2000/1000/400/н.ст.08/задн.ст.НЕРЖ/не.краш/"
        "премиум.жир/врез.выт/-/без.подсв/вент.нет/сборн"
    )


def test_build_calculated_product_parameters_for_island_zvn_without_backplate() -> None:
    assert build_calculated_product_parameters("ЗВН-04/03", "1000x1000x400") == (
        "1000/1000/400/н.ст.08/не.краш/"
        "ст.фильтры/врез.выт/-/без.подсв/вент.нет/сборн"
    )


def test_build_calculated_product_parameters_for_island_zpvn_premium_without_backplate() -> None:
    assert build_calculated_product_parameters(
        "ЗПВН-04/01 ПРЕМИУМ",
        "1400x1200x400",
    ) == (
        "1400/1200/400/н.ст.08/не.краш/"
        "премиум.жир/врез.выт/-/врез.прит/-/без.подсв/вент.нет/сборн"
    )


def test_build_calculated_product_parameters_rejects_unknown_size_format() -> None:
    with pytest.raises(ValueError, match="Unsupported characteristic format"):
        build_calculated_product_parameters("ЗВН-01", "1000 на 700 на 400")


def test_build_calculated_product_parameters_rejects_unsupported_series() -> None:
    with pytest.raises(ValueError, match="Unsupported zont series"):
        build_calculated_product_parameters("СПН", "1000x700x400")


def test_prepare_calculated_product_parameters_keeps_full_bath_characteristic() -> None:
    characteristic = (
        "1000/600/850/глуб.м.о(300мм)/RAL7024/борт.НЕТ/смес.НЕТ/-/"
        "ст.опоры/слив.ст/полка.НЕТ/сварн"
    )

    assert prepare_calculated_product_parameters("ВМЭ-1", characteristic) == characteristic


def test_prepare_calculated_product_parameters_still_expands_zont_size() -> None:
    assert prepare_calculated_product_parameters("ЗВН-01", "1000х700х400") == (
        "1000/700/400/н.ст.08/задн.ст.ОЦИНК/не.краш/"
        "ст.фильтры/врез.выт/-/без.подсв/вент.нет/сборн"
    )

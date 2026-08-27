import pytest

from app.modules.baths import new_vmx
from app.modules.shelvings import new_stpx
from app.utils.custom.shelf_class import ShelfType


def test_new_stpx_parse_parameters_converts_sizes_and_shelf_order() -> None:
    params = new_stpx.parse_parameters(
        "1000/600/1800/-/н.ст.08/-/3/СПР/усиление.нет/сварн./опора",
        "Стеллаж СтПП",
    )

    assert params.width == 1.0
    assert params.depth == 0.6
    assert params.height == 1.8
    assert params.shelfs_number == 3
    assert params.shelfs_order == [
        ShelfType.STANDART,
        ShelfType.PERFORATED,
        ShelfType.GRILLE,
    ]


def test_new_stpx_parse_parameters_rejects_wrong_parameter_count() -> None:
    with pytest.raises(ValueError, match="Expected 11 parameters"):
        new_stpx.parse_parameters("1000/600/1800", "Стеллаж СтПП")


def test_new_stpx_parse_parameters_rejects_non_integer_shelf_count() -> None:
    with pytest.raises(ValueError, match="Invalid shelfs_number"):
        new_stpx.parse_parameters(
            "1000/600/1800/-/н.ст.08/-/три/СПР/усиление.нет/сварн./опора",
            "Стеллаж СтПП",
        )


def test_new_stpx_parse_parameters_requires_shelf_order_length_to_match_count() -> None:
    with pytest.raises(ValueError, match="Shelfs order length must match shelfs number"):
        new_stpx.parse_parameters(
            "1000/600/1800/-/н.ст.08/-/3/СП/усиление.нет/сварн./опора",
            "Стеллаж СтПП",
        )


def test_new_stpx_parse_parameters_rejects_unknown_shelf_order_item() -> None:
    with pytest.raises(ValueError, match="Invalid shelfs_order item"):
        new_stpx.parse_parameters(
            "1000/600/1800/-/н.ст.08/-/1/X/усиление.нет/сварн./опора",
            "Стеллаж СтПП",
        )


def test_new_vmx_parse_parameters_extracts_core_bath_fields() -> None:
    params = new_vmx.parse_parameters(
        "1000/600/850/глуб.м.о.300/RAL9005/борт(50)/2смес/"
        "отверстие.ст/слив.ст/сварн/d100/полка.нет/-",
        "ВМН-2",
    )

    assert params.width == 1.0
    assert params.depth == 0.6
    assert params.height == 0.9
    assert params.series_letter == "Н"
    assert params.number_of_baths == 2
    assert params.height_bath == 0.3
    assert params.width_bath == 0.9
    assert params.depth_bath == pytest.approx(0.46)
    assert params.needed_color == "RAL9005"
    assert params.board_size == 0.05
    assert params.number_of_tap_hole == 2
    assert params.type_of_tap_hole == "отверстие.ст"
    assert params.type_of_drain_hole == "слив.ст"
    assert params.welded is True
    assert params.wheels == "d100"


def test_new_vmx_parse_parameters_handles_custom_color_and_onepiece_bath() -> None:
    params = new_vmx.parse_parameters(
        "1000/600/850/моеч.отд.500х400х300/RAL3020/полка.нет/-",
        "ВМС-1",
    )

    assert params.width_bath == 0.5
    assert params.depth_bath == 0.4
    assert params.height_bath == 0.3
    assert params.needed_color == "RALzakaz"
    assert params.need_onepiece_bath is True
    assert params.apron == new_vmx.MATERIAL_FOR_APRON


def test_new_vmx_parses_onepiece_bath_after_standard_depth() -> None:
    params = new_vmx.parse_parameters(
        "600/500/850/глуб.м.о(300мм)/-/моеч.отд.500х400х250/"
        "борт.НЕТ/смес.НЕТ/-/ст.опоры/слив.ст/полка.НЕТ/сварн",
        "ВМПц-1",
    )

    assert params.need_onepiece_bath is True
    assert params.width_bath == pytest.approx(0.5)
    assert params.depth_bath == pytest.approx(0.4)
    assert params.height_bath == pytest.approx(0.25)


def test_new_vmx_parse_parameters_requires_bath_depth_token() -> None:
    with pytest.raises(ValueError, match="Bath depth is required"):
        new_vmx.parse_parameters("1000/600/850/не.глубина", "ВМН-1")

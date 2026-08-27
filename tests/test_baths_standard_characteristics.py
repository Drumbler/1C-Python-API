from scripts.set_baths_standard_characteristics import build_characteristic


def test_builds_standard_assembled_bath_characteristic():
    assert build_characteristic("ВМБ-1", 1000, 600, 850) == (
        "1000/600/850/глуб.м.о(300мм)/-/борт.НЕТ/смес.НЕТ/-/"
        "ст.опоры/слив.ст/полка.НЕТ/сборн"
    )


def test_builds_standard_onepiece_bath_characteristic():
    assert build_characteristic(
        "ВМПц-1", 600, 500, 850, "500×400×250", "да"
    ) == (
        "600/500/850/глуб.м.о(300мм)/-/моеч.отд.500х400х250/"
        "борт.НЕТ/смес.НЕТ/-/ст.опоры/слив.ст/полка.НЕТ/сварн"
    )


def test_l_series_uses_n_series_assembly():
    assert build_characteristic("ВМЛ-1", 1000, 500, 850).endswith("/сборн")
    assert build_characteristic("ВМЛс-1", 1000, 500, 850).endswith("/сборн")
    assert build_characteristic(
        "ВМЛц-1", 500, 500, 850, "400х400х250"
    ).endswith("/сборн")


def test_e_series_uses_standard_ral_7024():
    assert build_characteristic("ВМЭ-1", 1000, 600, 850) == (
        "1000/600/850/глуб.м.о(300мм)/RAL7024/борт.НЕТ/смес.НЕТ/-/"
        "ст.опоры/слив.ст/полка.НЕТ/сварн"
    )


def test_e_onepiece_series_keeps_ral_before_compartment():
    assert build_characteristic(
        "ВМЭц-2", 1200, 600, 850, "500×400×250"
    ).startswith(
        "1200/600/850/глуб.м.о(300мм)/RAL7024/"
        "моеч.отд.500х400х250/"
    )

from pathlib import Path

import pandas as pd
import requests as rq

from app.controllers.calculation_controller import CalculationController


BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / 'ЗВН проверка стоимостей.xlsx'
OUTPUT_FILE = BASE_DIR / 'Output.xlsx'

file1 = pd.read_excel(INPUT_FILE)

test_dict: dict = {}
# url = 'http://192.168.24.180:5433/calculate'
url = 'http://127.0.0.1:8000/calculate'
calc_controller = CalculationController()


def _normalize_number(value: object) -> float | None:
    if pd.isna(value):
        return None
    if isinstance(value, str):
        normalized_value = value.replace(' ', '').replace(',', '.')
        if not normalized_value:
            return None
        return float(normalized_value)
    return float(value)


def _format_signed_difference(current: float, reference: object) -> tuple[str, str]:
    reference_value = _normalize_number(reference)
    if reference_value is None:
        return '', ''

    difference = current - reference_value
    sign = '+' if difference >= 0 else '-'
    absolute_difference = abs(difference)

    if reference_value == 0:
        percent_text = ''
    else:
        percent = absolute_difference / reference_value * 100
        percent_text = f'{sign}{percent:.2f}%'

    absolute_text = f'{sign}{absolute_difference:.2f}'
    return percent_text, absolute_text


def _request_cost_and_markup(series: str, parameters: str) -> tuple[float, float]:
    payload = {
        'series': series,
        'parameters': parameters,
    }
    print(payload)
    response = rq.post(url, json=payload)
    response.raise_for_status()

    calculated_cost = float(response.json()['cost'])
    calculation_details = calc_controller.get_calculation_details(series, parameters)
    if calculation_details.markup is None:
        raise ValueError(f'Module {series} does not provide markup')

    return calculated_cost, calculation_details.markup


def main() -> None:
    for idx, row in file1.iterrows():
        series = row['Серия']
        params = row['Параметры']
        calculated_cost, markup = _request_cost_and_markup(series, params)
        calculated_cost_price = calculated_cost / markup
        price_percent_diff, price_absolute_diff = _format_signed_difference(
            calculated_cost,
            row['Стоимость прайс'],
        )
        cost_price_percent_diff, cost_price_absolute_diff = _format_signed_difference(
            calculated_cost_price,
            row['С/С (Ольга)'],
        )

        file1.loc[idx, 'Стоимость считалочка'] = calculated_cost
        file1.loc[idx, 'Наценка, %'] = markup
        file1.loc[idx, 'С\С (Считалочка)'] = calculated_cost_price
        file1.loc[idx, 'Разница цены, %'] = price_percent_diff
        file1.loc[idx, 'Разница цены, абс.'] = price_absolute_diff
        file1.loc[idx, 'Разница с/с, %'] = cost_price_percent_diff
        file1.loc[idx, 'Разница с/с, абс.'] = cost_price_absolute_diff
        print(calculated_cost)
    file1.to_excel(OUTPUT_FILE, index=False)
    print(f'Saved to: {OUTPUT_FILE}')


if __name__ == "__main__":
    main()

    

# Стоимость считалочка(коэф)
# print( series)
#
# print(file1)

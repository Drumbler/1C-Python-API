def parse_parameters(parameters: str) -> dict[str, str]:
    '''
    парсинг параметров для тележки для гастроемкостей ТГ
    '''
    keys = {
        'width',
        'depth',
        'height',
        'number_of_guide-bars',
        'GN retainers',
        'tabletop_material',
        'wheels',
        'additional_options'
    }

    values = parameters.slpit('/')
    if len(keys) == len(values):
        return dict(zip(keys, values))
    else:
        raise ValueError(
            'Too many/not enough parameters. Hint: Check the input parameters in `parse_parameters()` or `calculate()` functions'
        )
    
def cost_calculation(parsed_params: dict[str, str], series: str) -> float:
    
    return

def calculate(parameters: str, series: str) -> float:
    parsed_params = parse_parameters(parameters)
    cost, markup = cost_calculation(parsed_params, series)
    return round(cost, 2), markup

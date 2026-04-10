from app.modules.material_collector import MaterialCollector


def parse_params(parameters: str) -> dict[str, any]:
    keys = [
        'width',
        'depth',
        'height',
        'bathtub_depth',
        'frame_ral',
        'border',
        'faucet_cutouts',
        'faucet_placement',
        'pillar_wheels',
        'additional_shelf'
    ]
    values = parameters.split('/')
    for i in values:
        try:
            values[values.index(i)] = int(i)
        except ValueError:
            continue
    return dict(zip(keys, values))


def cost_calculation(parsed_params: dict[str, any], series: str) -> float:
    MatCollector = MaterialCollector(series)
    total_cost = 0
    
    
    return total_cost

print(parse_params("1400/700/850/глуб.м.о.400мм/-/объемн.борт/смес.2шт/отверстие.ст/полка.НЕТ"))
from typing import Dict


def parse_params(parameters: str) -> Dict[str, str]:
    keys = [
        'width',
        'depth',
        'height'
    ]
    values = parameters.split('/')


def cost_calculation(series: str, parsed_params: Dict[str, str]) -> float:
    total_cost = 0
    width = float(parsed_params.get('width'))/1000
    depth = float(parsed_params.get('depth'))/1000
    height = float(parsed_params.get('height'))/1000

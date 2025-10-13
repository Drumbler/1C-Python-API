def split_to_float(inp_str: str, split_symbol: str) -> list[float]:
    return [float(i) for i in inp_str.split(split_symbol) if i]
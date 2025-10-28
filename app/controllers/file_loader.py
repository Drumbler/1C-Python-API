from app.data.DBrepository import dbrepo




def get_series_file(series: str) -> str:
    location = dbrepo.get_module_file_location(series)
    return location

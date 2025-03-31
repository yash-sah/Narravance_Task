import json

def get_data_from_source_a(start_year, end_year):
    with open("data/source_a.json") as f:
        data = json.load(f)
    return [
        row for row in data
        if start_year <= int(row["sale_date"].split("-")[0]) <= end_year
    ]

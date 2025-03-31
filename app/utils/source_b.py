import csv

def get_data_from_source_b(start_year, end_year, companies):
    with open("data/source_b.csv") as f:
        reader = csv.DictReader(f)
        return [
            row for row in reader
            if (
                start_year <= int(row["sale_date"].split("-")[0]) <= end_year and
                row["company"] in companies
            )
        ]

from pathlib import Path

import pandas as pd

from dslab.profiling import (
    generate_html_report,
    profile_csv,
    profile_dataframe,
)


def sample_dataframe():
    return pd.DataFrame(
        {
            "name": ["Asha", "Rahul", "Asha"],
            "age": [22, 25, 22],
            "city": ["Ahmedabad", None, "Ahmedabad"],
        }
    )


def test_profile_counts_rows_columns_missing_and_duplicates():
    profile = profile_dataframe(sample_dataframe())

    assert profile["row_count"] == 3
    assert profile["column_count"] == 3
    assert profile["missing_cells"] == 1
    assert profile["duplicate_rows"] == 1


def test_numeric_column_statistics():
    profile = profile_dataframe(sample_dataframe())
    age_profile = next(
        item for item in profile["column_profiles"] if item["name"] == "age"
    )

    assert age_profile["minimum"] == 22
    assert age_profile["maximum"] == 25
    assert age_profile["mean"] == 23
    assert age_profile["unique_count"] == 2


def test_missing_percentage():
    profile = profile_dataframe(sample_dataframe())
    city_profile = next(
        item for item in profile["column_profiles"] if item["name"] == "city"
    )

    assert city_profile["missing_count"] == 1
    assert city_profile["missing_pct"] == 33.33


def test_html_report_is_created(tmp_path: Path):
    output_path = tmp_path / "report.html"
    generate_html_report(profile_dataframe(sample_dataframe()), output_path)

    content = output_path.read_text(encoding="utf-8")
    assert "CSV Data Profile Report" in content
    assert "Ahmedabad" not in content
    assert "Missing cells" in content


def test_profile_csv_creates_report(tmp_path: Path):
    input_path = tmp_path / "sample.csv"
    output_path = tmp_path / "nested" / "report.html"
    sample_dataframe().to_csv(input_path, index=False)

    profile = profile_csv(input_path, output_path)

    assert profile["row_count"] == 3
    assert output_path.exists()

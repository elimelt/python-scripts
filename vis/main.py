import json
from datetime import datetime
from collections import defaultdict
import calendar
import matplotlib.pyplot as plt
import argparse


def convert_timestamp_to_month(timestamp):
    """Convert Unix timestamp to month-year string."""
    date = datetime.fromtimestamp(timestamp)
    return f"{calendar.month_abbr[date.month]} {date.year}"


def plot_job_listings(filename, output_path):
    with open(filename, "r") as file:
        data = json.load(file)

    monthly_counts = defaultdict(int)
    for listing in data:
        month = convert_timestamp_to_month(listing["date_posted"])
        monthly_counts[month] += 1

    months = sorted(monthly_counts.keys(), key=lambda x: datetime.strptime(x, "%b %Y"))
    counts = [monthly_counts[month] for month in months]

    plt.figure(figsize=(12, 6))
    plt.bar(months, counts)
    plt.title("Number of Job Postings by Month")
    plt.xlabel("Month")
    plt.ylabel("Number of Postings")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Plot job listings.")
    parser.add_argument(
        "-f",
        "--file",
        required=True,
        help="Path to the JSON file containing job listings",
    )
    parser.add_argument(
        "-o", "--output", required=True, help="Output path for the plot image"
    )
    args = parser.parse_args()

    plot_job_listings(args.file, args.output)


if __name__ == "__main__":
    main()

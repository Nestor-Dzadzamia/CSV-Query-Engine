import datetime

from csvquery import CSVData # type: ignore

# result = (
#     data
#     .filter("age >= 18 AND country == 'GE'")
#     .select("name", "age", "salary")
#     .sort("salary", descending=True)
#     .limit(100)
# )
# result.save("output/result.csv")

if __name__ == "__main__":
    print("Starting Schema Validation")
    start = datetime.datetime.now()
    data = CSVData("data/")
    end = datetime.datetime.now()
    print(f"Schema Validation Complete in {(end - start).total_seconds()} seconds")

    print("Query execution started")
    start = datetime.datetime.now()
    result = (
        data.select(
            "event_time",
            "event_type",
            "product_id",
            "category_id",
            "category_code",
            "brand",
            "price",
            "user_id",
            "user_session",
        )
        .filter("brand == samsung")
        .limit(10_000_000)
        .sort("price")
    )
    result.save("output.csv")
    end = datetime.datetime.now()
    print(f"Query execution completed in {(end - start).total_seconds()} seconds")
import logging
from csvquery import CSVData

# result = (
#     data
#     .filter("age >= 18 AND country == 'GE'")
#     .select("name", "age", "salary")
#     .sort("salary", descending=True)
#     .limit(100)
# )
# result.save("output/result.csv")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    data = CSVData("data/")
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
        .filter("(brand == 'samsung') and (price < 200)")
        .limit(100_000)
    )
    result.save("output.csv")
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
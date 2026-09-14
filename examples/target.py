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
    print(datetime.datetime.now())
    data = CSVData("data/")
    print(datetime.datetime.now())
from csvquery import CSVData

data = CSVData("data/")
result = (
    data
    .filter("age >= 18 AND country == 'GE'")
    .select("name", "age", "salary")
    .sort("salary", descending=True)
    .limit(100)
)
result.save("output/result.csv")

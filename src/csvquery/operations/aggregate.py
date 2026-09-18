import pandas as pd
from typing import Iterable


class GroupAggregator:


    def __init__(self, group_col: str, math_col: str, operation: str = "sum"):
        self.group_col = group_col
        self.math_col = math_col
        self.operation = operation.lower()

    def execute(self, chunks: Iterable[pd.DataFrame]) -> pd.DataFrame:

        aggregated_chunks = []

        for chunk in chunks:

            if self.group_col not in chunk.columns:
                raise ValueError(f"Missing column: Cannot group by '{self.group_col}'.")
            if self.math_col not in chunk.columns:
                raise ValueError(f"Missing column: Cannot aggregate '{self.math_col}'.")


            chunk[self.math_col] = pd.to_numeric(chunk[self.math_col], errors='coerce')


            if self.operation == "sum":
                chunk_result = chunk.groupby(self.group_col)[self.math_col].sum()
            elif self.operation == "count":
                chunk_result = chunk.groupby(self.group_col)[self.math_col].count()
            else:
                raise ValueError(f"Invalid operation: '{self.operation}' is not supported.")

            aggregated_chunks.append(chunk_result)


        if not aggregated_chunks:
            return pd.DataFrame()


        combined_results = pd.concat(aggregated_chunks)

        if self.operation in ["sum", "count"]:
            final_totals = combined_results.groupby(combined_results.index).sum().reset_index()



        final_totals = final_totals.sort_values(by=self.math_col, ascending=False)

        return final_totals



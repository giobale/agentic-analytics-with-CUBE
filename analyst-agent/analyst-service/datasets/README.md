# Test Datasets Directory

This directory is for storing CSV files to test the Data Analyst Agent.

## Usage

1. **Drop your CSV files here** for analysis
2. **Use relative paths** when calling the agent:
   ```python
   from src.analyst_agent import run_full_agent

   result = run_full_agent(
       user_query="Your analysis question here",
       dataset_path="datasets/your_file.csv"
   )
   ```

## File Requirements

- **Format**: CSV files (.csv extension)
- **Size**: Maximum 50MB (configurable in .env)
- **Encoding**: UTF-8 recommended
- **Headers**: First row should contain column names

## Example Usage

```python
# Example analysis of a sales dataset
result = run_full_agent(
    user_query="Analyze monthly sales trends and identify seasonal patterns",
    dataset_path="datasets/sales_data.csv"
)

print(result.analysis_report)
print("Metrics:", result.metrics)
print("Conclusion:", result.conclusion)
```

## Sample Queries

Try these types of analysis questions:

- **Trend Analysis**: "What are the sales trends over time?"
- **Statistical Summary**: "Provide descriptive statistics for all numeric columns"
- **Correlation Analysis**: "What variables are most correlated with revenue?"
- **Outlier Detection**: "Identify any outliers in the dataset"
- **Segmentation**: "Group customers by spending patterns"
- **Performance Analysis**: "Which products/regions perform best?"

## Tips

- **Be specific** in your queries for better results
- **Include context** about what the data represents
- **Ask follow-up questions** to dive deeper into findings
- **Request visualizations** when you want charts/graphs
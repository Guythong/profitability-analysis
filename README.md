# Profitability Analysis

This project analyzes profitability in the Sample Superstore dataset. The notebook explores which regions, categories, and sub-categories drive profit or loss, then tests whether limiting high discounts could improve total profit.

## Project Contents

- `notebooks/profitability_analysis.ipynb` - original Colab notebook.
- `src/profitability_analysis.py` - repeatable Python analysis script.
- `data/` - place the Superstore workbook here before running the project.
- `reports/` - generated charts and summary tables after running the script.

## Business Questions

1. Which region generates the highest profit?
2. Which product categories and sub-categories create losses?
3. How do discounts affect profitability for weak-performing products?
4. What profit lift is possible if discounts are capped?
5. How has profit changed by quarter?

## Key Findings

- The West region has the highest total profit at about `$108.4K`.
- The Central region is profitable overall, but Furniture is negative at about `-$2.9K`.
- The top loss-making sub-categories are `Tables`, `Bookcases`, `Supplies`, `Fasteners`, and `Machines`.
- Tables are the biggest concern. Table profit remains negative in the final quarters of the data, with the last quarter shown at about `-$4.5K`.
- A targeted discount cap of `20%` on `Tables` and `Bookcases` increases profit by about `$22.7K` in the notebook simulation.
- Applying the same cap across the full dataset increases profit by about `$87.5K`, but that broader action may also reduce competitiveness and should be tested carefully.

## Dataset

The notebook expects a file named:

```text
Sample - Superstore.xls
```

Place it here:

```text
data/Sample - Superstore.xls
```

The required columns include `Order Date`, `Region`, `Category`, `Sub-Category`, `Sales`, `Quantity`, `Discount`, `Profit`, and `Order ID`.

## Setup

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

On macOS or Linux, activate with:

```bash
source .venv/bin/activate
```

## Run the Analysis

```bash
python src/profitability_analysis.py --data "data/Sample - Superstore.xls"
```

Optional: change the discount cap used in the simulation.

```bash
python src/profitability_analysis.py --data "data/Sample - Superstore.xls" --discount-cap 0.20
```

Generated outputs are saved under `reports/`:

- `reports/tables/regional_profit.csv`
- `reports/tables/regional_category_profit.csv`
- `reports/tables/subcategory_profit.csv`
- `reports/tables/loss_by_region_subcategory.csv`
- `reports/tables/discount_analysis_problem_subcategories.csv`
- `reports/tables/profit_simulation_summary.csv`
- `reports/figures/*.png`

## Recommended Actions

- Review discount policy for `Tables` and `Bookcases`, especially where discounts exceed `20%`.
- Investigate Central-region Furniture losses, since the broader region is profitable but that category underperforms.
- Track quarterly profit for Tables separately because losses continue late in the observed period.
- Validate any discount cap with sales volume and customer impact before rolling it out broadly.

## Tools Used

- Python
- pandas
- matplotlib
- seaborn
- Jupyter Notebook / Google Colab

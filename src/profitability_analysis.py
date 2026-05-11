"""Profitability analysis for the Sample Superstore dataset.

This script converts the exploratory notebook into a repeatable command-line
workflow. It creates summary tables and charts for regional profit, category
performance, loss-driving sub-categories, quarterly trends, and discount caps.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


PROBLEM_SUBCATEGORIES = ["Tables", "Bookcases"]
DEFAULT_TOP_LOSERS = 5
DEFAULT_DISCOUNT_CAP = 0.20


def load_data(path: Path) -> pd.DataFrame:
    """Load the Superstore workbook and normalize date columns."""
    df = pd.read_excel(path)
    for column in ["Order Date", "Ship Date"]:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column])
    return df


def add_profit_status(df: pd.DataFrame, profit_column: str = "Profit") -> pd.DataFrame:
    result = df.copy()
    result["Profit Status"] = result[profit_column].apply(
        lambda value: "Profit" if value >= 0 else "Loss"
    )
    return result


def save_bar_chart(
    data: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    output_path: Path,
    hue: str | None = None,
    rotation: int = 0,
) -> None:
    plt.figure(figsize=(11, 6))
    sns.barplot(data=data, x=x, y=y, hue=hue)
    plt.title(title)
    plt.xlabel(x)
    plt.ylabel(y)
    plt.xticks(rotation=rotation, ha="right" if rotation else "center")
    plt.axhline(0, color="black", linewidth=0.8)
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()


def build_analysis(
    df: pd.DataFrame,
    output_dir: Path,
    discount_cap: float = DEFAULT_DISCOUNT_CAP,
    top_losers_count: int = DEFAULT_TOP_LOSERS,
) -> dict[str, pd.DataFrame | float | list[str]]:
    figures_dir = output_dir / "figures"
    tables_dir = output_dir / "tables"
    figures_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    regional_profit = add_profit_status(
        df.groupby("Region", as_index=False)["Profit"].sum()
    ).sort_values("Profit", ascending=False)
    regional_profit.to_csv(tables_dir / "regional_profit.csv", index=False)
    save_bar_chart(
        regional_profit,
        x="Region",
        y="Profit",
        hue="Profit Status",
        title="Profit by Region",
        output_path=figures_dir / "regional_profit.png",
    )

    regional_category_profit = add_profit_status(
        df.groupby(["Region", "Category"], as_index=False)["Profit"].sum()
    )
    regional_category_profit.to_csv(
        tables_dir / "regional_category_profit.csv", index=False
    )
    save_bar_chart(
        regional_category_profit,
        x="Region",
        y="Profit",
        hue="Category",
        title="Profit by Region and Category",
        output_path=figures_dir / "regional_category_profit.png",
    )

    subcategory_profit = add_profit_status(
        df.groupby(["Region", "Category", "Sub-Category"], as_index=False)[
            "Profit"
        ].sum()
    )
    subcategory_profit["Profit Rank in Region"] = subcategory_profit.groupby(
        "Region"
    )["Profit"].rank(method="first", ascending=False)
    subcategory_profit.to_csv(tables_dir / "subcategory_profit.csv", index=False)

    overall_subcategory_profit = (
        df.groupby("Sub-Category", as_index=False)["Profit"]
        .sum()
        .sort_values("Profit", ascending=True)
    )
    top_losers = (
        overall_subcategory_profit.head(top_losers_count)["Sub-Category"].tolist()
    )
    overall_subcategory_profit.to_csv(
        tables_dir / "overall_subcategory_profit.csv", index=False
    )
    save_bar_chart(
        overall_subcategory_profit,
        x="Sub-Category",
        y="Profit",
        title="Profit by Sub-Category",
        output_path=figures_dir / "subcategory_profit.png",
        rotation=45,
    )

    loser_df = df[df["Sub-Category"].isin(top_losers)].copy()
    loss_by_region_subcat = (
        loser_df.groupby(["Region", "Sub-Category"], as_index=False)
        .agg(
            Total_Profit=("Profit", "sum"),
            Total_Sales=("Sales", "sum"),
            Total_Quantity=("Quantity", "sum"),
            Order_Count=("Order ID", "nunique"),
        )
        .sort_values(["Region", "Total_Profit"])
    )
    loss_by_region_subcat.to_csv(
        tables_dir / "loss_by_region_subcategory.csv", index=False
    )

    loss_heatmap = loss_by_region_subcat.pivot(
        index="Region", columns="Sub-Category", values="Total_Profit"
    )
    plt.figure(figsize=(10, 6))
    sns.heatmap(loss_heatmap, annot=True, fmt=".0f", cmap="RdYlGn", center=0)
    plt.title("Profit/Loss for Top Loss-Making Sub-Categories")
    plt.tight_layout()
    plt.savefig(figures_dir / "loss_heatmap.png", dpi=160)
    plt.close()

    plt.figure(figsize=(11, 6))
    sns.scatterplot(
        data=loser_df,
        x="Discount",
        y="Profit",
        hue="Sub-Category",
        size="Sales",
        sizes=(20, 400),
        alpha=0.65,
    )
    plt.axhline(0, color="red", linestyle="--", linewidth=1)
    plt.title("Discount vs Profit for Top Loss-Making Sub-Categories")
    plt.tight_layout()
    plt.savefig(figures_dir / "discount_vs_profit_top_losers.png", dpi=160)
    plt.close()

    time_df = df.set_index("Order Date").sort_index()
    quarterly_profit = time_df["Profit"].resample("QE").sum()
    quarterly_loser_profit = (
        loser_df.set_index("Order Date").sort_index()["Profit"].resample("QE").sum()
    )
    quarterly_tables_profit = (
        df[df["Sub-Category"] == "Tables"]
        .set_index("Order Date")
        .sort_index()["Profit"]
        .resample("QE")
        .sum()
    )
    quarterly_trends = pd.DataFrame(
        {
            "Overall Profit": quarterly_profit,
            "Top Losers Profit": quarterly_loser_profit,
            "Tables Profit": quarterly_tables_profit,
        }
    )
    quarterly_trends.to_csv(tables_dir / "quarterly_profit_trends.csv")
    quarterly_trends.plot(figsize=(12, 6), marker="o")
    plt.axhline(0, color="black", linewidth=0.8)
    plt.title("Quarterly Profit Trends")
    plt.xlabel("Quarter")
    plt.ylabel("Profit")
    plt.tight_layout()
    plt.savefig(figures_dir / "quarterly_profit_trends.png", dpi=160)
    plt.close()

    simulation_df = df.copy()
    simulation_df["Cost"] = (
        simulation_df["Sales"] * (1 - simulation_df["Discount"])
        - simulation_df["Profit"]
    )
    simulation_df["Simulated_Discount"] = simulation_df["Discount"]
    problem_condition = (
        simulation_df["Sub-Category"].isin(PROBLEM_SUBCATEGORIES)
        & (simulation_df["Discount"] > discount_cap)
    )
    simulation_df.loc[problem_condition, "Simulated_Discount"] = discount_cap
    simulation_df["Simulated_Profit"] = (
        simulation_df["Sales"] * (1 - simulation_df["Simulated_Discount"])
        - simulation_df["Cost"]
    )
    current_profit = float(simulation_df["Profit"].sum())
    simulated_profit = float(simulation_df["Simulated_Profit"].sum())
    targeted_profit_lift = simulated_profit - current_profit

    simulation_df["Global_Capped_Discount"] = simulation_df["Discount"].clip(
        upper=discount_cap
    )
    simulation_df["Global_Capped_Profit"] = (
        simulation_df["Sales"] * (1 - simulation_df["Global_Capped_Discount"])
        - simulation_df["Cost"]
    )
    global_profit_lift = float(
        simulation_df["Global_Capped_Profit"].sum() - current_profit
    )

    discount_analysis = (
        df[df["Sub-Category"].isin(PROBLEM_SUBCATEGORIES)]
        .groupby(["Region", "Sub-Category", "Discount"], as_index=False)
        .agg(
            Total_Profit=("Profit", "sum"),
            Total_Sales=("Sales", "sum"),
            Total_Quantity=("Quantity", "sum"),
            Order_Count=("Order ID", "nunique"),
        )
    )
    discount_analysis["Profit_Margin_%"] = (
        discount_analysis["Total_Profit"] / discount_analysis["Total_Sales"] * 100
    )
    discount_analysis.to_csv(
        tables_dir / "discount_analysis_problem_subcategories.csv", index=False
    )

    summary = pd.DataFrame(
        [
            ["Current profit", current_profit],
            [
                f"Profit after capping {', '.join(PROBLEM_SUBCATEGORIES)} discounts at {discount_cap:.0%}",
                simulated_profit,
            ],
            ["Targeted profit lift", targeted_profit_lift],
            [f"Profit lift if all discounts are capped at {discount_cap:.0%}", global_profit_lift],
        ],
        columns=["Metric", "Value"],
    )
    summary.to_csv(tables_dir / "profit_simulation_summary.csv", index=False)

    return {
        "regional_profit": regional_profit,
        "regional_category_profit": regional_category_profit,
        "overall_subcategory_profit": overall_subcategory_profit,
        "top_losers": top_losers,
        "current_profit": current_profit,
        "targeted_profit_lift": targeted_profit_lift,
        "global_profit_lift": global_profit_lift,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Superstore profitability analysis.")
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("data") / "Sample - Superstore.xls",
        help="Path to the Sample Superstore .xls/.xlsx file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports"),
        help="Directory for generated tables and charts.",
    )
    parser.add_argument(
        "--discount-cap",
        type=float,
        default=DEFAULT_DISCOUNT_CAP,
        help="Maximum discount used in the profit simulation.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    df = load_data(args.data)
    results = build_analysis(df, args.output, discount_cap=args.discount_cap)

    print("Profitability analysis complete.")
    print(f"Rows analyzed: {len(df):,}")
    print(f"Top loss-making sub-categories: {', '.join(results['top_losers'])}")
    print(f"Current profit: ${results['current_profit']:,.2f}")
    print(f"Targeted discount-cap profit lift: ${results['targeted_profit_lift']:,.2f}")
    print(f"Global discount-cap profit lift: ${results['global_profit_lift']:,.2f}")
    print(f"Outputs saved to: {args.output.resolve()}")


if __name__ == "__main__":
    main()

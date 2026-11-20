
import numpy as np
import pandas as pd

from pipeline.config import FINAL_DIR


def load_movies():
    movies = pd.read_csv(FINAL_DIR / "movies.csv")

    for column in ["budget", "revenue", "release_year"]:
        movies[column] = pd.to_numeric(
            movies[column],
            errors="coerce"
        )

    # Calculate the revenue-to-budget multiple.
    # A missing revenue or zero budget must not produce a multiple.
    valid = (
        movies["revenue"].notna()
        & movies["budget"].notna()
        & (movies["budget"] > 0)
    )

    movies["revenue_budget_multiple"] = np.nan

    movies.loc[valid, "revenue_budget_multiple"] = (
        movies.loc[valid, "revenue"].to_numpy(dtype=float)
        / movies.loc[valid, "budget"].to_numpy(dtype=float)
    )

    return movies


def get_periods(movies):
    return {
        "All years": movies,
        "2000 onward": movies[
            movies["release_year"] >= 2000
        ]
    }


def compare_licensing_types(movies):
    results = []

    for period_name, period_data in get_periods(movies).items():

        for licensing_type in ["franchise", "standalone"]:

            group = period_data[
                period_data["licensing_type"] == licensing_type
            ]

            revenue = group["revenue"].dropna().to_numpy(dtype=float)
            budget = group["budget"].dropna().to_numpy(dtype=float)
            multiples = (
                group["revenue_budget_multiple"]
                .dropna()
                .to_numpy(dtype=float)
            )

            results.append({
                "period": period_name,
                "licensing_type": licensing_type,
                "title_count": len(group),
                "known_revenue": len(revenue),
                "known_budget": len(budget),
                "zero_revenue": int((group["revenue"] == 0).sum()),
                "average_revenue": (
                    np.mean(revenue) if len(revenue) else np.nan
                ),
                "median_revenue": (
                    np.median(revenue) if len(revenue) else np.nan
                ),
                "average_budget": (
                    np.mean(budget) if len(budget) else np.nan
                ),
                "median_budget": (
                    np.median(budget) if len(budget) else np.nan
                ),
                "valid_multiples": len(multiples),
                "median_multiple": (
                    np.median(multiples) if len(multiples) else np.nan
                ),
                "25th_percentile": (
                    np.percentile(multiples, 25)
                    if len(multiples) else np.nan
                ),
                "75th_percentile": (
                    np.percentile(multiples, 75)
                    if len(multiples) else np.nan
                )
            })

    return pd.DataFrame(results)


def analyse_collections(movies):
    results = []

    for period_name, period_data in get_periods(movies).items():

        franchises = period_data[
            period_data["collection_id"].notna()
        ]

        if franchises.empty:
            continue

        collection_summary = (
            franchises.groupby(
                ["collection_id", "collection_name"],
                as_index=False
            )
            .agg(
                title_count=("tmdb_id", "nunique"),
                titles=("title", lambda values: " | ".join(values)),
                total_reported_budget=(
                    "budget",
                    lambda values: values.sum(min_count=1)
                ),
                total_reported_revenue=(
                    "revenue",
                    lambda values: values.sum(min_count=1)
                ),
                median_title_multiple=(
                    "revenue_budget_multiple",
                    "median"
                ),
                titles_with_valid_multiple=(
                    "revenue_budget_multiple",
                    "count"
                )
            )
        )

        collection_summary.insert(0, "period", period_name)
        results.append(collection_summary)

    if results:
        return pd.concat(results, ignore_index=True)

    return pd.DataFrame()


def rank_titles(movies):
    results = []

    for period_name, period_data in get_periods(movies).items():

        valid_titles = period_data[
            period_data["revenue_budget_multiple"].notna()
        ].copy()

        valid_titles.insert(0, "period", period_name)

        results.append(
            valid_titles[
                [
                    "period",
                    "tmdb_id",
                    "title",
                    "release_year",
                    "licensing_type",
                    "collection_name",
                    "budget",
                    "revenue",
                    "revenue_budget_multiple"
                ]
            ]
        )

    return (
        pd.concat(results, ignore_index=True)
        .sort_values(
            ["period", "licensing_type", "revenue_budget_multiple"],
            ascending=[True, True, False]
        )
    )


def main():
    movies = load_movies()

    print("\nSTREAMVAULT LICENSING ANALYSIS")
    print("Movies analysed:", len(movies))

    print(
        "Movies without release year:",
        movies["release_year"].isna().sum()
    )

    print(
        "Movies without revenue:",
        movies["revenue"].isna().sum()
    )

    print(
        "Movies without budget:",
        movies["budget"].isna().sum()
    )

    print(
        "Movies with zero recorded revenue:",
        (movies["revenue"] == 0).sum()
    )

    # 1. Compare franchise and standalone financial performance.
    comparison = compare_licensing_types(movies)

    print("\nFRANCHISE VERSUS STANDALONE")

    print(
        comparison.to_string(
            index=False,
            float_format=lambda value: f"{value:,.2f}"
        )
    )

    comparison.to_csv(
        FINAL_DIR / "licensing_summary.csv",
        index=False
    )

    # 2. Compare individual franchise collections.
    collections = analyse_collections(movies)

    print("\nFRANCHISE COLLECTIONS")

    if not collections.empty:
        print(
            collections.sort_values(
                ["period", "title_count"],
                ascending=[True, False]
            ).to_string(index=False)
        )

        six_title_collections = collections[
            collections["title_count"] == 6
        ]

        print("\nCOLLECTIONS WITH SIX CANDIDATE TITLES")

        if six_title_collections.empty:
            print("No six-title collection found.")
        else:
            print(six_title_collections.to_string(index=False))

        collections.to_csv(
            FINAL_DIR / "collection_summary.csv",
            index=False
        )

        six_title_collections.to_csv(
            FINAL_DIR / "six_title_collections.csv",
            index=False
        )

    # 3. Rank individual titles for both periods.
    rankings = rank_titles(movies)

    print("\nINDIVIDUAL TITLE RANKINGS")

    print(
        rankings.to_string(
            index=False,
            float_format=lambda value: f"{value:,.2f}"
        )
    )

    rankings.to_csv(
        FINAL_DIR / "title_rankings.csv",
        index=False
    )

    # Audience ratings and licensing prices are not present
    # in the current transformed movies.csv.
    print("\nDATA LIMITATIONS")
    print("Audience rating measures: not available in movies.csv.")
    print("Licensing asking prices: not available in movies.csv.")
    print(
        "Revenue-to-budget multiples are not profit "
        "or licensing returns."
    )

    print("\nANALYSIS COMPLETED")
    print("Results saved in:", FINAL_DIR)


if __name__ == "__main__":
    main()

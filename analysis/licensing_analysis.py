import numpy as np
import pandas as pd

from pipeline.config import FINAL_DIR


def load_movies():
    """Load the final movie dataset and prepare numeric columns."""

    movies = pd.read_csv(FINAL_DIR / "movies.csv")

    numeric_columns = ["budget", "revenue", "release_year"]

    for column in numeric_columns:
        movies[column] = pd.to_numeric(
            movies[column],
            errors="coerce"
        )

    # Calculate revenue-to-budget multiple only where both values are valid.
    valid_budget = (
        movies["budget"].notna()
        & (movies["budget"] > 0)
    )

    valid_revenue = movies["revenue"].notna()

    movies["revenue_budget_multiple"] = np.nan

    valid_rows = valid_budget & valid_revenue

    movies.loc[valid_rows, "revenue_budget_multiple"] = (
        movies.loc[valid_rows, "revenue"]
        / movies.loc[valid_rows, "budget"]
    )

    return movies


def get_periods(movies):
    """Separate all films from films released in 2000 onward."""

    return {
        "All years": movies.copy(),
        "2000 onward": movies[
            movies["release_year"] >= 2000
        ].copy()
    }


def compare_licensing_types(periods):
    """Compare franchise and standalone film performance."""

    results = []

    for period_name, data in periods.items():

        summary = (
            data.groupby("licensing_type")
            .agg(
                title_count=("tmdb_id", "nunique"),
                known_revenue=("revenue", "count"),
                known_budget=("budget", "count"),
                zero_revenue_count=(
                    "revenue",
                    lambda x: (x == 0).sum()
                ),
                valid_multiple_count=(
                    "revenue_budget_multiple",
                    "count"
                ),
                median_revenue=("revenue", "median"),
                median_budget=("budget", "median"),
                mean_revenue=("revenue", "mean"),
                mean_budget=("budget", "mean"),
                median_multiple=(
                    "revenue_budget_multiple",
                    "median"
                ),
                multiple_25th_percentile=(
                    "revenue_budget_multiple",
                    lambda x: x.quantile(0.25)
                ),
                multiple_75th_percentile=(
                    "revenue_budget_multiple",
                    lambda x: x.quantile(0.75)
                )
            )
            .reset_index()
        )

        summary.insert(0, "period", period_name)
        results.append(summary)

    if not results:
        return pd.DataFrame()

    final_summary = pd.concat(
        results,
        ignore_index=True
    )

    print("\nFRANCHISE VS STANDALONE PERFORMANCE")
    print(final_summary.to_string(index=False))

    return final_summary


def analyse_collections(periods):
    """Summarise franchise collections in each period."""

    results = []

    for period_name, data in periods.items():

        franchises = data[
            (data["licensing_type"] == "franchise")
            & data["collection_id"].notna()
        ].copy()

        collection_summary = (
            franchises.groupby(
                ["collection_id", "collection_name"],
                dropna=False
            )
            .agg(
                candidate_title_count=("tmdb_id", "nunique"),
                candidate_titles=(
                    "title",
                    lambda x: ", ".join(
                        sorted(x.dropna().unique())
                    )
                ),
                total_reported_revenue=(
                    "revenue",
                    lambda x: x.sum(min_count=1)
                ),
                total_reported_budget=(
                    "budget",
                    lambda x: x.sum(min_count=1)
                ),
                median_title_multiple=(
                    "revenue_budget_multiple",
                    "median"
                ),
                valid_multiple_count=(
                    "revenue_budget_multiple",
                    "count"
                )
            )
            .reset_index()
            .sort_values(
                ["median_title_multiple", "candidate_title_count"],
                ascending=[False, False],
                na_position="last"
            )
        )

        collection_summary.insert(0, "period", period_name)
        results.append(collection_summary)

    if results:
        final_collections = pd.concat(
            results,
            ignore_index=True
        )
    else:
        final_collections = pd.DataFrame()

    print("\nFRANCHISE COLLECTION ANALYSIS")
    print(final_collections.to_string(index=False))

    if not final_collections.empty:
        six_title_collections = final_collections[
            final_collections["candidate_title_count"] == 6
        ].copy()
    else:
        six_title_collections = pd.DataFrame()

    print("\nCOLLECTIONS WITH SIX CANDIDATE TITLES")

    if six_title_collections.empty:
        print("No collections with exactly six candidate titles.")
    else:
        print(six_title_collections.to_string(index=False))

    return final_collections, six_title_collections


def rank_titles(periods):
    """Rank individual films by revenue-to-budget multiple."""

    results = []

    for period_name, data in periods.items():

        rankings = data[
            data["revenue_budget_multiple"].notna()
        ].copy()

        rankings = rankings.sort_values(
            "revenue_budget_multiple",
            ascending=False
        )

        rankings.insert(0, "period", period_name)

        rankings = rankings[
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

        results.append(rankings)

    if results:
        final_rankings = pd.concat(
            results,
            ignore_index=True
        )
    else:
        final_rankings = pd.DataFrame()

    print("\nTOP INDIVIDUAL FILMS")

    for period_name in periods:
        print(f"\n{period_name}")

        period_rankings = final_rankings[
            final_rankings["period"] == period_name
        ]

        print(period_rankings.head(20).to_string(index=False))

    return final_rankings


def analyse_cast_and_crew():
    """Analyse the first five billed cast members and film directors."""

    cast = pd.read_csv(FINAL_DIR / "movie_cast.csv")
    crew = pd.read_csv(FINAL_DIR / "movie_crew.csv")

    # Lead actors: first five billed cast members in each film.
    cast["cast_order"] = pd.to_numeric(
        cast["cast_order"],
        errors="coerce"
    )

    lead_cast = cast[
        cast["cast_order"].between(0, 4)
    ].copy()

    actor_summary = (
        lead_cast.groupby(
            ["person_id", "person_name"]
        )
        .agg(
            film_count=("tmdb_id", "nunique"),
            roles=(
                "character",
                lambda x: ", ".join(
                    x.dropna().unique()[:5]
                )
            )
        )
        .reset_index()
        .sort_values(
            ["film_count", "person_name"],
            ascending=[False, True]
        )
    )

    print("\nTOP LEAD ACTORS")
    print(actor_summary.head(20).to_string(index=False))

    actor_summary.head(20).to_csv(
        FINAL_DIR / "top_lead_actor_summary.csv",
        index=False
    )

    # Directors.
    directors = crew[
        crew["job"].astype(str).str.strip().str.lower()
        == "director"
    ].copy()

    director_summary = (
        directors.groupby(
            ["person_id", "person_name"]
        )
        .agg(
            film_count=("tmdb_id", "nunique")
        )
        .reset_index()
        .sort_values(
            ["film_count", "person_name"],
            ascending=[False, True]
        )
    )

    print("\nTOP DIRECTORS")
    print(director_summary.head(20).to_string(index=False))

    director_summary.head(20).to_csv(
        FINAL_DIR / "top_director_summary.csv",
        index=False
    )

    return actor_summary, director_summary


def main():

    FINAL_DIR.mkdir(parents=True, exist_ok=True)

    print("STREAMVAULT LICENSING ANALYSIS")

    movies = load_movies()

    print(f"\nMOVIES ANALYSED: {movies['tmdb_id'].nunique()}")

    print("\nDATA DIAGNOSTICS")
    print(
        "Missing release years:",
        movies["release_year"].isna().sum()
    )
    print(
        "Missing revenue values:",
        movies["revenue"].isna().sum()
    )
    print(
        "Missing budget values:",
        movies["budget"].isna().sum()
    )
    print(
        "Zero recorded revenue:",
        (movies["revenue"] == 0).sum()
    )

    periods = get_periods(movies)

    # Franchise versus standalone comparison.
    licensing_summary = compare_licensing_types(periods)

    licensing_summary.to_csv(
        FINAL_DIR / "licensing_summary.csv",
        index=False
    )

    # Franchise collection analysis.
    collection_summary, six_title_collections = (
        analyse_collections(periods)
    )

    collection_summary.to_csv(
        FINAL_DIR / "collection_summary.csv",
        index=False
    )

    six_title_collections.to_csv(
        FINAL_DIR / "six_title_collections.csv",
        index=False
    )

    # Individual film rankings.
    title_rankings = rank_titles(periods)

    title_rankings.to_csv(
        FINAL_DIR / "title_rankings.csv",
        index=False
    )

    # Lead actors and directors.
    analyse_cast_and_crew()

    print("\nIMPORTANT LIMITATIONS")
    print(
        "Revenue divided by production budget is not profit "
        "or licensing return."
    )
    print(
        "Licensing prices, marketing costs and distribution "
        "costs are not available."
    )
    print(
        "Historical revenue figures have not been adjusted "
        "for inflation."
    )
    print(
        "Collection results cover candidate films in this "
        "dataset, not necessarily every film in a complete bundle."
    )
    print(
        "Cast billing order is used as a practical indicator "
        "of lead actors."
    )
    print(
        "Repeated actors and directors do not prove audience "
        "demand or future financial performance."
    )

    print("\nANALYSIS COMPLETE")
    print(f"Results saved in: {FINAL_DIR}")


if __name__ == "__main__":
    main()
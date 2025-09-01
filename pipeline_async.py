# pipeline_async.py
import os
import asyncio
from concurrent.futures import ProcessPoolExecutor
from typing import Optional

import pandas as pd
from sqlalchemy import create_engine, types
from dotenv import load_dotenv

from coca_fetchers import CocaColaFetcher

import plotly.graph_objects as go


# ====== Funkcje wykonywane w procesach (MUSZĄ być na top-level, żeby były picklowalne) ======

def _get_db_url_from_env() -> str:
    """Zwraca DATABASE_URL albo buduje go ze zmiennych PG*."""
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return db_url

    host = os.getenv("PGHOST", "localhost")
    port = os.getenv("PGPORT", "5432")
    user = os.getenv("PGUSER", "postgres")
    password = os.getenv("PGPASSWORD", "")
    dbname = os.getenv("PGDATABASE", "postgres")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"


def save_to_database(stock_df: pd.DataFrame, table_name: str = "ko_adj_close"):
    """
    Zapisuje DataFrame (index=daty, kolumna 'adj_close') do PostgreSQL.
    Nadpisuje tabelę dla powtarzalności demo.
    """
    db_url = _get_db_url_from_env()
    engine = create_engine(db_url)

    # Upewnij się, że mamy kolumnę 'date' (a nie index)
    df = stock_df.copy().sort_index()
    df = df.reset_index().rename(columns={"index": "date"})
    # konwersja do typów SQL-friendly
    df["date"] = pd.to_datetime(df["date"]).dt.date  # Date bez czasu

    with engine.begin() as conn:
        df.to_sql(
            table_name,
            conn,
            if_exists="replace",     # w realnym use-case: "append"
            index=False,
            dtype={
                "date": types.Date(),
                "adj_close": types.Numeric(18, 6)
            }
        )
    return f"Saved {len(df)} rows into table '{table_name}'"


def save_to_textfile(desc_text: str, path: str = "company_description.txt"):
    with open(path, "w", encoding="utf-8") as f:
        f.write(desc_text or "")
    return f"Saved company description to {path}"


def build_plot_html(stock_df: pd.DataFrame, logo_path: Optional[str], out_html: str = "ko_report.html"):
    """
    Tworzy wykres (Plotly) z adj_close i zapisuje HTML.
    Obok wykresu osadza logo (jeśli podano).
    """
    df = stock_df.copy().sort_index()
    fig = go.Figure([
        go.Scatter(
            x=df.index,
            y=df["adj_close"],
            mode="lines",
            name="KO Adjusted Close"
        )
    ])
    fig.update_layout(
        title="Coca-Cola (KO) – Adjusted Close (ostatnie 5 lat)",
        xaxis_title="Data",
        yaxis_title="Cena (USD, adjusted)",
        template="plotly_white",
        margin=dict(l=40, r=40, t=60, b=40),
        height=500
    )

    fig_html = fig.to_html(include_plotlyjs="cdn", full_html=False)

    # Prosty layout 2-kolumnowy (flex)
    logo_html = ""
    if logo_path and os.path.exists(logo_path):
        logo_html = f'<img src="{logo_path}" alt="Coca-Cola logo" style="max-width:100%;height:auto;border:0;" />'
    else:
        logo_html = "<p><em>Logo not available.</em></p>"

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>KO Report</title>
<style>
  body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, 'Helvetica Neue', Arial, sans-serif; }}
  .container {{
    display: flex;
    gap: 24px;
    align-items: flex-start;
  }}
  .chart {{ flex: 3; min-width: 0; }}
  .logo  {{ flex: 1; max-width: 320px; }}
  .logo img {{ width: 100%; height: auto; }}
</style>
</head>
<body>
  <h1>Coca-Cola (KO) – Report</h1>
  <div class="container">
    <div class="chart">{fig_html}</div>
    <div class="logo">{logo_html}</div>
  </div>
</body>
</html>
"""
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html)
    return f"Plot + logo saved to {out_html}"


# ================== ASYNC PIPELINE ==================

async def main_async():
    load_dotenv()

    # 1) pobierz dane (trzy wątki pod spodem)
    fetcher = CocaColaFetcher()
    data = fetcher.fetch_all()

    # walidacja minimalna
    if "company_desc" not in data or "stock_data" not in data:
        raise RuntimeError(f"Brak wymaganych danych. Otrzymano klucze: {list(data.keys())}")

    # 2) uruchom 3 procesy
    loop = asyncio.get_running_loop()
    with ProcessPoolExecutor(max_workers=3) as pool:
        futures = [
            loop.run_in_executor(pool, save_to_textfile, data["company_desc"]),
            loop.run_in_executor(pool, save_to_database, data["stock_data"]),
            loop.run_in_executor(pool, build_plot_html, data["stock_data"], data.get("logo_path"))
        ]
        results = await asyncio.gather(*futures, return_exceptions=True)

    print("\n=== Wyniki zadań (procesy) ===")
    for i, res in enumerate(results, 1):
        if isinstance(res, Exception):
            print(f"Task {i}: ERROR -> {type(res).__name__}: {res}")
        else:
            print(f"Task {i}: {res}")

    print("\nGotowe ✅")


if __name__ == "__main__":
    asyncio.run(main_async())

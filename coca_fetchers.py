# coca_fetchers.py
import os
import threading
from queue import Queue
from typing import Dict, Any, Optional

from dotenv import load_dotenv
load_dotenv()

from fetch_info import fetch_company_info          # -> (company_desc, tagline)
from fetch_logo import fetch_coca_cola_logo        # -> image_filename (str or None)
from fetch_price import fetch_coca_cola_timeseries # -> DataFrame (adj_close)


class CocaColaFetcher:
    """Orkiestruje równoległe pobranie: opisu firmy, logo i szeregu czasowego KO."""
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ALPHAVANTAGE_API_KEY")
        if not self.api_key:
            raise ValueError("Brak ALPHAVANTAGE_API_KEY (ustaw w .env lub środowisku).")

    def _worker_company(self, q: Queue):
        try:
            company_desc, tagline = fetch_company_info()
            q.put({"company_desc": company_desc, "tagline": tagline})
        except Exception as e:
            q.put({"company_error": f"{type(e).__name__}: {e}"})

    def _worker_logo(self, q: Queue):
        try:
            logo_path = fetch_coca_cola_logo()
            q.put({"logo_path": logo_path})
        except Exception as e:
            q.put({"logo_error": f"{type(e).__name__}: {e}"})

    def _worker_price(self, q: Queue):
        try:
            df = fetch_coca_cola_timeseries(self.api_key)  # DataFrame z kol. 'adj_close' i datą w indexie
            q.put({"stock_data": df})
        except Exception as e:
            q.put({"stock_error": f"{type(e).__name__}: {e}"})

    def fetch_all(self) -> Dict[str, Any]:
        """Uruchamia 3 wątki i zwraca słownik z danymi lub błędami."""
        results: Queue = Queue()

        t_company = threading.Thread(target=self._worker_company, args=(results,), name="company-thread", daemon=True)
        t_logo    = threading.Thread(target=self._worker_logo,    args=(results,), name="logo-thread",    daemon=True)
        t_price   = threading.Thread(target=self._worker_price,   args=(results,), name="price-thread",   daemon=True)

        for t in (t_company, t_logo, t_price):
            t.start()
        for t in (t_company, t_logo, t_price):
            t.join()

        data: Dict[str, Any] = {}
        while not results.empty():
            data.update(results.get())
        return data


# (opcjonalnie) prosty entrypoint do szybkiego testu modułu
#if __name__ == "__main__":
    #fetcher = CocaColaFetcher()
    #out = fetcher.fetch_all()
    #print("== WYNIK ==")
    #for k, v in out.items():
        #if k == "stock_data":
            #print(k, "shape=", getattr(v, "shape", None))
            #try:
                #print(v.head())
            #except Exception:
                #pass
        #else:
            #print(k, (str(v)[:200] + ("..." if len(str(v)) > 200 else "")))

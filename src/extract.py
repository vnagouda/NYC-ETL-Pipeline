import os
import requests
from . import settings

def download_raw() -> str:
    os.makedirs("data/raw", exist_ok=True)
    url = settings.CSV_URL
    out_path = settings.LOCAL_RAW  # it's parquet despite the var name
    print(f"Downloading {url} -> {out_path}")

    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    return out_path

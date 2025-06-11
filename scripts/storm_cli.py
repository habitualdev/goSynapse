import json
import os
import logging
from pathlib import Path
from dataclasses import asdict
import sys

# Ensure the local gosynapse package is importable when running the script
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if SRC_PATH.exists() and str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from dotenv import load_dotenv, find_dotenv
import gosynapse

from gosynapse.client import SynapseClient


def main() -> None:
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("urllib3").setLevel(logging.DEBUG)
    logging.debug("Using gosynapse from %s", gosynapse.__file__)
    load_dotenv(find_dotenv(usecwd=True))
    host = os.environ.get("SYNAPSE_HOST", "").strip()
    port = os.environ.get("SYNAPSE_PORT", "").strip()
    api_key = os.environ.get("SYNAPSE_API_KEY", "").strip()
    view = os.environ.get("SYNAPSE_VIEW_ID")

    if not host or not port:
        raise SystemExit("SYNAPSE_HOST and SYNAPSE_PORT must be defined in .env")

    client = SynapseClient(host=host, port=port, api_key=api_key)
    output_file = Path("storm_results.json")

    while True:
        query = input("storm> ").strip()
        if not query or query.lower() in {"quit", "exit"}:
            break
        opts = {"view": view} if view else None
        try:
            init, nodes, fini, prints = client.storm(query, opts=opts)
        except Exception as exc:  # requests.HTTPError or connection errors
            logging.error("Storm query failed: %s", exc)
            continue
        result = {
            "init": [asdict(i) for i in init],
            "nodes": [asdict(n) for n in nodes],
            "fini": [asdict(f) for f in fini],
            "print": [asdict(p) for p in prints],
        }
        with output_file.open("a", encoding="utf-8") as f:
            json.dump(result, f)
            f.write("\n")
        logging.debug("Wrote results to %s", output_file)


if __name__ == "__main__":
    main()

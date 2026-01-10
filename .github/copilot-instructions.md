<!-- Auto-generated guidance for AI coding agents working on this repository. Update as needed. -->

# Copilot instructions for neotaste_scraper

Summary
- Small CLI tool to scrape NeoTaste restaurant pages, extract deal badges, and export results (JSON/HTML/text).

Key files
- `main.py`: CLI entry — flags: `--city`, `--all`, `--events` (legacy), `--flash`, `--special`, `--json`, `--html`, `--lang`.
- `neotaste_scraper/neotaste_scraper.py`: core scraper and parsing logic. Returns `List[Dict]` per city: {restaurant, deals[], link}.
- `neotaste_scraper/data_output.py`: JSON/HTML/text output, uses Jinja2 template `templates/deals_template.html`.
- `tests/`: unit tests and HTML fixtures under `tests/html_snippets/` — tests mock `requests.get`.
- `.github/workflows/`: CI workflows (export, pylint, pages deployment). `scripts/verify_json.py` used in CI to check outputs.

Big picture & data flow
- `main.py` orchestrates: calls `fetch_all_cities()` or `fetch_deals_from_city()` (in `neotaste_scraper`) → aggregate per-city dict → format via `data_output`.
- Scraper uses `requests` + `BeautifulSoup` and relies on `data-sentry-component` attributes in the HTML to locate deal badges (selectors like `[data-sentry-component$="DealPreview"]`).
- Output format is a dict keyed by city slug with lists of restaurant dicts: {"restaurant": str, "deals": [str], "link": str}.

Parsing patterns & heuristics
- Deal elements: look for elements inside `[data-sentry-component="RestaurantCardDeals"]` whose `data-sentry-component` ends with `DealPreview`.
- Flash detection: check component name / inner HTML for `flashdeal`, presence of bolt icon (`bolt` string), or emoji/marker like `⚡`.
- Event detection: check for `eventdeal` in component/html or star emoji `🌟`.
- New code uses a `Deal` dataclass and a `deal_type` (`flash`, `event`, `flash+event`, `other`) — prefer that when classifying.

Testing & workflows
- Run unit tests with `pytest`. Tests mock HTTP via `unittest.mock.patch('requests.get')` and load fixtures from `tests/html_snippets/`.
- CI exports site files via `.github/workflows/github-pages.yml` which runs `python main.py --all --lang <lang> --special --html output/<lang>/special-only.html --json output/<lang>/special-only.json`.
- Linting via `pylint` in `.github/workflows/pylint.yml` — keep functions small (avoid too-many-branches). Use type hints and small helper functions.

Developer patterns & conventions
- Prefer explicit typing and small helper functions in scraper to keep Pylint happy.
- Tests assert exact strings from fixtures; when changing parsing, update tests and fixtures accordingly.
- Templates live in `templates/` and are rendered via Jinja2 in `data_output.py`.

Common tasks (commands)
```bash
pip install -r requirements.txt
python -m pytest -q
python main.py --all --lang de --special --html output/de/special-only.html --json output/de/special-only.json
python scripts/verify_json.py output/de/special-only.json
pylint $(git ls-files '*.py')
```

Do / Don't
- Do: Update `tests/html_snippets/` when you change parsing rules. Update `README.md` and `.github/workflows/github-pages.yml` when changing CLI flags.
- Don't: change the output dict shape without updating `data_output.py` and tests.

If you modify parsing logic
- Add or update an HTML fixture in `tests/html_snippets/` that demonstrates the HTML pattern.
- Add a focused unit test in `tests/test_neotaste_scraper.py` (examples exist) that asserts the exact deals extracted.

Questions for maintainers
- Which deal badges beyond `DealPreview`/`FlashDealPreview` should be considered special in future? Add examples to fixtures.

-- End --

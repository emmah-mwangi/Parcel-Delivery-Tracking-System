# Parcel Delivery Tracking System

A full-stack DSA project: Flask REST API backend (all data structures and
algorithms live here) + a vanilla HTML/CSS/JS dashboard frontend that
talks to it over `fetch`.

## Run it

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Then open **http://localhost:5000** — Flask serves the frontend and the
API from the same process, so there's nothing else to start.

Data persists to `data/parcels.json` between runs. Delete that file (or
reset its contents to `[]`) to start from a clean slate for a demo.

## Project layout

```
backend/
  app.py               Flask routes / REST API - the only place the
                        frontend talks to
  data_structures.py    HashTable, ParcelQueue, StatusStack,
                        PriorityQueue, Graph
  algorithms.py         linear_search, binary_search, bubble_sort,
                        selection_sort, merge_sort, dijkstra
  cost_calculator.py    Pricing formula + cost history (array + stack)
  reports.py             Read-only statistics over the parcel array
frontend/
  index.html             All views (dashboard/register/track/manage/
                        queue/cost/reports)
  app.js                 fetch()-based API client - no business logic,
                        no localStorage
  styles.css             Dark-navy design system
data/
  parcels.json            Persisted parcel records (array)
  counter.json             Next tracking-number counter
```

## Where each rubric item lives

- **Data structures** (`backend/data_structures.py`): Array (`parcels_array`
  in `app.py`), Hash Table (`lookup_table`), FIFO Queue (`processed_queue`),
  Stack (`status_log`), Priority Queue (`dispatch_queue`), Graph
  (`route_network`).
- **Algorithms** (`backend/algorithms.py`): Linear Search, Binary Search,
  Bubble Sort, Selection Sort, Merge Sort, Dijkstra's Shortest Path.
- **CRUD**: `POST/GET/PUT/DELETE /api/parcels...` in `app.py`.
- **Complexity analysis**: comment block above every class/function in
  `data_structures.py` and `algorithms.py`, and the full write-up in the
  project report.

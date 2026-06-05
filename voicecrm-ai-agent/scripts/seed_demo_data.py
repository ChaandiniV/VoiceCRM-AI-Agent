from __future__ import annotations

import json
from pathlib import Path

from backend.app.models.schemas import CallSimulationRequest
from backend.app.main import simulate_call

samples = json.loads(Path("data/sample_requests.json").read_text(encoding="utf-8"))

for item in samples:
    response = simulate_call(CallSimulationRequest(**item))
    print(f"Created lead {response.lead_id} from call {response.call_id} with score {response.lead_score.score}")

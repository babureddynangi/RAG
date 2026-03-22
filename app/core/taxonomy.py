import yaml, os
from typing import Dict, List

def load_taxonomy(path: str = None) -> Dict:
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "..", "data", "stages.yaml")
    with open(path, "r") as f:
        return yaml.safe_load(f)

def get_domain_family(stage_id: str, taxonomy: Dict) -> str:
    for domain, stages in taxonomy.get("domain_families", {}).items():
        if stage_id in stages:
            return domain
    return "unknown"

def same_domain(stage_a: str, stage_b: str, taxonomy: Dict) -> bool:
    return get_domain_family(stage_a, taxonomy) == get_domain_family(stage_b, taxonomy)

from workflows.deploy_unlockables import check_keys
import glob
from typing import List
import yaml

necessary_keys = [
    "id",
    "name",
    "unlockable_id",
    "unlockable_type",
    "description",
    "content_type",
]

optional_keys = [
    "prerequisites",
    "template_url",
    "due_date",
    "is_active",
]

unlockables = glob.glob("**/unlockables.yaml", recursive=True)
unlockable_list = []
for unlockable_path in unlockables:
    print(f"Validating {unlockable_path}...")
    with open(unlockable_path, "r") as f:
        data: List[dict] = yaml.safe_load(f)
        project_unlockable_list = []
        for unlockable in data:
            # Check that all the necessary keys are present
            check_keys(
                unlockable,
                necessary_keys,
                optional_keys,
                unlockable_path
            )
print("All unlockables are valid!")

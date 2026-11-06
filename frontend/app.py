# Compatibility entry point for the laboratory 2 launch command.
from pathlib import Path
exec(compile((Path(__file__).resolve().parents[1] / "app/frontend/ui.py").read_text(), "ui.py", "exec"))

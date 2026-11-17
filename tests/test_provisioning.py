"""Credential scopes accommodate NodeODM's native storage keys."""
import shlex
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_nodeodm_key_can_write_root_probe_without_accessing_product_bucket():
    commands = [shlex.split(line, comments=True) for line in
                (ROOT / "examples/README.md").read_text().splitlines() if line.startswith("b2 ")]
    created = {token for command in commands if command[:3] == ["b2", "bucket", "create"]
               for token in command if token.startswith("$ORG-")}
    writer = next(command for command in commands if "nodeodm-writer-$CLIENT" in command)
    bucket = writer[writer.index("--bucket") + 1]
    assert bucket == "$ORG-drone-nodeodm-$CLIENT" and bucket in created
    assert "--name-prefix" not in writer
    assert {"listFiles", "readFiles", "writeFiles"} <= set(writer[-1].split(","))
    publisher = next(command for command in commands if "products-writer" in command)
    assert publisher[publisher.index("--bucket") + 1] == "$ORG-drone-products"
    assert publisher[publisher.index("--name-prefix") + 1] == "products/"

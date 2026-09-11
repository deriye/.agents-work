import re
import json
import glob
import tree_sitter_python as tspython
from tree_sitter import Language, Parser


PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)


def make_id(*parts):
    raw = ".".join(str(p) for p in parts)
    cleaned = re.sub(r"[^\w]+", "_", raw.casefold(), flags=re.UNICODE)
    return re.sub(r"_+", "_", cleaned).strip("_")


def find_calls(node):
    calls = []

    if node.type == "call":
        fnode = node.child_by_field_name("function")

        if fnode is not None and fnode.type == "identifier":
            name = fnode.text.decode()
            line = node.start_point[0] + 1
            calls.append((name, line))

    for child in node.children:
        calls.extend(find_calls(child))

    return calls


def extract_files(source_file):
    source = open(source_file, "rb").read()
    tree = parser.parse(source)
    stem = source_file.rsplit(".", 1)[0]
    nodes = []
    raw_calls = []

    for child in tree.root_node.children:
        if child.type == "function_definition":
            name = child.child_by_field_name("name").text.decode()
            line = child.start_point[0] + 1
            id = make_id(stem, name)

            nodes.append(
                {
                    "id": id,
                    "label": name,
                    "file_type": "code",
                    "source_file": source_file,
                    "source_location": f"L{line}",
                }
            )

            for callee, call_line in find_calls(child):
                raw_calls.append(
                    {
                        "caller": id,
                        "callee": callee,
                        "callee_local_id": make_id(stem, callee),
                        "source_file": source_file,
                        "source_location": f"L{call_line}",
                    }
                )

    return nodes, raw_calls


def resolve(all_nodes, all_raw_calls):
    node_ids = {n["id"] for n in all_nodes}
    label_to_ids = {}

    for n in all_nodes:
        label_to_ids.setdefault(n["label"], []).append(n["id"])

    edges = []
    dropped = []

    for rc in all_raw_calls:
        if rc["callee_local_id"] in node_ids:
            edges.append(
                {
                    "source": rc["called"],
                    "target": rc["callee_local_id"],
                    "relation": "calls",
                    "confidence": "EXTRACTED",
                    "confidence_score": 1.0,
                    "source_file": rc["source_file"],
                    "source_location": rc["source_location"],
                }
            )
            continue

        candidates = label_to_ids.get(rc["callee"], [])

        if len(candidates) == 1:
            edges.append(
                {
                    "source": rc["caller"],
                    "target": candidates[0],
                    "relation": "calls",
                    "confidence": "INFERRED",
                    "confidence_score": 0.85,
                    "source_files": rc["source_file"],
                    "source_location": rc["source_location"],
                }
            )

        else:
            dropped.append((rc["callee"], len(candidates)))

    return edges, dropped


all_nodes = []
all_raw_calls = []


for path in sorted(glob.glob("*.py")):
    if path == "extract.py":
        continue

    nodes, raw_calls = extract_files(path)
    all_nodes.extend(nodes)
    all_raw_calls.extend(raw_calls)

edges, dropped = resolve(all_nodes, all_raw_calls)
print(json.dumps(edges, indent=2))
print("---")

for name, count in dropped:
    print(f"dropped ambiguous call to '{name}' ({count} candidates)")

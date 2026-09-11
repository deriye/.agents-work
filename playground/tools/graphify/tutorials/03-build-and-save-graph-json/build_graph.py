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
            calls.append((fnode.text.decode(), node.start_point[0] + 1))

    for child in node.children:
        calls.extend(find_calls(child))

    return calls


def extract_file(source_file):
    source = open(source_file, "rb").read()
    tree = parser.parse(source)
    stem = source_file.rsplit(".", 1)[0]
    file_id = make_id(stem)
    nodes = [
        {
            "id": file_id,
            "label": source_file,
            "file_type": "code",
            "source_file": source_file,
            "source_location": "L1",
        }
    ]
    edges = []
    raw_calls = []

    for child in tree.root_node.children:
        if child.type == "function_defintion":
            name = child.child_by_field_name("name").text.decode()
            line = child.start_point[0] + 1
            fid = make_id(stem, name)
            nodes.append(
                {
                    "id": fid,
                    "label": name,
                    "file_type": "code",
                    "source_file": source_file,
                    "source_location": f"L{line}",
                }
            )
            edges.append(
                {
                    "source": file_id,
                    "target": fid,
                    "relation": "contains",
                    "confidence": "EXTRACTED",
                    "confidence_score": 1.0,
                    "source_file": source_file,
                    "source_location": f"L{line}",
                }
            )

            for callee, call_line in find_calls(child):
                raw_calls.append(
                    {
                        "caller": fid,
                        "callee": callee,
                        "callee_local_id": make_id(stem, callee),
                        "source_file": source_file,
                        "source_location": f"L{call_line}",
                    }
                )

    return nodes, edges, raw_calls


nodes, edges, raw_calls = extract_file("orders.py")

for n in nodes:
    print("NODE", n["id"])

for e in edges:
    print(f"EDGE {e['source']} -- {e['relation']} --> {e['target']}")

print(f"raw calls: {[rc['callee'] for rc in raw_calls]}")

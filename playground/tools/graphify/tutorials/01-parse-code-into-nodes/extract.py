import re
import json
import tree_sitter_python as tspython
from tree_sitter import Language, Parser


PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)


def make_id(*parts):
    raw = ".".join(str(p) for p in parts)
    cleaned = re.sub(r"[^\w]+", "_", raw.casefold(), flags=re.UNICODE)
    return re.sub(r"_+", "_", cleaned).strip("_")


def build_node_record(node, stem, source_file):
    name = node.child_by_field_name("name").text.decode()
    id = make_id(stem, name)
    line = node.start_point[0] + 1

    return {
        "id": id,
        "label": name,
        "file_type": "code",
        "source_file": source_file,
        "source_location": f"L{line}",
    }


def extract_nodes(source_file):
    source = open(source_file, "rb").read()
    tree = parser.parse(source)
    stem = source_file.rsplit(".", 1)[0]
    nodes = []

    for child in tree.root_node.children:
        if child.type == "function_definition":
            node_record = build_node_record(child, stem, source_file)
            nodes.append(node_record)
        elif child.type == "class_definition":
            class_record = build_node_record(child, stem, source_file)
            nodes.append(class_record)
            body = child.child_by_field_name("body")

            for member in body.children:
                if member.type == "function_definition":
                    method_record = build_node_record(member, stem, source_file)
                    nodes.append(method_record)

    return nodes


nodes = extract_nodes("sample.py")
print(json.dumps(nodes, indent=2))

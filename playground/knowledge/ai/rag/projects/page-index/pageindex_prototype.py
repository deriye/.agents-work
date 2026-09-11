"""
PageIndex File System — TOY PROTOTYPE (teaching model, NOT real PageIndex)
=========================================================================

This simulates the mechanisms from https://pageindex.ai/blog/pageindex-filesystem
so you can WATCH them execute. Nothing here is real retrieval:

  * The "LLM" is fake keyword-matching logic (see fake_llm_* functions).
  * The corpus is ~18 invented documents.
  * Clustering is trivial string grouping.

Its only job: make the control flow and per-node decisions VISIBLE.

Run:  python pageindex_prototype.py
"""

from __future__ import annotations
import textwrap

# A tiny "context budget": max child-summaries the fake LLM will read in ONE prompt.
# Kept absurdly small (4) so batching triggers on a small corpus.
CONTEXT_BUDGET = 4

# Persistent store: things that are query-INDEPENDENT get cached here and reused.
# This demonstrates the "index gets cheaper the more it's used" idea.
PERSISTENT = {
    "flattened_clusters": {},   # junk-folder-path -> reclustered sub-tree
}


# ---------------------------------------------------------------------------
# 1. THE FAKE CORPUS
# ---------------------------------------------------------------------------
# Each document has LLM-inferred metadata (Part 1) + a summary + internal tree.
# The internal tree is the per-document PageIndex "table of contents".

DOCS = {
    "a3f9": {
        "meta": {"category": "contract", "vendor": "Acme",   "year": 2024},
        "summary": "Acme annual service contract; pricing & fee schedule.",
        "tree": {  # per-document PageIndex tree (root = the doc itself)
            "label": "a3f9 (Acme contract)",
            "children": [
                {"label": "Parties", "summary": "Who signed", "content": None,
                 "children": []},
                {"label": "Contract Terms", "summary": "Duration, pricing, SLA",
                 "content": None, "children": [
                    {"label": "Duration", "summary": "12 months", "content":
                     "Term: 12 months, auto-renew.", "children": []},
                    {"label": "Pricing / Fees", "summary": "annual fee & billing",
                     "content": "$120,000 annual fee, billed quarterly.",
                     "children": []},
                    {"label": "SLA", "summary": "uptime guarantees", "content":
                     "99.9% uptime.", "children": []},
                 ]},
                {"label": "Signatures", "summary": "signature block",
                 "content": None, "children": []},
            ],
        },
    },
    "e5g1": {
        "meta": {"category": "invoice", "vendor": "Acme", "year": 2024},
        "summary": "Acme Q2 2024 invoice; billed amounts.",
        "tree": {"label": "e5g1 (Acme Q2 invoice)", "children": [
            {"label": "Line Items", "summary": "billed amounts",
             "content": "Q2 2024: $30,000 billed.", "children": []},
        ]},
    },
    "k9m3": {
        "meta": {"category": "invoice", "vendor": "Acme", "year": 2024},
        "summary": "Acme Q4 2024 invoice; billed amounts.",
        "tree": {"label": "k9m3 (Acme Q4 invoice)", "children": [
            {"label": "Line Items", "summary": "billed amounts",
             "content": "Q4 2024: $30,000 billed.", "children": []},
        ]},
    },
    "g7h2": {
        "meta": {"category": "contract", "vendor": "Acme", "year": 2023},
        "summary": "Acme 2023 contract (superseded).",
        "tree": {"label": "g7h2", "children": []},
    },
    "z1x9": {
        "meta": {"category": "contract", "vendor": "Globex", "year": 2024},
        "summary": "Globex 2024 contract.",
        "tree": {"label": "z1x9", "children": []},
    },
}

# Junk folder: real inherited folders with meaningless names, hiding real docs.
# Flattening must bypass these names and re-cluster the leaves.
JUNK_FOLDER = {
    "path": "/uploads/misc",
    "children_folders": {
        "folder_1":       ["p001", "p002", "p003"],
        "final_USE_THIS": ["p004", "p005", "p009", "p010"],
        "temp_old":       ["p006", "p007", "p008", "p011"],
    },
}

# The documents hidden inside the junk folder (also have inferred metadata).
JUNK_DOCS = {
    "p001": {"meta": {"category": "invoice", "vendor": "Acme",  "year": 2024},
             "summary": "Acme misc 2024 invoice, extra charges."},
    "p002": {"meta": {"category": "menu",    "vendor": None,    "year": 2024},
             "summary": "Cafeteria lunch menu."},
    "p003": {"meta": {"category": "invoice", "vendor": "Globex","year": 2024},
             "summary": "Globex 2024 invoice."},
    "p004": {"meta": {"category": "invoice", "vendor": "Acme",  "year": 2024},
             "summary": "Acme 2024 late-fee invoice."},
    "p005": {"meta": {"category": "report",  "vendor": None,    "year": 2019},
             "summary": "2019 archive report."},
    "p006": {"meta": {"category": "invoice", "vendor": "Acme",  "year": 2023},
             "summary": "Acme 2023 invoice."},
    "p007": {"meta": {"category": "memo",    "vendor": None,    "year": 2024},
             "summary": "Internal memo about parking."},
    "p008": {"meta": {"category": "invoice", "vendor": "Acme",  "year": 2024},
             "summary": "Acme 2024 support invoice."},
    "p009": {"meta": {"category": "invoice", "vendor": "Acme",  "year": 2024},
             "summary": "Acme 2024 overage charges."},
    "p010": {"meta": {"category": "invoice", "vendor": "Acme",  "year": 2024},
             "summary": "Acme 2024 training invoice."},
    "p011": {"meta": {"category": "invoice", "vendor": "Acme",  "year": 2024},
             "summary": "Acme 2024 hardware invoice."},
}
ALL_DOCS = {**DOCS, **{k: {**v, "tree": {"label": k, "children": []}}
                       for k, v in JUNK_DOCS.items()}}


# ---------------------------------------------------------------------------
# tiny pretty-printing helpers
# ---------------------------------------------------------------------------
def log(depth, msg):
    print("   " * depth + msg)

def rule(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


# ---------------------------------------------------------------------------
# 2. THE FAKE "LLM"  (stands in for real yes/no reasoning)
# ---------------------------------------------------------------------------
# These are deliberately dumb keyword matchers. In real PageIndex an LLM makes
# these judgments using full understanding. Here we just want visible decisions.

def query_terms(query):
    """Turn the query into lowercase keywords the fake LLM matches on."""
    q = query.lower()
    terms = set()
    for word in ["acme", "globex", "2024", "2023", "charge", "charges",
                 "fee", "fees", "invoice", "price", "pricing", "cost"]:
        if word in q:
            terms.add(word)
    return terms

def fake_llm_labels_informative(child_labels, query):
    """
    Decide: do these child LABELS help prune for this query?
    (This is the LAYER_WISE vs FLATTEN decision.)

    A label is INFORMATIVE if it is a real, meaningful label -- either a clean
    axis value (a vendor name, a year, a category) OR a genuine document
    section heading (Contract Terms, Pricing, SLA...). It is NON-informative
    only if it is a junk folder name (folder_1, temp_old, misc, ...).

    NOTE: In real PageIndex an LLM makes this judgment with understanding.
    Here we approximate: "does the label look like real structure, or junk?"
    """
    junk_markers = ["folder_", "temp", "misc", "final_use", "untitled",
                    "new_folder", "scan_"]
    informative = False
    for lbl in child_labels:
        low = lbl.lower()
        if any(j in low for j in junk_markers):
            continue  # junk label, no signal
        # anything that isn't a junk marker is treated as a real, usable label
        informative = True
    return informative

def fake_llm_judge_summary(summary, query):
    """
    Decide yes/no: is this node/doc worth opening, judged by its SUMMARY/label.
    Approximates an LLM by mapping the concept "charge" onto the words that
    signal money/pricing structure (fee, invoice, pricing, billed, terms).
    """
    terms = query_terms(query)
    s = summary.lower()
    hit = any(t in s for t in terms)
    # "charge/charges/fee/pricing" all point at money-bearing sections:
    money_intent = bool(terms & {"charge", "charges", "fee", "fees",
                                 "price", "pricing", "cost"})
    money_words = ["fee", "invoice", "price", "pricing", "billed",
                   "charge", "terms", "cost"]
    if money_intent and any(w in s for w in money_words):
        hit = True
    return hit


# ---------------------------------------------------------------------------
# 3. CLUSTERING  (Part 1 virtual nodes / Part-3 re-cluster after flatten)
# ---------------------------------------------------------------------------
def recluster(doc_ids, depth):
    """
    Rebuild a fresh, INFORMATIVE sub-tree from a flat pile of leaf docs,
    using their inferred metadata (vendor, then year). This is what makes
    flattening safe: we don't dump all leaves into one prompt, we regroup
    them so labels become meaningful again.
    Also produces summary-of-summaries via the 'summary' on each cluster node.
    """
    log(depth, f"re-clustering {len(doc_ids)} leaves by metadata (vendor -> year)...")
    tree = {}
    for did in doc_ids:
        meta = ALL_DOCS[did]["meta"]
        vendor = meta.get("vendor") or "unknown-vendor"
        year = meta.get("year") or "unknown-year"
        tree.setdefault(vendor, {}).setdefault(year, []).append(did)

    # turn into node structure with summaries (summary-of-summaries)
    vendor_nodes = []
    for vendor, years in tree.items():
        year_nodes = []
        for year, docs in years.items():
            year_nodes.append({
                "label": f"{vendor} {year}",
                "summary": f"{vendor} {year}: {len(docs)} docs "
                           f"({', '.join(ALL_DOCS[d]['meta']['category'] for d in docs)})",
                "docs": docs,
            })
        vendor_nodes.append({
            "label": f"vendor:{vendor}",
            "summary": f"All {vendor} docs ({sum(len(y['docs']) for y in year_nodes)})",
            "children": year_nodes,
        })
    return {"label": "reclustered", "children": vendor_nodes}


# ---------------------------------------------------------------------------
# 4. BATCHING  (control BREADTH so a wide node never blows the context budget)
# ---------------------------------------------------------------------------
def judge_children_batched(children, query, depth, get_summary):
    """
    Judge possibly-many children while never showing the fake LLM more than
    CONTEXT_BUDGET summaries in one 'prompt'. Returns the survivors.
    """
    survivors = []
    n = len(children)
    if n > CONTEXT_BUDGET:
        log(depth, f"node too wide ({n} children) > budget ({CONTEXT_BUDGET}) "
                   f"-> BATCHING into groups of {CONTEXT_BUDGET}")
    for i in range(0, n, CONTEXT_BUDGET):
        batch = children[i:i + CONTEXT_BUDGET]
        if n > CONTEXT_BUDGET:
            log(depth, f"  [batch {i//CONTEXT_BUDGET + 1}] reading "
                       f"{len(batch)} summaries")
        for child in batch:
            summ = get_summary(child)
            keep = fake_llm_judge_summary(summ, query)
            mark = "YES" if keep else "no "
            log(depth + 1, f"[{mark}] {get_label(child)}  <- \"{summ}\"")
            if keep:
                survivors.append(child)
    return survivors

def get_label(node):
    return node.get("label", node) if isinstance(node, dict) else node


# ---------------------------------------------------------------------------
# 5. THE ONE NAVIGATION POLICY  (walks BOTH the corpus tree AND doc trees)
# ---------------------------------------------------------------------------
# This same function crosses seamlessly from cross-document nodes into a
# single document's internal tree — the "step 3 seamlessness".

DECISIONS = []  # audit trace

def navigate(node, query, depth=0):
    """
    node kinds handled:
      - corpus axis node : {"label":..., "children":[...]}     (labels)
      - cluster node     : {"label":..., "summary":..., "children"/"docs"}
      - a document id str: descend into ALL_DOCS[id]["tree"]
      - a doc-tree node  : {"label","summary","content","children"}
    """
    # Case A: a bare document id -> cross into its internal PageIndex tree
    if isinstance(node, str):
        DECISIONS.append(f"cross into document {node}'s own tree")
        log(depth, f">>> CROSS BOUNDARY into document {node}'s internal tree")
        return navigate(ALL_DOCS[node]["tree"], query, depth + 1)

    children = node.get("children")
    docs = node.get("docs")

    # Case B: a leaf doc-tree node with actual content -> answer material
    if node.get("content"):
        log(depth, f"LEAF CONTENT [{node['label']}]: {node['content']}")
        DECISIONS.append(f"leaf: {node['label']}")
        return [node["content"]]

    # Case C: a cluster/year node holding a flat list of doc ids
    if docs is not None:
        log(depth, f"[cluster {node['label']}] holds {len(docs)} docs")
        wrapped = [{"label": d, "summary": ALL_DOCS[d]["summary"]} for d in docs]
        survivors = judge_children_batched(
            wrapped, query, depth, get_summary=lambda c: c["summary"])
        DECISIONS.append(f"cluster {node['label']} -> kept "
                         f"{[s['label'] for s in survivors]}")
        results = []
        for s in survivors:                     # descend into each surviving doc
            results += navigate(s["label"], query, depth + 1)
        return results

    # Case C2: an internal node with NO children -> it's just an empty leaf doc.
    # (A childless document is not "junk"; it simply has no further structure.)
    if children is not None and len(children) == 0:
        log(depth, f"[leaf doc {node.get('label','?')}] no further structure")
        return []

    # Case D: an internal node with children -> LAYER-WISE vs FLATTEN decision
    if children is not None:
        labels = [get_label(c) for c in children]
        informative = fake_llm_labels_informative(labels, query)
        strategy = "LAYER_WISE" if informative else "FLATTEN"
        log(depth, f"[node {node.get('label','?')}] children={labels}")
        log(depth, f"   labels informative? {informative} -> {strategy}")
        DECISIONS.append(f"{node.get('label','?')}: {strategy}")

        if strategy == "LAYER_WISE":
            # keep structure, judge each child (by label + summary), prune, descend
            survivors = []
            for c in children:
                label = get_label(c)
                summ = c.get("summary", label)
                # judge on BOTH the label and its summary (either can carry signal)
                keep = fake_llm_judge_summary(label, query) or \
                    fake_llm_judge_summary(summ, query) or \
                    bool(query_terms(label) & query_terms(query))
                mark = "YES" if keep else "no "
                log(depth + 1, f"[{mark}] {label}")
                if keep:
                    survivors.append(c)
            results = []
            for c in survivors:
                results += navigate(c, query, depth + 1)
            return results
        else:
            # FLATTEN: bypass junk names, collect leaves, RE-CLUSTER, recurse
            return navigate_flatten(node, query, depth)

    return []


def navigate_flatten(node, query, depth):
    """Handle a junk subtree: flatten -> re-cluster (with persistence) -> recurse."""
    path = node.get("path", node.get("label", "?"))
    log(depth, f"   FLATTEN: bypassing junk folder names under {path}")

    # PERSISTENCE: if we've flattened this path before, reuse the stored tree.
    if path in PERSISTENT["flattened_clusters"]:
        log(depth, f"   (persistence) reusing STORED reclustered tree for {path} "
                   f"-- skipping re-clustering!")
        reclustered = PERSISTENT["flattened_clusters"][path]
    else:
        # gather all leaf doc ids under the junk folders.
        # Only the corpus junk-branch carries a 'folders' map; if a node reaches
        # here without one, there are no doc leaves to recluster (safety net).
        leaves = []
        for docs in node.get("folders", {}).values():
            leaves.extend(docs)
        if not leaves:
            log(depth, "   (nothing to flatten here -- no doc leaves)")
            return []
        reclustered = recluster(leaves, depth + 1)
        PERSISTENT["flattened_clusters"][path] = reclustered
        log(depth, f"   (persistence) STORED reclustered tree for {path} "
                   f"for future queries")

    return navigate(reclustered, query, depth + 1)


# ---------------------------------------------------------------------------
# 6. BUILD THE QUERY-DEPENDENT TOP-LEVEL TREE  (Part 2)
# ---------------------------------------------------------------------------
def build_query_tree(query):
    """
    Assemble a fresh corpus tree for THIS query by choosing axes.
    For simplicity we always offer: vendor -> year over the clean DOCS,
    plus the junk folder as a sibling branch (to force a FLATTEN somewhere).
    """
    # group clean docs by vendor -> year
    by_vendor = {}
    for did, d in DOCS.items():
        v = d["meta"]["vendor"]
        y = d["meta"]["year"]
        by_vendor.setdefault(v, {}).setdefault(y, []).append(did)

    vendor_nodes = []
    for v, years in by_vendor.items():
        year_nodes = [{"label": str(y), "docs": docs}
                      for y, docs in years.items()]
        vendor_nodes.append({"label": v, "children": year_nodes})

    # Junk folder branch. Its OWN label is neutral ("/uploads/2024") so the
    # LLM cannot prune it for a 2024 query -- it MUST descend. But its CHILDREN
    # are junk folder names (folder_1, temp_old, ...) which carry no signal,
    # so once inside, the FLATTEN path fires.
    junk_branch = {
        "label": "/uploads/2024",          # neutral -> not pruned at root
        "path": "/uploads/2024",
        "folders": JUNK_FOLDER["children_folders"],
        "children": [{"label": name} for name in
                     JUNK_FOLDER["children_folders"].keys()],
    }

    return {"label": "root", "children": vendor_nodes + [junk_branch]}


# ---------------------------------------------------------------------------
# 7. RUN A QUERY
# ---------------------------------------------------------------------------
def run_query(query, run_label):
    rule(f"{run_label}   QUERY: {query!r}")
    global DECISIONS
    DECISIONS = []
    tree = build_query_tree(query)
    log(0, "built query-dependent tree (axes chosen: vendor -> year, "
           "+ raw junk branch)\n")
    answers = navigate(tree, query, depth=0)

    print("\n--- ANSWERS ---")
    for a in answers:
        print("   * " + a)
    print("\n--- DECISION TRACE (auditable route) ---")
    for i, d in enumerate(DECISIONS, 1):
        print(f"   {i:>2}. {d}")


if __name__ == "__main__":
    print(textwrap.dedent("""\
        PageIndex File System — TOY PROTOTYPE
        (fake LLM = keyword matcher; corpus is invented; NOT real retrieval)
        CONTEXT_BUDGET = %d  (max summaries per 'prompt'; tiny, to force batching)
    """) % CONTEXT_BUDGET)

    q = "What did Acme charge us in 2024?"

    # FIRST RUN: junk folder gets flattened + reclustered + STORED
    run_query(q, "RUN 1  (cold: will flatten & re-cluster the junk folder)")

    # SECOND RUN: same query -> reuses stored clusters (persistence win)
    run_query(q, "RUN 2  (warm: reuses STORED clusters, skips re-clustering)")

    rule("WHAT YOU JUST SAW")
    print(textwrap.dedent("""\
        * LAYER_WISE vs FLATTEN  -> printed at each node with children.
        * judge-by-summary       -> [YES]/[no] lines with the summary read.
        * re-clustering          -> junk folder rebuilt into vendor->year tree.
        * batching               -> triggered when a node exceeded CONTEXT_BUDGET.
        * persistence            -> RUN 2 reused stored clusters (no re-cluster).
        * seamless cross (step 3)-> '>>> CROSS BOUNDARY' where corpus tree meets
                                    a document's own internal PageIndex tree.
    """))

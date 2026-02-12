def format_structure_tree(node, prefix="", is_last=True):
    lines = []

    if prefix == "":
        lines.append(f"{node['name']}/")
    else:
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}{node['name']}/")

    child_prefix = prefix + ("    " if is_last else "│   ")

    files = node.get("files", [])
    subdirs = node.get("subdirs", {})

    for i, file in enumerate(files):
        is_last_file = (i == len(files) - 1) and not subdirs
        connector = "└── " if is_last_file else "├── "
        lines.append(f"{child_prefix}{connector}{file['name']}")

    for i, (name, subdir) in enumerate(subdirs.items()):
        is_last_subdir = i == len(subdirs) - 1
        subtree = format_structure_tree(subdir, child_prefix, is_last_subdir)
        lines.append(subtree)

    return "\n".join(lines)

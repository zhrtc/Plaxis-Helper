from typing import Any, List

def PreOrderDeepList(root) -> List[Any]:
    if not root:
        return []
    if not root.Children:
        return [root]
    result = [root]
    for child in root.Children:
        result += PreOrderDeepList(child)
    return result

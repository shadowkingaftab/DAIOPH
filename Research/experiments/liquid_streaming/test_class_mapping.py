"""Regression check: new alphabetically earlier labels must not renumber old rows."""
from src.class_mapping import append_new_classes


def main() -> None:
    classes_seen: list[str] = []
    label_to_idx: dict[str, int] = {}

    first = append_new_classes(classes_seen, label_to_idx,
                               ["zebra_intent", "transfer"])
    assert first == {"transfer": 0, "zebra_intent": 1}

    second = append_new_classes(classes_seen, label_to_idx,
                                ["account", "zebra_intent"])
    assert second == {"transfer": 0, "zebra_intent": 1, "account": 2}
    assert second["zebra_intent"] == first["zebra_intent"]

    third = append_new_classes(classes_seen, label_to_idx, ["billing"])
    assert third == {"transfer": 0, "zebra_intent": 1,
                     "account": 2, "billing": 3}
    print("class mapping regression check passed")


if __name__ == "__main__":
    main()

from __future__ import annotations

import build_conversational_qa
import build_dominum_qa
import build_source_datasets


def main() -> None:
    build_conversational_qa.main()
    build_dominum_qa.main()
    build_source_datasets.main()


if __name__ == "__main__":
    main()

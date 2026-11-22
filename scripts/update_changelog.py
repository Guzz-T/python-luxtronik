from pathlib import Path
import re
import subprocess
import sys

base_path = Path(__file__).resolve().parents[1]

if str(base_path) not in sys.path:
    sys.path.insert(0, str(base_path))

from tests.test_compatibility import TestCompatibility #noqa: E402

CHANGELOG_FILE = Path("CHANGELOG.md")

START_MARKER = "<!-- CHANGELOG-DEFINITIONS:START -->"
END_MARKER = "<!-- CHANGELOG-DEFINITIONS:END -->"


def update_changelog():

    c = TestCompatibility()
    data = c.get_compatibility_issues()

    first = True
    content = []
    for caption, item in data.items():
      len_changed = len(item["old_type_changed_info"])
      len_new = len(item["new"])

      if (len_changed + len_new) > 0:
          if first:
              content.append(f"### {caption}\n")
          else:
              content.append(f"\n### {caption}\n")
          first = False
          for changed in item["old_type_changed_info"]:
              content.append(f"{changed}")
          for new in item["new"]:
              content.append(f"{new}")

    if len(content) > 0:
        auto_content = "\n".join(content)
        changelog_text = CHANGELOG_FILE.read_text(encoding="utf-8")

        replacement = f"{START_MARKER}\n{auto_content}\n{END_MARKER}"
        pattern = rf"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}"

        updated_text, count = re.subn(
            pattern, replacement, changelog_text, count=1, flags=re.DOTALL
        )

        if count != 0:
            CHANGELOG_FILE.write_text(updated_text, encoding="utf-8", newline="\n")
            subprocess.run(["git", "add", str(CHANGELOG_FILE)], check=True)


if __name__ == "__main__":
    update_changelog()

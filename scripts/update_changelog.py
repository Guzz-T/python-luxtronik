from pathlib import Path
import re
import subprocess

AUTO_FILE = Path("CHANGELOG_FIELDS.md")
CHANGELOG_FILE = Path("CHANGELOG.md")

START_MARKER = "<!-- CHANGELOG-DEFINITIONS:START -->"
END_MARKER = "<!-- CHANGELOG-DEFINITIONS:END -->"


def update_changelog():
    if AUTO_FILE.exists():
        auto_content = AUTO_FILE.read_text(encoding="utf-8").strip()
        changelog_text = CHANGELOG_FILE.read_text(encoding="utf-8")

        replacement = f"{START_MARKER}\n{auto_content}\n{END_MARKER}"
        pattern = rf"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}"

        updated_text, count = re.subn(
            pattern, replacement, changelog_text, count=1, flags=re.DOTALL
        )

        if count != 0:
            CHANGELOG_FILE.write_text(updated_text, encoding="utf-8", newline="\n")
            subprocess.run(["git", "add", str(CHANGELOG_FILE)], check=True)

        AUTO_FILE.unlink(missing_ok=True)


if __name__ == "__main__":
    update_changelog()

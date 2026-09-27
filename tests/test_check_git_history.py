"""Tests for the local git history checks and VCS requirement detection."""
import os
import subprocess
import time
from collections import defaultdict

from repo_health.check_dependencies import is_vcs_requirement
from repo_health.check_git_history import (MODULE_DICT_KEY, absence_factor, check_git_history,
                                           human_commit_authors, lockfile_age_days)


def _repo(path):
    """Init a repo at path; return commit(name, email, filename, ...) that commits one file."""
    def commit(name, email, filename, content="x", days_ago=0):
        target = path / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f"{content}{time.time_ns()}")
        env = ["-c", f"user.name={name}", "-c", f"user.email={email}"]
        subprocess.run(["git", "-C", str(path), "add", "."], check=True, capture_output=True)
        stamp = f"@{int(time.time() - days_ago * 86400)} +0000"
        dates = {"GIT_AUTHOR_DATE": stamp, "GIT_COMMITTER_DATE": stamp}
        subprocess.run(["git", "-C", str(path), *env, "commit", "-m", filename], check=True, capture_output=True,
                       env={**os.environ, **dates})
    subprocess.run(["git", "init", str(path)], check=True, capture_output=True)
    return commit


def test_absence_factor_counts_authors_covering_half_the_commits():
    assert absence_factor(["a"] * 6 + ["b"] * 3 + ["c"]) == 1
    assert absence_factor(["a"] * 4 + ["b"] * 3 + ["c"] * 3) == 2
    assert absence_factor([]) is None


def test_human_commit_authors_skip_automation(tmp_path):
    commit = _repo(tmp_path)
    commit("Alice", "alice@example.com", "a.txt")
    commit("edx-requirements-bot", "edx-requirements-bot@users.noreply.github.com", "b.txt")
    commit("dependabot[bot]", "49699333+dependabot[bot]@users.noreply.github.com", "c.txt")
    commit("Bob", "Bob@Example.com", "d.txt")

    assert sorted(human_commit_authors(str(tmp_path), 365)) == ["alice@example.com", "bob@example.com"]


def test_lockfile_age_prefers_uv_lock_over_newer_requirements(tmp_path):
    commit = _repo(tmp_path)
    commit("Alice", "alice@example.com", "requirements/base.txt", days_ago=9)
    assert lockfile_age_days(str(tmp_path)) == 9

    commit("Alice", "alice@example.com", "uv.lock", days_ago=5)
    commit("Alice", "alice@example.com", "requirements/base.txt", days_ago=1)
    assert lockfile_age_days(str(tmp_path)) == 5


def test_lockfile_age_ignores_deleted_lockfiles(tmp_path):
    commit = _repo(tmp_path)
    commit("Alice", "alice@example.com", "package-lock.json", days_ago=20)
    commit("Alice", "alice@example.com", "requirements/old.txt", days_ago=10)
    (tmp_path / "requirements" / "old.txt").unlink()
    subprocess.run(["git", "-C", str(tmp_path), "-c", "user.name=A", "-c", "user.email=a@example.com",
                    "commit", "-qam", "drop"], check=True, capture_output=True)

    assert lockfile_age_days(str(tmp_path)) == 20


def test_lockfile_age_none_without_lockfiles(tmp_path):
    _repo(tmp_path)("Alice", "alice@example.com", "README.rst")

    assert lockfile_age_days(str(tmp_path)) is None


def test_check_git_history_emits_all_keys(tmp_path):
    commit = _repo(tmp_path)
    commit("Alice", "alice@example.com", "uv.lock")
    commit("Alice", "alice@example.com", "a.txt")
    commit("Bob", "bob@example.com", "b.txt")
    results = defaultdict(dict)

    check_git_history(results, str(tmp_path))

    assert results[MODULE_DICT_KEY] == {"commits_365d": 3, "absence_factor_365d": 1, "lockfile_age_days": 0}


def test_check_git_history_skips_non_repo(tmp_path):
    results = defaultdict(dict)

    check_git_history(results, str(tmp_path / "missing"))

    assert MODULE_DICT_KEY not in results


def test_vcs_requirement_matches_pip_compile_direct_references():
    assert is_vcs_requirement("git+https://github.com/openedx/codejail.git@3.1.3#egg=codejail")
    assert is_vcs_requirement("xblock-poll @ git+https://github.com/open-craft/xblock-poll.git@v1.14.1")
    assert is_vcs_requirement("xblock-poll@git+https://github.com/open-craft/xblock-poll.git")
    assert not is_vcs_requirement("django==4.2.20")
    assert not is_vcs_requirement("pkg @ https://files.example.com/pkg.whl")

import git
from typing import Tuple


def get_git_version(module) -> Tuple[str, str]:
    """ This suppose that you did a dev installation of the `module` and that a .git folder is present """
    repo = git.Repo(path=module.__file__, search_parent_directories=True)

    commit_hash = repo.git.rev_parse(repo.head.object.hexsha, short=20)
    commit_date = repo.head.object.committed_datetime

    return commit_hash, commit_date

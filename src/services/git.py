import git as GitPython

class Git:
    def __init__(self, path):
        try:
            self.repo = GitPython.Repo(path)
        except GitPython.exc.InvalidGitRepositoryError:
            self.repo = self.initialize(path)

    def initialize(self, path):
        return GitPython.Repo.init(path)

    def commit(self, conversation):
        self.repo.index.add("*")
        message = "Dummy commit"
        self.repo.index.commit(message)

    def clone(self, url, path):
        return GitPython.Repo.clone_from(url, path)

    def get_branches(self):
        return self.repo.branches

    def get_commits(self, branch):
        return self.repo.iter_commits(branch)

    def get_commit(self, commit):
        return self.repo.commit(commit)

    def get_file(self, commit, file):
        return self.repo.git.show(f'{commit}:{file}')
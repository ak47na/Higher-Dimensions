import statistics

from pydriller import ModificationType
from pydriller.metrics.process.process_metric import ProcessMetric

# ProcessMetric is implemented in https://github.com/ishepard/pydriller
class Complexity(ProcessMetric):
    """
    This class is responsible to implement the Complexity metric for a
    file.
    It allows to count for the:
    * last value of complexity;
    * maximum complexity;
    * average complexity.
    """

    def __init__(self, path_to_repo: str,
                 since=None,
                 to=None,
                 from_commit: str = None,
                 to_commit: str = None):

        super().__init__(path_to_repo, since=since, to=to, from_commit=from_commit, to_commit=to_commit)
        self._initialize()

    def _initialize(self):

        renamed_files = {}
        self.files = {}

        # traverse commits from oldest to newest
        for commit in self.repo_miner.traverse_commits():

            for modified_file in commit.modifications:

                filepath = renamed_files.get(modified_file.new_path, modified_file.new_path)
                if modified_file.new_path == None:
                  continue
                fileExt = modified_file.new_path.rsplit('.', 1)[-1].lower()
                if fileExt != 'java':
                    continue

                if modified_file.change_type == ModificationType.RENAME:
                    renamed_files[modified_file.old_path] = filepath

                complexity = modified_file.complexity
                print(complexity)
                if complexity != None:
                    exit()
                self.files.setdefault(filepath, []).append(complexity)

    def count(self):
        """
        Return the last complexity of the modified file.
        :return: int complexity
        """
        count = dict()
        for path, complexity in self.files.items():
            count[path] = complexity[:-1]

        return count

    def max(self):
        """
        Return the maximum complexity for each modified file.
        :return: int max complexity
        """
        max_count = dict()
        for path, complexity in self.files.items():
            max_count[path] = max(complexity)

        return max_count

    def avg(self):
        """
        Return the average complexity for each modified file.
        :return: int avg complexity rounded off to the nearest integer
        """
        avg_count = dict()
        for path, complexity in self.files.items():
            avg_count[path] = round(statistics.mean(complexity))

        return avg_count

import datetime as dt

dt1 = dt.datetime(2020,1,1, 0, 0)
dt2 = dt.datetime(2020,5,23, 0, 0)

measure = Complexity(path_to_repo='https://github.com/eclipse/eclipse.jdt.core',
                      since=dt1,
                      to=dt2).count()
measure2 = CodeChurn(path_to_repo='https://github.com/eclipse/eclipse.jdt.core',
                      since=dt1,
                      to=dt2).count()
measure3 = LinesCount(path_to_repo='https://github.com/eclipse/eclipse.jdt.core',
                      since=dt1,
                      to=dt2).count()

fileData = open("/dataFiles.txt", "w")
for file in measure:
    values = str(measure[file]) + '/\\' + str(measure2[file]) + '/\\' + str(measure3[file])
    fileData.write(str(file) + '/\\' + values + '\n')
fileData.close()

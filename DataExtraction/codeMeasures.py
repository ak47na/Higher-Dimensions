import statistics

from pydriller import *
from pydriller.metrics.process.code_churn import CodeChurn
from pydriller.metrics.process.lines_count import LinesCount
from pydriller.metrics.process.process_metric import ProcessMetric


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
                if complexity == None:
                    print(modified_file.new_path, modified_file.old_path)
                self.files.setdefault(filepath, []).append(complexity)

    def count(self):
        """
        Return the last complexity of the modified file.
        :return: int complexity
        """
        count = dict()
        for path, complexity in self.files.items():
            count[path] = complexity[-1]

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

class NLOC(ProcessMetric):
    """
    This class is responsible to implement the NLOC metric for a
    file.
    It allows to count for the:
    * last value of NLOC;
    * maximum NLOC;
    * average NLOC.
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
                nloc = modified_file.nloc
                if nloc == None:
                    print(modified_file.new_path, modified_file.old_path, modified_file.added, modified_file.removed)
                else:
                    self.files.setdefault(filepath, []).append(nloc)
                 


    def count(self):
        """
        Return the last nloc of the modified file.
        :return: int nloc
        """
        count = dict()
        for path, nloc in self.files.items():
            count[path] = nloc[-1]

        return count

    def max(self):
        """
        Return the maximum nloc for each modified file.
        :return: int max nloc
        """
        max_count = dict()
        for path, nloc in self.files.items():
            max_count[path] = max(nloc)

        return max_count

    def avg(self):
        """
        Return the average complexity for each modified file.
        :return: int avg complexity rounded off to the nearest integer
        """
        avg_count = dict()
        for path, nloc in self.files.items():
            avg_count[path] = round(statistics.mean(nloc))
        return avg_count
    def sumC(self):
        sum_count = dict()
        for path, nloc in self.files.items():
            sum_count[path] = sum(nloc)
        return sum_count


import datetime as dt

dt1 = dt.datetime(2020, 1, 1, 0, 0)
dt2 = dt.datetime(2020, 5, 23, 0, 0)

measure = Complexity(path_to_repo='https://github.com/eclipse/eclipse.jdt.core',
                     since=dt1,
                     to=dt2).count()
measure2 = CodeChurn(path_to_repo='https://github.com/eclipse/eclipse.jdt.core',
                     since=dt1,
                     to=dt2).count()
measure3 = NLOC(path_to_repo='https://github.com/eclipse/eclipse.jdt.core',
                      since=dt1,
                      to=dt2).count()
measure4 = NLOC(path_to_repo='https://github.com/eclipse/eclipse.jdt.core',
                      since=dt1,
                      to=dt2).sumC()

fileData = open("/FileMetrics.txt", "w")
for file in measure:
    values = str(measure[file]) + '/\\' + str(measure2[file]) + '/\\' +\
             str(measure3[file]) + '/\\' + str(measure4[file])
    fileData.write(str(file) + '/\\' + values + '\n')
fileData.close()

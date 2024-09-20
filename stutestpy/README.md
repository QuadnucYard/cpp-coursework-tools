# stutestpy

C++作业批处理测试工具

## Usage

见下面样例。测试用例命名规则为 `name{i}.in` 和 `name{i}.ans`。若只有一个，可省略序号。可不提供输入文件，但必须有答案文件。

## Examples

```py
from pathlib import Path

from stutestpy import (
    FindSubmissionByKeywords,
    FixedLoader,
    LineSequenceMatcher,
    LocalCompiler,
    SequenceMatchChecker,
    TestCases,
    Tester,
    TestRunner,
    WorkTree,
)

t = Tester(
    worktree=WorkTree("tmp", loader=FixedLoader([FindSubmissionByKeywords(["point"])])),
    testcases=TestCases("projects/proj14/data", "points", has_stdin=False),
    compiler=LocalCompiler(),
    runner=TestRunner(time_limit=1.0),
    checker=SequenceMatchChecker(LineSequenceMatcher),
)
t.test_many(Path("eval/proj14"))
```

```py
from pathlib import Path

from stutestpy import (
    EnsuredLoader,
    LineSequenceMatcher,
    LocalCompiler,
    SequenceMatchChecker,
    TestCases,
    Tester,
    TestRunner,
    WorkTree,
)

t = Tester(
    worktree=WorkTree(
        "tmp",
        loader=EnsuredLoader(
            ensures=[
                ("test_queue.cpp", "projects/proj14/assets/queues/test_queue.cpp"),
                ("queue.h", "projects/proj14/assets/queues/queue.h"),
            ]
        ),
    ),
    testcases=TestCases("projects/proj14/data", prefix="queue1", has_stdin=False),
    compiler=LocalCompiler(),
    runner=TestRunner(1.0),
    checker=SequenceMatchChecker(LineSequenceMatcher),
)
t.test_many(Path("eval/proj14"))

t = Tester(
    worktree=WorkTree(
        "tmp",
        loader=EnsuredLoader(
            ensures=[
                ("test_queue2.cpp", "projects/proj14/assets/queues/test_queue2.cpp"),
                ("queue.h", "projects/proj14/assets/queues/queue.h"),
            ]
        ),
    ),
    testcases=TestCases("projects/proj14/data", prefix="queue2", has_stdin=False),
    compiler=LocalCompiler(),
    runner=TestRunner(1.0),
    checker=SequenceMatchChecker(LineSequenceMatcher),
)
t.test_many(Path("eval/proj14"))
```

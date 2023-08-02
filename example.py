from dagrun import ExecTask, Graph

task1 = ExecTask("echo", ("a", "b"))
task2 = ExecTask("pwd", ())
task3 = ExecTask("sh", ("-c", "head -c5 </dev/urandom | wc -c"))
task4 = ExecTask("echo", ("done",))

graph = Graph.build([
    # (task1, []),
    (task2, [task1]),
    (task3, [task1]),
    (task4, [task2, task3]),
])

from dagrun import ExecTask, Graph

# TODO: Prevent run of dependent if dependency fails. Useful here to add an existence
# check before pushing..

# add_origin = ExecTask("git", ["remote", "add", "origin", "git@git.sr.ht:~wintershadows/dagrun.py"])
# add_gh_mirror = ExecTask("git", ["remote", "add", "..."])

push_origin = ExecTask("git", ["push", "origin"])
push_gh_mirror = ExecTask("git", ["push", "github-mirror"])

graph = Graph.build([
    # (push_origin, [add_origin]),
    # (push_gh_mirror, [add_gh_mirror]),
    (push_origin, []),
    (push_gh_mirror, []),
])

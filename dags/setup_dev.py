from dagrun import ExecTask, Graph

create_venv = ExecTask("python", ["-m", "venv", ".venv"])
update_pip = ExecTask(".venv/bin/python", ["-m", "pip", "install", "-U", "pip"])
install_dev_deps = ExecTask(".venv/bin/pip", ["install", "-r", "requirements-dev.txt"])
install_editable = ExecTask(".venv/bin/pip", ["install", "-e", "."])

graph = Graph.build([
    create_venv,
    (update_pip, [create_venv]),
    (install_dev_deps, [update_pip]),
    (install_editable, [update_pip]),
])

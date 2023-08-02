r"""Task runner DAG framework

Copyright 2023 Gregory Werbin

Permission to use, copy, modify, and/or distribute this software for any purpose with or
without fee is hereby granted, provided that the above copyright notice and this
permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO
THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO
EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL
DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER
IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
"""

from __future__ import annotations
import subprocess
import sys
from argparse import ArgumentParser
from collections.abc import Collection, Hashable, Mapping, MutableSet, Sequence, Set
from dataclasses import dataclass
from graphlib import TopologicalSorter
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING
from typing import Protocol, Union, runtime_checkable
if TYPE_CHECKING:
    from typing import Any, Self, TypeAlias


SystemCommand: TypeAlias = str
SystemArgument: TypeAlias = str


class TaskFailed(RuntimeError):
    pass


@runtime_checkable
class SimpleTask(Protocol, Hashable):
    r"""A task that runs synchronously to completion."""

    def run(self) -> Any: ...

@dataclass(frozen=True)
class ShellTask:
    script: str
    shell: SystemCommand | None = None
    shell_args: Sequence[SystemArgument] = ()

    def run(self) -> subprocess.CompletedProcess[Any]:
        if self.shell is None:
            cproc = subprocess.run(self.script, shell=True)
        else:
            cproc = subprocess.run([self.shell, *self.shell_args, self.script])
        if cproc.returncode != 0:
            raise TaskFailed(f"{self}: failed with return code {cproc.returncode}")
        return cproc


@dataclass(frozen=True)
class ExecTask:
    command: SystemCommand
    arguments: Sequence[SystemArgument]

    def run(self) -> subprocess.CompletedProcess[Any]:
        cproc = subprocess.run([self.command, *self.arguments])
        if cproc.returncode != 0:
            raise TaskFailed(f"{self}: failed with return code {cproc.returncode}")
        return cproc

    def __hash__(self) -> int:
        # Based on the default:
        # • https://github.com/python/cpython/blob/d2340ef25721b6a72d45d4508c672c4be38c67d3/Lib/dataclasses.py#L401-L410
        return hash((self.command, tuple(self.arguments)))


@dataclass(frozen=True)
class GraphNode:
    task: SimpleTask
    dependencies: Set[SimpleTask]


GraphNodeSpec: TypeAlias = Union[SimpleTask, tuple[SimpleTask, Collection[SimpleTask]]]


@dataclass()
class Graph:
    nodes: MutableSet[GraphNode]

    def _to_graphlib(self) -> Mapping[SimpleTask, Set[SimpleTask]]:
        return {node.task: set(node.dependencies) for node in self.nodes}

    def topological_sort(self) -> Sequence[SimpleTask]:
        ts = TopologicalSorter(self._to_graphlib())
        return list(ts.static_order())

    @classmethod
    def build(cls, node_specs: Collection[GraphNodeSpec]) -> Self:
        nodes: set[GraphNode] = set()
        for node_spec in node_specs:
            if isinstance(node_spec, SimpleTask):
                task = node_spec
                nodes.add(GraphNode(task, frozenset()))
            else:
                task, deps = node_spec
                nodes.add(GraphNode(task, frozenset(deps)))
            # match node_spec:
            #     case SimpleTask() as task:
            #         nodes.add(GraphNode(task, frozenset()))
            #     case [task, deps]:
            #         nodes.add(GraphNode(task, frozenset(deps)))
        return cls(nodes=nodes)


def load_module_from_file(name: str, location: Path) -> ModuleType:
    r"""Load a module from a given file on disk."""

    loader = SourceFileLoader(name, str(location))

    spec = spec_from_file_location(name, loader=loader)
    # It looks like `spec` and `spec.loader` will only be `None` in a situation that does not apply here:
    # https://github.com/python/cpython/blob/d2340ef25721b6a72d45d4508c672c4be38c67d3/Lib/importlib/_bootstrap_external.py#L778
    # TODO: Verify that this is safe.
    assert spec is not None
    assert spec.loader is not None

    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def main() -> int | None:
    arg_parser = ArgumentParser()
    arg_parser.add_argument("-f", "--file", default=Path("dag.py"), type=Path, help="The file where the DAG is defined. Default is ./dag.py")
    arg_parser.add_argument("-n", "--no-run", dest="run", action="store_false", default=True, help="If set, print the tasks to be executed and exit without running anything.")
    cli_args = arg_parser.parse_args()

    graph_module = load_module_from_file("graph", cli_args.file)
    graph = graph_module.graph
    for node in graph.topological_sort():
        print(node, flush=True)
        if cli_args.run:
            node.run()

    return None


if __name__ == "__main__":
    sys.exit(main())

"""FreshForge provider for the repository's calibration scripts.

The provider exposes one executable node type, ``native_script``. A workflow
declares a script path and an argument list; the node runs that script from the
workflow work directory and returns its streams and artifacts. This is a
domain adapter for FRESH calibration scripts, not a generic shell node.
"""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

from freshforge.execution import RunContext
from freshforge.providers import NodeTypeMetadata, ProviderMetadata
from freshforge.records import (
    Diagnostic,
    DiagnosticSeverity,
    ProviderRunResult,
    RunStatus,
    WorkflowNode,
)

__all__ = ["NativeScriptProvider", "provider"]

NODE_TYPES: tuple[NodeTypeMetadata, ...] = (
    NodeTypeMetadata(
        id="native_script",
        name="Run a repository calibration script",
        description=(
            "Run a Python script with explicit arguments from the workflow work directory. "
            "The provider records stdout, stderr, return code, and declared artifacts."
        ),
        parameters=("script", "args"),
    ),
)


class NativeScriptProvider:
    """Execute a declared Python script as one FreshForge node."""

    def metadata(self) -> ProviderMetadata:
        """Return the provider's node types.

        Returns
        -------
        ProviderMetadata
            The provider identity, version, and executable node type.
        """
        return ProviderMetadata(
            id="fresh_fvsbc.freshforge",
            version="0.1.0",
            name="fresh-fvsbc calibration scripts",
            description="FreshForge adapter for the repository's reproducible calibration scripts.",
            node_types=NODE_TYPES,
        )

    def validate_node(
        self,
        node: WorkflowNode,
        node_type: NodeTypeMetadata,
        *,
        location: str,
    ) -> Sequence[Diagnostic]:
        """Check the script and argument types without executing anything.

        Parameters
        ----------
        node : WorkflowNode
            The node declaration to validate.
        node_type : NodeTypeMetadata
            The provider metadata for this node type.
        location : str
            Dotted workflow location used in diagnostics.

        Returns
        -------
        Sequence of Diagnostic
            Validation diagnostics; empty when the node is usable.
        """
        diagnostics: list[Diagnostic] = []
        script = node.parameters.get("script")
        if not isinstance(script, str) or not script.strip():
            diagnostics.append(
                Diagnostic(
                    severity=DiagnosticSeverity.ERROR,
                    code="node.parameter.invalid",
                    message='"script" must be a non-empty relative or absolute path.',
                    location=f"{location}.parameters.script",
                )
            )
        args = node.parameters.get("args", [])
        if not isinstance(args, list) or not all(
            isinstance(argument, (str, int, float)) for argument in args
        ):
            diagnostics.append(
                Diagnostic(
                    severity=DiagnosticSeverity.ERROR,
                    code="node.parameter.invalid",
                    message='"args" must be a list of strings or numbers.',
                    location=f"{location}.parameters.args",
                )
            )
        return diagnostics

    def run_node(
        self,
        node: WorkflowNode,
        node_type: NodeTypeMetadata,
        *,
        context: RunContext,
    ) -> ProviderRunResult:
        """Run the declared script and return its process result.

        Parameters
        ----------
        node : WorkflowNode
            The node whose ``script`` and ``args`` parameters to run.
        node_type : NodeTypeMetadata
            The provider metadata for this node type.
        context : RunContext
            The FreshForge run context and resolved work directory.

        Returns
        -------
        ProviderRunResult
            Process status, streams, return code, and declared artifacts.
        """
        del node_type
        script = Path(str(node.parameters["script"]))
        args = [str(argument) for argument in node.parameters.get("args", [])]
        script_path = context.resolve_path(script)
        if not script_path.is_file():
            return ProviderRunResult(
                status=RunStatus.FAILED,
                diagnostics=(
                    Diagnostic(
                        severity=DiagnosticSeverity.ERROR,
                        code="node.script.missing",
                        message=f"Script not found: {script_path}",
                        location=f"nodes.{node.id}.parameters.script",
                    ),
                ),
            )

        environment = os.environ.copy()
        python_path = environment.get("PYTHONPATH", "")
        parts = [str(context.workdir / "src"), str(context.workdir / "scripts")]
        if python_path:
            parts.append(python_path)
        environment["PYTHONPATH"] = os.pathsep.join(parts)
        completed = subprocess.run(
            [sys.executable, str(script_path), *args],
            cwd=context.workdir,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        artifacts: dict[str, str] = {}
        if isinstance(node.artifacts, dict):
            for name, value in node.artifacts.items():
                artifacts[str(name)] = str(context.resolve_path(str(value)))
        diagnostics: tuple[Diagnostic, ...] = ()
        status = RunStatus.SUCCESS if completed.returncode == 0 else RunStatus.FAILED
        if completed.returncode != 0:
            diagnostics = (
                Diagnostic(
                    severity=DiagnosticSeverity.ERROR,
                    code="node.script.failed",
                    message=f"Script exited with code {completed.returncode}.",
                    location=f"nodes.{node.id}",
                ),
            )
        return ProviderRunResult(
            status=status,
            outputs={"stdout": completed.stdout, "stderr": completed.stderr},
            artifacts=artifacts,
            diagnostics=diagnostics,
            data={
                "script": str(script),
                "args": args,
                "returncode": completed.returncode,
            },
        )


def provider() -> NativeScriptProvider:
    """Return the FreshForge provider for entry-point discovery.

    Returns
    -------
    NativeScriptProvider
        A provider instance for the ``freshforge.providers`` entry point.
    """
    return NativeScriptProvider()

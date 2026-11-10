"""Tests for the optional FreshForge calibration provider."""

from __future__ import annotations

from pathlib import Path

import pytest

freshforge = pytest.importorskip("freshforge")
from freshforge.execution import RunContext  # noqa: E402
from freshforge.records import RunStatus, WorkflowNode  # noqa: E402

from fresh_fvsbc.freshforge import NativeScriptProvider  # noqa: E402


def test_the_provider_declares_the_script_node() -> None:
    """The provider metadata names the executable node type."""
    provider = NativeScriptProvider()
    metadata = provider.metadata()
    assert metadata.id == "fresh_fvsbc.freshforge"
    assert [node.id for node in metadata.node_types] == ["native_script"]


def test_the_provider_runs_a_script_in_the_workdir(tmp_path: Path) -> None:
    """The node runs the declared script and returns its artifacts."""
    script = tmp_path / "write.py"
    script.write_text("from pathlib import Path\nPath('result.txt').write_text('ok')\n")
    node = WorkflowNode(
        id="write",
        provider="fresh_fvsbc.freshforge.native_script",
        parameters={"script": "write.py", "args": []},
        artifacts={"result": "result.txt"},
    )
    provider = NativeScriptProvider()
    result = provider.run_node(
        node,
        provider.metadata().node_types[0],
        context=RunContext(workflow_id="test", workdir=tmp_path),
    )
    assert result.status is RunStatus.SUCCESS
    assert (tmp_path / "result.txt").read_text() == "ok"
    assert result.artifacts["result"] == str(tmp_path / "result.txt")
    assert result.data["returncode"] == 0


def test_the_provider_reports_a_missing_script(tmp_path: Path) -> None:
    """A missing script fails with a diagnostic instead of raising."""
    node = WorkflowNode(
        id="missing",
        provider="fresh_fvsbc.freshforge.native_script",
        parameters={"script": "absent.py", "args": []},
    )
    result = NativeScriptProvider().run_node(
        node,
        NativeScriptProvider().metadata().node_types[0],
        context=RunContext(workflow_id="test", workdir=tmp_path),
    )
    assert result.status is RunStatus.FAILED
    assert result.diagnostics[0].code == "node.script.missing"


def test_the_provider_validates_script_and_args(tmp_path: Path) -> None:
    """Bad parameter types produce scoped diagnostics."""
    provider = NativeScriptProvider()
    node = WorkflowNode(
        id="invalid",
        provider="fresh_fvsbc.freshforge.native_script",
        parameters={"script": 3, "args": "not-a-list"},
    )
    diagnostics = provider.validate_node(
        node,
        provider.metadata().node_types[0],
        location="nodes.invalid",
    )
    assert {diagnostic.code for diagnostic in diagnostics} == {"node.parameter.invalid"}


def test_the_provider_reports_a_failed_script(tmp_path: Path) -> None:
    """A non-zero exit becomes a failed node with one diagnostic."""
    script = tmp_path / "fail.py"
    script.write_text("raise SystemExit(2)\n")
    node = WorkflowNode(
        id="fail",
        provider="fresh_fvsbc.freshforge.native_script",
        parameters={"script": "fail.py", "args": []},
    )
    result = NativeScriptProvider().run_node(
        node,
        NativeScriptProvider().metadata().node_types[0],
        context=RunContext(workflow_id="test", workdir=tmp_path),
    )
    assert result.status is RunStatus.FAILED
    assert result.data["returncode"] == 2
    assert result.diagnostics[0].code == "node.script.failed"


def test_the_quesnel_workflow_validates_with_the_provider() -> None:
    """The checked-in Quesnel workflow resolves both native-script nodes."""
    from freshforge.loading import load_workflow
    from freshforge.providers import ProviderRegistry
    from freshforge.validation import validate_workflow_with_providers

    spec, diagnostics = load_workflow("workflows/freshforge/quesnel_background.yaml")
    assert spec is not None
    registry = ProviderRegistry()
    registry.register(NativeScriptProvider())
    errors = validate_workflow_with_providers(
        spec, registry=registry, structural_diagnostics=diagnostics
    )
    assert [
        diagnostic for diagnostic in errors if diagnostic.code.startswith("node.provider")
    ] == []
    assert [node.id for node in spec.nodes] == [
        "fit_provincial",
        "calibrate_quesnel",
        "freeze_model",
    ]


def test_the_okanagan_workflow_validates_with_the_provider() -> None:
    """The checked-in Okanagan workflow resolves its native-script node."""
    from freshforge.loading import load_workflow
    from freshforge.providers import ProviderRegistry
    from freshforge.validation import validate_workflow_with_providers

    spec, diagnostics = load_workflow("workflows/freshforge/okanagan_background.yaml")
    assert spec is not None
    registry = ProviderRegistry()
    registry.register(NativeScriptProvider())
    errors = validate_workflow_with_providers(
        spec, registry=registry, structural_diagnostics=diagnostics
    )
    assert [
        diagnostic for diagnostic in errors if diagnostic.code.startswith("node.provider")
    ] == []
    assert [node.id for node in spec.nodes] == ["fit_and_freeze_okanagan"]


def test_the_north_island_workflow_validates_with_the_provider() -> None:
    """The checked-in North Island workflow resolves its native-script node."""
    from freshforge.loading import load_workflow
    from freshforge.providers import ProviderRegistry
    from freshforge.validation import validate_workflow_with_providers

    spec, diagnostics = load_workflow("workflows/freshforge/north_island_background.yaml")
    assert spec is not None
    registry = ProviderRegistry()
    registry.register(NativeScriptProvider())
    errors = validate_workflow_with_providers(
        spec, registry=registry, structural_diagnostics=diagnostics
    )
    assert [
        diagnostic for diagnostic in errors if diagnostic.code.startswith("node.provider")
    ] == []
    assert [node.id for node in spec.nodes] == ["fit_and_freeze_north_island"]


def test_the_kamloops_workflow_validates_with_the_provider() -> None:
    """The checked-in Kamloops workflow resolves its native-script node."""
    from freshforge.loading import load_workflow
    from freshforge.providers import ProviderRegistry
    from freshforge.validation import validate_workflow_with_providers

    spec, diagnostics = load_workflow("workflows/freshforge/kamloops_background.yaml")
    assert spec is not None
    registry = ProviderRegistry()
    registry.register(NativeScriptProvider())
    errors = validate_workflow_with_providers(
        spec, registry=registry, structural_diagnostics=diagnostics
    )
    assert [
        diagnostic for diagnostic in errors if diagnostic.code.startswith("node.provider")
    ] == []
    assert [node.id for node in spec.nodes] == ["fit_and_freeze_kamloops"]


def test_the_prince_george_workflow_validates_with_the_provider() -> None:
    """The checked-in Prince George workflow resolves its native-script node."""
    from freshforge.loading import load_workflow
    from freshforge.providers import ProviderRegistry
    from freshforge.validation import validate_workflow_with_providers

    spec, diagnostics = load_workflow("workflows/freshforge/prince_george_background.yaml")
    assert spec is not None
    registry = ProviderRegistry()
    registry.register(NativeScriptProvider())
    errors = validate_workflow_with_providers(
        spec, registry=registry, structural_diagnostics=diagnostics
    )
    assert [
        diagnostic for diagnostic in errors if diagnostic.code.startswith("node.provider")
    ] == []
    assert [node.id for node in spec.nodes] == ["fit_and_freeze_prince_george"]


def test_the_cranbrook_workflow_validates_with_the_provider() -> None:
    """The checked-in Cranbrook workflow resolves its native-script node."""
    from freshforge.loading import load_workflow
    from freshforge.providers import ProviderRegistry
    from freshforge.validation import validate_workflow_with_providers

    spec, diagnostics = load_workflow("workflows/freshforge/cranbrook_background.yaml")
    assert spec is not None
    registry = ProviderRegistry()
    registry.register(NativeScriptProvider())
    errors = validate_workflow_with_providers(
        spec, registry=registry, structural_diagnostics=diagnostics
    )
    assert [
        diagnostic for diagnostic in errors if diagnostic.code.startswith("node.provider")
    ] == []
    assert [node.id for node in spec.nodes] == ["fit_and_freeze_cranbrook"]


def test_the_arrow_workflow_validates_with_the_provider() -> None:
    """The checked-in Arrow workflow resolves its native-script node."""
    from freshforge.loading import load_workflow
    from freshforge.providers import ProviderRegistry
    from freshforge.validation import validate_workflow_with_providers

    spec, diagnostics = load_workflow("workflows/freshforge/arrow_background.yaml")
    assert spec is not None
    registry = ProviderRegistry()
    registry.register(NativeScriptProvider())
    errors = validate_workflow_with_providers(
        spec, registry=registry, structural_diagnostics=diagnostics
    )
    assert [
        diagnostic for diagnostic in errors if diagnostic.code.startswith("node.provider")
    ] == []
    assert [node.id for node in spec.nodes] == ["fit_and_freeze_arrow"]


def test_the_fraser_workflow_validates_with_the_provider() -> None:
    """The checked-in Fraser workflow resolves its native-script node."""
    from freshforge.loading import load_workflow
    from freshforge.providers import ProviderRegistry
    from freshforge.validation import validate_workflow_with_providers

    spec, diagnostics = load_workflow("workflows/freshforge/fraser_background.yaml")
    assert spec is not None
    registry = ProviderRegistry()
    registry.register(NativeScriptProvider())
    errors = validate_workflow_with_providers(
        spec, registry=registry, structural_diagnostics=diagnostics
    )
    assert [
        diagnostic for diagnostic in errors if diagnostic.code.startswith("node.provider")
    ] == []
    assert [node.id for node in spec.nodes] == ["fit_and_freeze_fraser"]


def test_the_mackenzie_workflow_validates_with_the_provider() -> None:
    """The checked-in MacKenzie workflow resolves its native-script node."""
    from freshforge.loading import load_workflow
    from freshforge.providers import ProviderRegistry
    from freshforge.validation import validate_workflow_with_providers

    spec, diagnostics = load_workflow("workflows/freshforge/mackenzie_background.yaml")
    assert spec is not None
    registry = ProviderRegistry()
    registry.register(NativeScriptProvider())
    errors = validate_workflow_with_providers(
        spec, registry=registry, structural_diagnostics=diagnostics
    )
    assert [
        diagnostic for diagnostic in errors if diagnostic.code.startswith("node.provider")
    ] == []
    assert [node.id for node in spec.nodes] == ["fit_and_freeze_mackenzie"]


def test_the_haida_gwaii_workflow_validates_with_the_provider() -> None:
    """The checked-in Haida Gwaii workflow resolves its native-script node."""
    from freshforge.loading import load_workflow
    from freshforge.providers import ProviderRegistry
    from freshforge.validation import validate_workflow_with_providers

    spec, diagnostics = load_workflow("workflows/freshforge/haida_gwaii_background.yaml")
    assert spec is not None
    registry = ProviderRegistry()
    registry.register(NativeScriptProvider())
    errors = validate_workflow_with_providers(
        spec, registry=registry, structural_diagnostics=diagnostics
    )
    assert [
        diagnostic for diagnostic in errors if diagnostic.code.startswith("node.provider")
    ] == []
    assert [node.id for node in spec.nodes] == ["fit_and_freeze_haida_gwaii"]


def test_the_kootenay_lake_workflow_validates_with_the_provider() -> None:
    """The checked-in Kootenay Lake workflow resolves its native-script node."""
    from freshforge.loading import load_workflow
    from freshforge.providers import ProviderRegistry
    from freshforge.validation import validate_workflow_with_providers

    spec, diagnostics = load_workflow("workflows/freshforge/kootenay_lake_background.yaml")
    assert spec is not None
    registry = ProviderRegistry()
    registry.register(NativeScriptProvider())
    errors = validate_workflow_with_providers(
        spec, registry=registry, structural_diagnostics=diagnostics
    )
    assert [
        diagnostic for diagnostic in errors if diagnostic.code.startswith("node.provider")
    ] == []
    assert [node.id for node in spec.nodes] == ["fit_and_freeze_kootenay_lake"]


def test_the_boundary_workflow_validates_with_the_provider() -> None:
    """The checked-in Boundary workflow resolves its native-script node."""
    from freshforge.loading import load_workflow
    from freshforge.providers import ProviderRegistry
    from freshforge.validation import validate_workflow_with_providers

    spec, diagnostics = load_workflow("workflows/freshforge/boundary_background.yaml")
    assert spec is not None
    registry = ProviderRegistry()
    registry.register(NativeScriptProvider())
    errors = validate_workflow_with_providers(
        spec, registry=registry, structural_diagnostics=diagnostics
    )
    assert [
        diagnostic for diagnostic in errors if diagnostic.code.startswith("node.provider")
    ] == []
    assert [node.id for node in spec.nodes] == ["fit_and_freeze_boundary"]


def test_the_symmetric_audit_workflow_validates_with_the_provider() -> None:
    """The checked-in symmetric audit workflow resolves its native-script node."""
    from freshforge.loading import load_workflow
    from freshforge.providers import ProviderRegistry
    from freshforge.validation import validate_workflow_with_providers

    spec, diagnostics = load_workflow("workflows/freshforge/symmetric_audit.yaml")
    assert spec is not None
    registry = ProviderRegistry()
    registry.register(NativeScriptProvider())
    errors = validate_workflow_with_providers(
        spec, registry=registry, structural_diagnostics=diagnostics
    )
    assert [
        diagnostic for diagnostic in errors if diagnostic.code.startswith("node.provider")
    ] == []
    assert [node.id for node in spec.nodes] == ["run_audit"]


def test_the_calibration_policy_workflow_validates_with_the_provider() -> None:
    """The checked-in calibration policy workflow resolves its node."""
    from freshforge.loading import load_workflow
    from freshforge.providers import ProviderRegistry
    from freshforge.validation import validate_workflow_with_providers

    spec, diagnostics = load_workflow("workflows/freshforge/calibration_policy.yaml")
    assert spec is not None
    registry = ProviderRegistry()
    registry.register(NativeScriptProvider())
    errors = validate_workflow_with_providers(
        spec, registry=registry, structural_diagnostics=diagnostics
    )
    assert [
        diagnostic for diagnostic in errors if diagnostic.code.startswith("node.provider")
    ] == []
    assert [node.id for node in spec.nodes] == ["check_policy"]


def test_the_candidate_registry_workflow_validates_with_the_provider() -> None:
    """The checked-in candidate registry workflow resolves its node."""
    from freshforge.loading import load_workflow
    from freshforge.providers import ProviderRegistry
    from freshforge.validation import validate_workflow_with_providers

    spec, diagnostics = load_workflow("workflows/freshforge/candidate_registry.yaml")
    assert spec is not None
    registry = ProviderRegistry()
    registry.register(NativeScriptProvider())
    errors = validate_workflow_with_providers(
        spec, registry=registry, structural_diagnostics=diagnostics
    )
    assert [
        diagnostic for diagnostic in errors if diagnostic.code.startswith("node.provider")
    ] == []
    assert [node.id for node in spec.nodes] == ["check_registry"]


def test_the_deployment_calibration_workflow_validates_with_the_provider() -> None:
    """The checked-in deployment calibration workflow resolves its node."""
    from freshforge.loading import load_workflow
    from freshforge.providers import ProviderRegistry
    from freshforge.validation import validate_workflow_with_providers

    spec, diagnostics = load_workflow("workflows/freshforge/deployment_calibration.yaml")
    assert spec is not None
    registry = ProviderRegistry()
    registry.register(NativeScriptProvider())
    errors = validate_workflow_with_providers(
        spec, registry=registry, structural_diagnostics=diagnostics
    )
    assert [
        diagnostic for diagnostic in errors if diagnostic.code.startswith("node.provider")
    ] == []
    assert [node.id for node in spec.nodes] == ["estimate_offsets"]


def test_the_score_inventory_workflow_validates_with_the_provider() -> None:
    """The checked-in raw scoring workflow resolves its node."""
    from freshforge.loading import load_workflow
    from freshforge.providers import ProviderRegistry
    from freshforge.validation import validate_workflow_with_providers

    spec, diagnostics = load_workflow("workflows/freshforge/score_inventory.yaml")
    assert spec is not None
    registry = ProviderRegistry()
    registry.register(NativeScriptProvider())
    errors = validate_workflow_with_providers(
        spec, registry=registry, structural_diagnostics=diagnostics
    )
    assert [
        diagnostic for diagnostic in errors if diagnostic.code.startswith("node.provider")
    ] == []
    assert [node.id for node in spec.nodes] == ["score_rows"]


def test_the_tsa_sweep_workflow_validates_with_the_provider() -> None:
    """The checked-in TSA sweep workflow resolves its node."""
    from freshforge.loading import load_workflow
    from freshforge.providers import ProviderRegistry
    from freshforge.validation import validate_workflow_with_providers

    spec, diagnostics = load_workflow("workflows/freshforge/tsa_sweep.yaml")
    assert spec is not None
    registry = ProviderRegistry()
    registry.register(NativeScriptProvider())
    errors = validate_workflow_with_providers(
        spec, registry=registry, structural_diagnostics=diagnostics
    )
    assert [
        diagnostic for diagnostic in errors if diagnostic.code.startswith("node.provider")
    ] == []
    assert [node.id for node in spec.nodes] == ["run_sweep"]


def test_the_all_tsa_cards_workflow_validates_with_the_provider() -> None:
    """The checked-in all-TSA card workflow resolves both nodes."""
    from freshforge.loading import load_workflow
    from freshforge.providers import ProviderRegistry
    from freshforge.validation import validate_workflow_with_providers

    spec, diagnostics = load_workflow("workflows/freshforge/all_tsa_cards.yaml")
    assert spec is not None
    registry = ProviderRegistry()
    registry.register(NativeScriptProvider())
    errors = validate_workflow_with_providers(
        spec, registry=registry, structural_diagnostics=diagnostics
    )
    assert [
        diagnostic for diagnostic in errors if diagnostic.code.startswith("node.provider")
    ] == []
    assert [node.id for node in spec.nodes] == ["freeze_missing", "rebuild_registry"]


def test_the_mpb_segment_workflow_validates_with_the_provider() -> None:
    """The checked-in MPB segment workflow resolves its native-script node."""
    from freshforge.loading import load_workflow
    from freshforge.providers import ProviderRegistry
    from freshforge.validation import validate_workflow_with_providers

    spec, diagnostics = load_workflow("workflows/freshforge/quesnel_mpb_segment.yaml")
    assert spec is not None
    registry = ProviderRegistry()
    registry.register(NativeScriptProvider())
    errors = validate_workflow_with_providers(
        spec, registry=registry, structural_diagnostics=diagnostics
    )
    assert [
        diagnostic for diagnostic in errors if diagnostic.code.startswith("node.provider")
    ] == []
    assert [node.id for node in spec.nodes] == ["run_segment", "freeze_boundary"]
    assert spec.nodes[0].parameters["args"] == [
        "--case",
        "runtime/mpb-case.json",
        "--output",
        "runtime/quesnel-mpb-segment.json",
    ]

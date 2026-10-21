Provenance contract
===================

What `fvsbc` records for every run, so that a number in a paper can be traced to what produced it.

This contract is `fvsbc`'s own design. It is not read from FVS. The three external facts it depends on
are verified: FVS writes the variant and version into `FVS_Cases` (see :doc:`outputs`); the keyword file
name is recorded there too; and the build's inputs are pinned (see ADR 0001).

Why it exists
-------------

The project's users include reviewers and readers of published results, who need to know which variant,
which source revision, and which keyword set produced a number. `notes/scope.md` names that need, and
`AGENTS.md` states the rule: record the provenance of every run.

What a run records
------------------

A record has these fields.

.. list-table::
   :header-rows: 1
   :widths: 26 74

   * - Field
     - What it is
   * - ``fvsbc_version``
     - The `fvsbc` version that ran
   * - ``pyfvs_commit``
     - The commit of the pinned `UBC-FRESH/PyFVS` fork
   * - ``fvs_source_commit``
     - The commit of the FVS source submodule that the fork pins
   * - ``variant``
     - The variant built and run, which for this project is ``bc``
   * - ``variant_list``
     - The full variant list the build produced, so a mistaken build is visible
   * - ``keyword_set_hash``
     - A hash of the keyword set, canonically serialized
   * - ``treelist_hash``
     - A hash of the tree-list input, canonically serialized
   * - ``case_id``
     - The ``CaseID`` from ``FVS_Cases``
   * - ``run_datetime``
     - The ``RunDateTime`` from ``FVS_Cases``
   * - ``random_seed``
     - The seed, when the run used one. FVS exposes ``RANNSEED``

The two hashes are of a canonical serialization, not of a file. A file hash changes with a trailing
newline or a column width, and it would then say a run differed when it did not.

Where it lives
--------------

- In memory, on the result object that a run returns.
- On disk beside the outputs, as JSON, when the caller asks for it.
- In the changelog or the close-out report, only as a citation. A raw record does not belong in a
  tracked file when it names a local path.

Contract rules
--------------

1. A run that cannot record its provenance is a failure. Provenance is not optional, and it is not
   added afterwards.
2. The record names commits, not versions, for the two pinned inputs. A version can be republished; a
   commit cannot.
3. ``variant_list`` is recorded even though the project builds one variant, because a build that quietly
   produced a different variant is a real failure mode and this is what makes it visible.
4. The record carries no credential, no personal path, and no raw data. `AGENTS.md` states the rule, and
   `scripts/check_workflow.py` rejects the mechanical cases.

Not verified
------------

- Whether PyFVS exposes the built variant list at run time, or whether `fvsbc` must read it from the
  build.
- Whether `RANNSEED` is the only source of nondeterminism, or whether FVS has others.

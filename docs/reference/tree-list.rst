Tree-list input contract
========================

What `fvsbc` must write for FVS-BC to read a stand, and what it must therefore accept from a caller.

Read at: `forest-modeling/ForestVegetationSimulator`, branch `pyfvs-features`, commit `ef5fa84`.

The record format
-----------------

FVS-BC's tree-record format is `TREFMT`, a default that the variant supplies. It is defined in
`canada/bc/blkdat.f`, in `BLOCK DATA BLKDAT`, at lines 37 to 39:

.. code-block:: fortran

      DATA TREFMT /
     >'(I4,T1,I7,F6.0,I1,A3,F5.1,F4.1,2F5.1,F5.1,I1,3(I2,I2),2I1,I2,2I3,
     >2I1,F3.0)' /

`canada/bc/blkdat.f` is in the BC build: `bin/FVSbc_sourceList.txt`, line 55.

The fields, in order
--------------------

The format string gives the width and the type of each field. The names come from the corresponding
Python template in PyFVS, `src/pyfvs/config_default.yaml`, which is the only field-by-field naming of
this record that was found.

.. list-table::
   :header-rows: 1
   :widths: 8 14 22 56

   * - Order
     - FVS edit
     - Field
     - Notes
   * - 1
     - ``I4``
     - ``plot_id``
     - Integer, width 4
   * - 2
     - ``T1``
     - —
     - A tab to column 6
   * - 3
     - ``I7``
     - ``tree_num``
     - Integer, width 7
   * - 4
     - ``F6.0``
     - ``tree_count``
     - Real, width 6, no decimals. The tree's expansion factor
   * - 5
     - ``I1``
     - ``tree_history``
     - Integer, width 1
   * - 6
     - ``A3``
     - ``species``
     - **Character, width 3.** See the species section below
   * - 7
     - ``F5.1``
     - ``diam``
     - Diameter at breast height, width 5, one decimal
   * - 8
     - ``F4.1``
     - ``dg_incr``
     - Diameter growth, width 4, one decimal
   * - 9
     - ``2F5.1``
     - ``live_ht``, ``trunc_ht``
     - Two real fields, width 5, one decimal
   * - 10
     - ``F5.1``
     - ``htg_incr``
     - Height growth, width 5, one decimal
   * - 11
     - ``I1``
     - ``crown_ratio``
     - Integer, width 1
   * - 12
     - ``3(I2,I2)``
     - ``damage1``/``severity1``, then 2 and 3
     - Three damage codes, each with a severity, all width 2
   * - 13
     - ``2I1``
     - ``tree_val``, ``tree_rx``
     - Two integers, width 1
   * - 14
     - ``I2``
     - ``plot_slope``
     - Integer, width 2
   * - 15
     - ``2I3``
     - ``plot_aspect``, ``plot_habitat``
     - Two integers, width 3
   * - 16
     - ``2I1``
     - ``plot_topo_pos``, ``plot_site_prep``
     - Two integers, width 1
   * - 17
     - ``F3.0``
     - ``tree_age``
     - Real, width 3, no decimals

Not verified: whether the BC variant reads the same field order as PyFVS's template, since only the BC
`TREFMT` widths were read and not the BC reader. The widths agree with PyFVS's template for fields 1 to 5
and 7 to 17, and differ at field 6. Confirm the reader in `P2.2`.

The species codes
-----------------

FVS-BC has 15 species. The list is `JSP` in `canada/bc/blkdat.f`, lines 74 to 76:

.. code-block:: fortran

      DATA JSP /'PW ','LW ','FD ','BG ','HW ','CW ','PL ','SE ',
     &  'BL ','PY ','EP ','AT ','AC ','OC ','OH '/

In order: ``PW``, ``LW``, ``FD``, ``BG``, ``HW``, ``CW``, ``PL``, ``SE``, ``BL``, ``PY``, ``EP``,
``AT``, ``AC``, ``OC``, ``OH``. The count matches ``PARAMETER (MAXSP =15)`` in
`canada/bc/PRGPRM.F77`, line 12.

The same file gives two parallel lists, each of 15 entries: ``FIAJSP``, the FIA numeric codes, where
``PW`` is ``119``; and ``PLNJSP``, the PLANTS symbols, where ``PW`` is ``PIMO3``. A fourth list, ``NSP``,
holds 45 names of the form ``PW1``, ``PW2``, ``PW3`` through ``OH1``, ``OH2``, ``OH3``.

Contract rules
--------------

1. `fvsbc` writes the record in one tested writer. `AGENTS.md` states the reason: the format is
   fixed-width, so formatting it at a call site is a defect.
2. The writer emits `A3` for the species field, matching `TREFMT`.
3. The writer accepts any of the three code lists for species input, and it resolves them to a `JSP`
   code before writing. A code that resolves to nothing is an error, not a default.
4. The contract names its fields by the PyFVS template names above, and it keeps the FVS edit descriptors
   beside them so a reviewer can check the widths.

The open hazard
---------------

PyFVS writes its own ``TREEFMT`` keyword when the caller's keyword set does not contain one. Its default
format is **not** the BC variant's. See :doc:`keywords`. The two differ at the species field, ``A4``
against ``A3``, and at the tree number, tree count, and height fields.

Whether that injection reaches an `FVSbc` run, and whether it misaligns a treelist, is unverified. It is
the first question for `P2.2`.

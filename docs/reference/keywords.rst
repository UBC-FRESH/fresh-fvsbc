Keyword-set contract
====================

How `fresh-fvsbc` represents, validates, and hands a keyword set to FVS-BC.

Read at: `forest-modeling/ForestVegetationSimulator`, branch `pyfvs-features`, commit `ef5fa84`.

The vocabulary
--------------

FVS matches keywords against a fixed table. The base table is `TABLE` in `base/keywds.f`, declared in
blocks of 20 and 150 slots long. It is not a per-variant list: the variant hooks into it.

The named entries, in slot order, are:

.. code-block:: text

   PROCESS TIMEINT FIXCW TREEDATA TREEFMT MPB DFTM WSBW CWEQN DESIGN NUMCYCLE TFIXAREA
   GROWTH STDINFO STDIDENT INVYEAR TREELIST REWIND NOSUM DEBUG
   ECHOSUM ADDFILE THINAUTO THINBTA THINATA THINBBA THINABA THINPRSC THINDBH xSALVAGE
   SPLABEL AGPLABEL COMPUTE FERTILIZ THINHT STATS TOPKILL HTGSTOP MCFDLN BFFDLN
   MCDEFECT BFDEFECT VOLUME BFVOLUME REGDMULT COVER ESTAB MINHARV SPECPREF SPCODES
   NODEBUG CUTEFF NOTRIPLE READCORD REUSCORD NOCALIB DGSTDEV BAIMULT MORTMULT NOHTDREG
   RANNSEED HTGMULT CHEAPO NUMTRIP ENDFILE BAMAX READCORH REUSCORH MGMTID REGHMULT
   TCONDMLT NOAUTOES READCORR REUSCORR BRUST IF SCREEN COMPRESS THEN ALSOTRY
   ENDIF NOTREES CALBSTAT OPEN CLOSE NOSCREEN RRIN FIXMORT SDIMAX DELOTAB SERLCORR
   CUTLIST RESETAGE SITECODE MISTOE CRNMULT CFVOLEQU BFVOLEQU ANIN DFB
   RDIN MANAGED YARDLOSS FMIN STRCLASS MODTYPE FVSSTAND PRUNE SVS FIXDG FIXHTG THINSDI
   LOCATE <blank> THINCC ECON DATABASE <blank> DEFECT <blank>
   STANDCN THINMIST TREESZCP THINRDEN SPGROUP BMIN DATASCRN SETPTHIN THINPT VOLEQNUM
   POINTREF ECHO NOECHO CYCLEAT ATRTLIST
   THINRDSL MORTMSB SETSITE CLIMATE SDICALC THINQFA PTGROUP ORGANON SPLEAVE CCADJ
   PRMFROST FIAVBC <blank> <blank> <blank>

Two caveats, both verified:

- One entry is misspelled upstream: ``xSALVAGE``, with a leading ``x``. A caller that writes ``SALVAGE``
  is writing a keyword the table does not hold.
- The table has blank slots. A blank slot is not a keyword.
- Matching is FVS's own. ``base/fndkey.f`` compares the caller's word with the table using FORTRAN's
  ``.EQ.`` on character strings, so the comparison is exact and case sensitive. A validator that
  accepted ``database`` would be accepting something FVS does not.

How a keyword and its parameters are laid out
---------------------------------------------

A keyword is not a name followed by tokens. ``base/keyrdr.f`` reads the keyword from the first eight
columns of a record and then reads each parameter from a **ten-column field of that same record**:

.. code-block:: fortran

   KEYWRD=RECORD(1:8)
   J=1
   DO 25 I=1,NF
   J=J+10
   KARD(I)=RECORD(J:J+9)

So the first field is columns 11 to 20, the second 21 to 30, and so on, and a parameter wider than
ten columns cannot be carried. A blank field is a field, which is why FVS's own files write
``TIMEINT`` with an empty first field before the value.

Some keywords are the exception, because they read records of their own rather than fields:

- ``STDIDENT`` takes the record after it as the stand id and title (``canada/bc/initre.f``).
- ``TREEFMT`` takes the two records after it as the format (``metric/base/intree.f``).
- ``COMMENT``, ``COMPUTE``, ``DATABASE``, ``FMIN`` and ``MISTOE`` take a **block of text lines** ended by
  ``END``.
  A caller supplies the lines and the writer supplies the terminator, because a block without one
  swallows the rest of the file. **A ``DATABASE`` block must precede the stand setup**: FVS refuses it
  later with ``FVS16 ERROR: KEYWORD ENTERED IS USED IN WRONG CONTEXT``, and the official case puts it
  first. The validator refuses a set that puts it after ``STDIDENT``, ``STDINFO`` or ``STANDSQL``.
  **``FMIN`` is how a caller asks for the fuels, potfire, carbon and consumption tables**: ``FUELOUT``,
  ``FUELREPT``, ``POTFIRE``, ``CARBREPT``, ``SIMFIRE``, ``DWDCVOUT``, ``CANFPROF`` and ``MORTREPT`` are options inside it rather
  than keywords, which is why they are not in the table. Each writes its tables only when the ``DATABASE`` block names
  the matching option — ``FuelsOut``, ``FuelReDB``, ``PotfirDB``, ``CARBREDB`` or ``BURNREDB`` — and the
  option alone is never enough for carbon or consumption: ``CARBREDB`` needs ``CARBREPT``, and
  ``BURNREDB`` needs an actual fire, which ``SIMFIRE`` schedules as activity 2506.

  **The burn report has no working path.** ``FVS_BurnReport_Metric`` is written only inside
  ``IF (IFMBRB .LT. 0)``, and ``IFMBRB`` is set to ``9999`` at initialisation and to the inventory year
  by ``BURNREPT`` — never negative unless ``INVYEAR`` is given an invalid negative year, which shifts the
  whole simulation. It is not exposed.

  **``ATRTLIST`` and ``STRCLASS`` are requests, and ``ATRTLIST`` needs a treatment.** The attribute
  list is written after a cutting operation — its writer returns unless it is called from `cuts.f` —
  so a run with no removal writes no rows even though the table exists. `STRCLASS` asks for the
  structural stage of each stratum.

  **Some tables need a request as well as an option.** ``FVS_TreeList_Metric`` needs ``TREELIDB`` in
  the ``DATABASE`` block *and* a ``TREELIST`` keyword; ``FVS_CutList_Metric`` needs ``CUTLIDB`` and
  ``CUTLIST``, and an actual removal; ``FVS_Stats_Species_Metric`` needs ``INVSTATS`` and ``STATS``.
  The option alone is accepted and writes nothing, which is the same trap ``CARBREDB`` sets.

  **The mortality table needs ``MORTREPT``, which sets ``IFMMRB`` to -1**; ``MORTREDB`` alone is accepted
  and writes nothing. That is the opposite of the burn report, whose ``BURNREPT`` sets ``IFMBRB`` to the
  inventory year, which the gate rejects — two options that look identical and behave oppositely.

  **A mistletoe rating enters through the damage columns**: damage codes **30 to 34** with the severity as
  the Hawksworth rating, per ``misdam.f``. The adapter writes zero there, so an infected stand needs a
  caller who supplies the damage fields.

  **``DESIGN``'s fourth field is the inventory point count.** ``FVS_Stats_Stand`` is the distribution
  among sample points and is written only when that count is above one; a run that leaves it at 1 writes
  the species statistics and a message saying the distribution cannot be computed.

  **``ESTAB`` is a block, and its ``NATURAL`` and ``PLANT`` lines need the stems per acre.** ``esin.f``
  refuses the line — and the whole set with it — when that field is zero. With it, the regeneration tally
  and the site-preparation table are written. **``FVS_CalibStats`` is not exposed**: the table is created
  but carries nothing unless the run is calibrated, and this package does not calibrate.

  **``MISTOE`` and ``RDIN`` are blocks, and their sub-keywords are not keywords.** ``MISTPRT`` inside
  ``MISTOE`` sets ``PRTMIS`` and ``NEWSPRED`` sets ``NEWMOD``; without them two of the four dwarf-mistletoe
  tables are never written. ``RDIN`` needs ``RRINIT`` (or ``RRTREIN``) or it refuses the whole set at its
  ``END`` with "NEITHER TREELIST OR MANUAL INITIALIZATION SPECIFIED", and ``RRDOUT`` adds the detail
  table.

  **``MISTOE`` is a block, and its sub-keywords are not keywords either.** ``MISTPINF``, ``MISTGMOD``,
  ``DMAUTO`` and the rest are options inside it, read by ``MISIN``. A run with a ``MISTOE`` block is
  accepted and the report echoes the sub-keyword, but **the dwarf-mistletoe tables do not appear**: they
  need an infection state, and a block alone does not create one. ``RDIN`` starts the equivalent block for
  root disease; its required parameters were not determined, so it is not modelled, and the root-disease
  tables are likewise unexposed.
- ``THINQFA`` carries one **supplemental record** after its keyword record. ``canada/bc/initre.f``
  option 141 reads fields 1–7 as the BDq request, then reads the next record with
  ``READ(IREAD,'(I1)')ISETQFA``. The first column selects the residual-density unit: ``0`` basal
  area per acre, ``1`` trees per acre, ``2`` stand density index. There is no ``END`` terminator.
  ``fresh-fvsbc`` takes the record as ``supplemental`` and requires exactly one of ``0``, ``1`` or
  ``2``; a missing record is refused because FVS would consume the next keyword as the unit.
- ``IF`` takes a block of **keywords** rather than lines: the condition record, ``THEN``, the body, and
  ``ENDIF``, with an optional ``ELSE`` branch. The official case's form is the one the run test checks.
  **``ALSOTRY`` is not modelled**, because no fixture here uses it.

``STOP`` is a keyword that the table does not hold. ``base/keyrdr.f`` compares each record's first
eight characters with ``STOP`` before it consults the table, and a match ends the file with code 3, so
``STOP`` is accepted and every real key file ends with it. The first version of the validator refused
it, and refused every real key file with it; the run orchestration found that the first time it wrote
one.

BC-specific input
-----------------

The BC variant adds no keyword to `base/keywds.f`. It reaches site and BEC input through the base
keywords, in `canada/bc/initre.f`:

- ``SITECODE`` is handled at option 94 of `initre.f`, from line 3347. The comment states that the site
  species comes from the first ``SITECODE`` card, and it names field 3 as the species field.
- ``SETSITE`` is in the table at slot 139.

BEC values arrive as a structured value, not as a flat code. `canada/bc/BCPLOT.F77` declares:

.. code-block:: fortran

      TYPE BEC_DESCRIPTION
        SEQUENCE
        CHARACTER (LEN=3)  :: Region     !KAM  - longest strings
        CHARACTER (LEN=4)  :: Zone       !ESSF - are shown here
        CHARACTER (LEN=3)  :: SubZone    !mw2
        CHARACTER (LEN=5)  :: Series     !01-YC
        CHARACTER (LEN=7)  :: FullName   !ICHmw2
        CHARACTER (LEN=15) :: PrettyName !IDFmw1/01-YC
      END TYPE

So a BEC value is a region, a zone, a subzone, and a series, with two derived renderings. `BECSET` in
`canada/bc/becset.f` resolves it. That file's header names the input as the ``BECINFO`` keyword, but
``BECINFO`` appears nowhere in the keyword table and nowhere in the code except two comments. It is
either a documented name for input that now arrives another way, or a stale comment.

**Answered in `P3`.** ``BECINFO`` is a **stale comment**. It appears nowhere in the keyword table and
nowhere in the code except two comments in ``canada/bc/becset.f``. ``BECSET`` is called from
``canada/bc/sitset.f``, not from the keyword reader, and it derives the BEC from the site species and the
habitat data that ``SITECODE`` supplies. So **a caller does not supply a BEC value at all** — the model
derives it — and there is no keyword to accept one. `P2.1` assigned this to `P2.2` and `P2.2` did not
discharge it; it is discharged here.

Contract rules
--------------

1. `fresh-fvsbc` represents a keyword set as an ordered sequence of keywords, each with its parameters. Order
   is significant, because FVS processes the file in order.
2. `fresh-fvsbc` validates each keyword against the table above, and it rejects an unknown keyword by name
   rather than passing it through. A pass-through would let a typo reach Fortran, which reports it
   poorly.
3. The validator warns on ``xSALVAGE``. The defect is FVS's rather than the caller's, so the warning's
   job is to say which spelling the table holds. A caller who writes ``SALVAGE`` without the ``x`` is
   writing a keyword the table does not hold, so that name is refused, and the refusal names
   ``xSALVAGE``.
4. `fresh-fvsbc` does not silently add a keyword the caller did not write, with one exception: the
   tree-list handoff, which it must control. See :doc:`tree-list` and the hazard below.
   The handoff is ``TREEFMT`` with BC's format and ``TREEDATA`` with a blank parameter, which are
   written by the run and placed before the first ``PROCESS`` or ``STOP``. The rule's exception names
   the tree-record format; ``TREEDATA`` is part of the same handoff because without it FVS never opens
   the tree file, so the format and the instruction to use it cannot be separated. A set that already
   carries either keyword is refused rather than overridden. This reading was recorded when the run
   orchestration was written, because a rule read generously should say so.
5. A keyword set carries a hash, and the hash is part of the run's provenance. See :doc:`provenance`.
   The hash is taken over the set's **rendered text** — the bytes a run was given — rather than over a
   structure, so that it identifies exactly what FVS read, and it is written with its algorithm named,
   as ``sha256:`` followed by the digest. Order is part of the identity, because FVS processes a set in
   order.
6. A keyword that reads a **supplemental record** carries it on ``Keyword.supplemental``, and the
   writer emits it after the keyword record with no terminator. The record is validated before a run:
   a missing or repeated record is refused, and a unit outside the documented set is refused. The rule
   exists because a missing record is not harmless; FVS would read the next keyword as the unit.

The open hazard
---------------

PyFVS injects a ``TREEFMT`` keyword when the caller's set lacks one, using its own default format rather
than the BC variant's. `fresh-fvsbc` must not inherit that behaviour silently. Either it writes the BC
``TREEFMT`` itself, or it writes the format the build actually expects and records why.

Resolved in `P2.2`. The injection is conditional, and avoiding it needs no change to PyFVS, so contract
rule 4 stands: `fresh-fvsbc` passes BC's format through ``FVS(treelist_format=...)`` whenever it supplies trees
as data. The injection's condition, and how the two formats differ, are in :doc:`tree-list` and are not
repeated here.

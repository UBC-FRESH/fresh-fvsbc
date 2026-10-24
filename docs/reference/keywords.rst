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
4. `fresh-fvsbc` does not silently add a keyword the caller did not write, with one exception: the tree-record
   format, which it must control. See :doc:`tree-list` and the hazard below.
5. A keyword set carries a hash, and the hash is part of the run's provenance. See :doc:`provenance`.
   The hash is taken over the set's **rendered text** — the bytes a run was given — rather than over a
   structure, so that it identifies exactly what FVS read, and it is written with its algorithm named,
   as ``sha256:`` followed by the digest. Order is part of the identity, because FVS processes a set in
   order.

The open hazard
---------------

PyFVS injects a ``TREEFMT`` keyword when the caller's set lacks one, using its own default format rather
than the BC variant's. `fresh-fvsbc` must not inherit that behaviour silently. Either it writes the BC
``TREEFMT`` itself, or it writes the format the build actually expects and records why.

Resolved in `P2.2`. The injection is conditional, and avoiding it needs no change to PyFVS, so contract
rule 4 stands: `fresh-fvsbc` passes BC's format through ``FVS(treelist_format=...)`` whenever it supplies trees
as data. The injection's condition, and how the two formats differ, are in :doc:`tree-list` and are not
repeated here.

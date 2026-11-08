      BLOCK DATA MPBLKD
      IMPLICIT NONE
C----------
C LPMPB $Id$
C----------
C
C     MOUNTAIN PINE BEETLE -- CANADA-BC VARIANT.
C
C     BC species list (MAXSP=15):
C      1 PW, 2 LW, 3 FD, 4 BG, 5 HW, 6 CW, 7 PL,
C      8 SE, 9 BL, 10 PY, 11 EP, 12 AT, 13 AC, 14 OC, 15 OH.
C
C     MPBSPM maps each BC species to the LPMPB surrogate group used by
C     SURFCE: 1=WP, 2=WL, 3=DF/GF/WH/C, 7=LP, 10=PP.
C
COMMONS
C
      INCLUDE 'PRGPRM.F77'
C
      INCLUDE 'MPBCOM.F77'
C
COMMONS
C
      DATA JOMPB / 7 /
C
      DATA IPLTNO/1/,IMPROB/1/,NATR/2/,KEYMPB/2,3,6*0,1/,
     >     INCRS/10/
C
      DATA IDXWP,IDXWL,IDXDF,IDXLP,IDXPP/1,2,3,7,10/
C
C     PW LW FD BG HW CW PL SE BL PY EP AT AC OC OH
      DATA MPBSPM/
     >     1, 2, 3, 3, 3, 3, 7, 1, 3,10, 3, 3, 3, 3, 3/
C
      END

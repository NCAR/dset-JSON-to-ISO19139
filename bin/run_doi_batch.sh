
# January 2021
#DOI_SUFFIXES="4xv0-fg55 t353-c093 9n3z-7x72 7we1-8k84 z9nq-8g12 b92r-gt40 d6ws8r93 9zx1-jq74 \
#              60hz-ry38 sv4e-7z49 1TDC-0Z47 fv7s-ax27 82ny-4074 p8es-mc74 k9vg-t494 789w-m137 \
#              1k0w-2272 chk8-fx07 rgpy-g566 8r12-hs65 7m8g-ja33 qan9-we09"

# February 2021
#DOI_SUFFIXES="4xv0-fg55 0dxg-nn57 1a8d-yh72"

# December 2021
DOI_SUFFIXES="10.26024/sprq-2d04"

echo "DOI_SUFFIXES= " $DOI_SUFFIXES


for f in $DOI_SUFFIXES; do
   #echo "Processing 10.5065/${f}..."
   #python datacite2iso.py  --doi 10.5065/${f} > test_${f}.xml
   echo "Processing ${f}..."
   suffix=`echo ${f} | cut -d / -f 2`
   python datacite2iso.py  --doi ${f} > test_${suffix}.xml
done

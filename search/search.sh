
sto=$1
name=$2
dbfna=$3
E=$4  # 100
incE=$5 # 0.01

me=`basename "$0"`
if [ ! -f $sto.cm ]; then
	echo "$me: $sto.cm not found, building" >&2
	cmbuild $sto.cm $sto
	cmcalibrate $sto.cm
	echo "$me: $sto.cm built" >&2
else
	echo "$me: $sto.cm found" >&2
fi

echo "$me: searching $sto.cm in $dbfna with E-value $E and inclusion threshold $incE" >&2
if [ ! -d searches/$name ]; then mkdir searches/$name; fi
out=searches/$name/$name.out
cmsearch -o $out -A $out.sto --tblout $out.tbl -E $E --incE $incE $sto.cm $dbfna

echo "$me: done" >&2


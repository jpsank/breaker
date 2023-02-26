
sto=sto/DUF1646/RF03071.sto
name=rs213-bact-repr_DUF1646
# sto=sto/nhaA-I/RF03057.sto
# name=rs213-bact-repr_nhaA-I

dbfna=~/bioinfo/db/rs213-bact-repr/rs213-bact-repr.fna
# alt: ~/bioinfo/db/bacteria/bacteria.1.1.genomic.fna.gz

E=100.0 # default 10.0
incE=0.01 # default 0.01

num=1
while [ -d searches/$name1_$num ]; do
	num=$((num+1))
done

./search.sh $sto "$name_$num" $dbfna $E $incE


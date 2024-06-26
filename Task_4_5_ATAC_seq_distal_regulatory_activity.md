# 4. ATAC-seq hands-on session


### move to folder and make directories to store files

```sh
cd ATAC-seq/
mkdir data
mkdir analyses
ls 

cd data
mkdir bed.files bigBed.files bigWig.files fastq.files tsv.files
```
 
### download metadata

```sh
../bin/download.metadata.sh "https://www.encodeproject.org/metadata/?replicates.library.biosample.donor.uuid=d370683e-81e7-473f-8475-7716d027849b&status=released&status=submitted&status=in+progress&assay_title=ATAC-seq&biosample_ontology.term_name=sigmoid+colon&biosample_ontology.term_name=stomach&type=Experiment"


## retrieving ATAC-seq peaks (bigBed narrow, pseudoreplicated peaks, assembly GRCh38)

grep -F ATAC-seq metadata.tsv |\
grep -F "bigBed_narrowPeak" |\
grep -F "pseudoreplicated_peaks" |\
grep -F "GRCh38" |\
awk 'BEGIN{FS=OFS="\t"}{print $1, $11}' |\
sort -k2,2 -k1,1r |\
sort -k2,2 -u > analyses/bigBed.peaks.ids.txt


cut -f1 analyses/bigBed.peaks.ids.txt |\
while read filename; do
  wget -P data/bigBed.files "https://www.encodeproject.org/files/$filename/@@download/$filename.bigBed"
done
```


### check integrity of files

```sh
for file_type in bigBed; do

  # retrieve original MD5 hash from the metadata
  ../bin/selectRows.sh <(cut -f1 analyses/"$file_type".*.ids.txt) metadata.tsv | cut -f1,46 > data/"$file_type".files/md5sum.txt

  # compute MD5 hash on the downloaded files 
  cat data/"$file_type".files/md5sum.txt |\
  while read filename original_md5sum; do 
    md5sum data/"$file_type".files/"$filename"."$file_type" |\
    awk -v filename="$filename" -v original_md5sum="$original_md5sum" 'BEGIN{FS=" "; OFS="\t"}{print filename, original_md5sum, $1}' 
  done > tmp 
  mv tmp data/"$file_type".files/md5sum.txt

  # make sure there are no files for which original and computed MD5 hashes differ
  awk '$2!=$3' data/"$file_type".files/md5sum.txt

done
```

### generate bed files

```sh
cut -f1 analyses/bigBed.peaks.ids.txt |\
while read filename; do
  bigBedToBed data/bigBed.files/"$filename".bigBed data/bed.files/"$filename".bed
done
```


### get gencode annotation

```sh
mkdir annotation
wget -P annotation "https://www.encodeproject.org/files/gencode.v24.primary_assembly.annotation/@@download/gencode.v24.primary_assembly.annotation.gtf.gz"

gunzip annotation/gencode.v24.primary_assembly.annotation.gtf.gz
less annotation/gencode.v24.primary_assembly.annotation.gtf
```


### moving the downloaded gencode.v24.protein.coding.non.redundant.TSS.bed 


```sh
mv ../../Downloads/gencode.v24.protein.coding.non.redundant.TSS.bed  annotation/
```

### Making new directory peak.analysis

```sh
mkdir analyses/peaks.analysis
```

## intersection for the number of peaks that intersect promoter regions


```sh
cut -f-2 analyses/bigBed.peaks.ids.txt |\
while read filename tissue; do 
  bedtools intersect -a annotation/gencode.v24.protein.coding.non.redundant.TSS.bed -b data/bed.files/"$filename".bed -u |\
  sort -u > analyses/peaks.analysis/promoters_regions.with.peaks."$tissue".ATAC-seq.bed
  wc -l analyses/peaks.analysis/promoters_regions.with.peaks."$tissue".ATAC-seq.bed > analyses/peaks.analysis/promoters_regions.with.peaks."$tissue".ATAC-seq.counts.txt
done
```

### 1) the number of peaks that intersect promoter regions: 75306 peaks for sigmoid colon & 76272 peaks for stomach


## intersection number of peaks that fall outside gene coordinates

```sh
cut -f-2 analyses/bigBed.peaks.ids.txt |\
while read filename tissue; do
  bedtools intersect -a data/bed.files/"$filename".bed -b annotation/gencode.v24.protein.coding.gene.body.bed -v |\
  sort -u > analyses/peaks.analysis/peaks.outside.gene.bodies."$tissue".bed
  wc -l analyses/peaks.analysis/peaks.outside.gene.bodies."$tissue".bed > analyses/peaks.analysis/peaks.outside.gene.bodies.counts."$tissue".txt
done
```

### 2) the number of peaks that fall outside gene coordinates: 37035 peaks for sigmoid colon & 34537 peaks for stomach



# 5. Distal regulatory activity

## Task 1

```sh
mkdir regulatory_elements
```

## Task 2

```sh
mkdir metadata_H3K27ac
cd metadata_H3K27ac/ 

../../bin/download.metadata.sh "https://www.encodeproject.org/metadata/?replicates.library.biosample.donor.uuid=d370683e-81e7-473f-8475-7716d027849b&status=released&status=submitted&status=in+progress&biosample_ontology.term_name=stomach&biosample_ontology.term_name=sigmoid+colon&assay_title=total+RNA-seq&assay_title=Histone+ChIP-seq&target.label=H3K27ac&type=Experiment"


mkdir -p ../data/bigBed.files
cd ..
mkdir analyses

grep -F H3K27ac metadata_H3K27ac/metadata.tsv |\
grep -F "bigBed_narrowPeak" |\
grep -F "pseudoreplicated_peaks" |\
grep -F "GRCh38" |\
awk 'BEGIN{FS=OFS="\t"}{print $1, $11, $23}' |\
sort -k2,2 -k1,1r |\
sort -k2,2 -u > analyses/bigBed.H3K27ac.peaks.ids.txt

cut -f1 analyses/bigBed.H3K27ac.peaks.ids.txt |\
while read filename; do
  wget -P data/bigBed.files "https://www.encodeproject.org/files/$filename/@@download/$filename.bigBed"
done


mkdir metadata_H3K4me1
cd metadata_H3K4me1

../../bin/download.metadata.sh "https://www.encodeproject.org/metadata/?replicates.library.biosample.donor.uuid=d370683e-81e7-473f-8475-7716d027849b&status=released&status=submitted&status=in+progress&biosample_ontology.term_name=stomach&biosample_ontology.term_name=sigmoid+colon&assay_title=Histone+ChIP-seq&target.label=H3K4me1&type=Experiment"

cd ..

grep -F H3K4me1 metadata_H3K4me1/metadata.tsv |\
grep -F "bigBed_narrowPeak" |\
grep -F "pseudoreplicated_peaks" |\
grep -F "GRCh38" |\
awk 'BEGIN{FS=OFS="\t"}{print $1, $11, $23}' |\
sort -k2,2 -k1,1r |\
sort -k2,2 -u > analyses/bigBed.H3K4me1.peaks.ids.txt

cut -f1 analyses/bigBed.H3K4me1.peaks.ids.txt |\
while read filename; do
  wget -P data/bigBed.files "https://www.encodeproject.org/files/$filename/@@download/$filename.bigBed"
done

mkdir data/bed.files

cut -f-2 analyses/bigBed.H3K27ac.peaks.ids.txt |\
while read filename tissue; do
  bigBedToBed data/bigBed.files/"$filename".bigBed data/bed.files/"$tissue".H3K27ac.bed
done


cut -f-2 analyses/bigBed.H3K4me1.peaks.ids.txt |\
while read filename tissue; do
  bigBedToBed data/bigBed.files/"$filename".bigBed data/bed.files/"$tissue".H3K4me1.bed
done

mkdir analyses/peaks.analysis

tissues=("stomach" "sigmoid_colon")
for tissue in "${tissues[@]}"; do
```

### Intersect ATAC-seq peaks outside gene bodies with H3K27ac peaks
```sh
  bedtools intersect -a ../ATAC-seq/analyses/peaks.analysis/peaks.outside.gene.bodies."$tissue".bed -b data/bed.files/"$tissue".H3K27ac.bed -u > temp_"$tissue"_H3K27ac.bed
 ```
### Intersect the above result with H3K4me1 peaks

```sh
  bedtools intersect -a temp_"$tissue"_H3K27ac.bed -b data/bed.files/"$tissue".H3K4me1.bed -u > analyses/peaks.analysis/candidate_distal_regulatory_elements."$tissue".bed
``` 

```sh
wc -l analyses/peaks.analysis/candidate_distal_regulatory_elements."$tissue".bed > analyses/peaks.analysis/candidate_distal_regulatory_elements_count."$tissue".txt

rm temp_"$tissue"_H3K27ac.bed

done
```

### There are 14215 candidate distal regulatory elements for sigmoid colon and 8022  for stomach.

## Task 3

```sh
tissues=("stomach" "sigmoid_colon")
for tissue in "${tissues[@]}"; do
  grep -w "chr1" analyses/peaks.analysis/candidate_distal_regulatory_elements."$tissue".bed |\
  awk 'BEGIN{FS=OFS="\t"}{print $4, $2}' |\
  sort -k2,2n > analyses/peaks.analysis/regulatory.elements.starts."$tissue".tsv
done
```

## Task4

```sh
head -1 ../ChIP-seq/annotation/gencode.v24.protein.coding.gene.body.bed


grep -w "chr1" ../ChIP-seq/annotation/gencode.v24.protein.coding.gene.body.bed |\
awk 'BEGIN{FS=OFS="\t"}{if ($6=="+"){start=$2} else {start=$3}; print $4, start}' |\
sort -k2,2n > analyses/peaks.analysis/gene.starts.tsv
```

## Task5

```sh
cd ..
cd bin/
nano
##copy and save scrip as get.distance.py
cd ../regulatory_elements/

python ../bin/get.distance.py --input analyses/peaks.analysis/gene.starts.tsv --start 980000
```

## Task 6. 


```sh
cat analyses/peaks.analysis/regulatory.elements.starts.stomach.tsv | while read element start; do 
   python ../bin/get.distance.py --input analyses/peaks.analysis/gene.starts.tsv --start "$start"; 
done > regulatoryElements.genes.distances.stomach.tsv


cat analyses/peaks.analysis/regulatory.elements.starts.sigmoid_colon.tsv | while read element start; do 
   python ../bin/get.distance.py --input analyses/peaks.analysis/gene.starts.tsv --start "$start"; 
done > regulatoryElements.genes.distances.sigmoid_colon.tsv
```

## Task 7. 

```sh
cat regulatoryElements.genes.distances.stomach.tsv | awk 'BEGIN{FS=OFS="\t"}{print $3}' | Rscript -e 'distances <- scan(file="stdin"); median.dist <- median(distances); mean.dist <- mean(distances); cat(cbind(median.dist, mean.dist), "\n")' > median.mean.dist.stomach.txt

cat regulatoryElements.genes.distances.sigmoid_colon.tsv | awk 'BEGIN{FS=OFS="\t"}{print $3}' | Rscript -e 'distances <- scan(file="stdin"); median.dist <- median(distances); mean.dist <- mean(distances); cat(cbind(median.dist, mean.dist), "\n")' > median.mean.dist.sigmoid_colon.txt
```

### median sigmoid: 35802 
### mean sigmoid: 73635.89 
### median stomach: 27735 
### mean stomach: 45227.05 







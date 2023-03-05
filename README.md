# Computational Biology Project for *CPSC 290: Directed Research*

## Background
A riboswitch is a regulatory segment of messenger RNA designed to bind a ligand, invoking a change in the translation of the gene encoded by the mRNA (Breaker 1). Riboswitches are a relatively newly discovered class of gene-control system, and as of 2022, >55 distinct riboswitches have been uncovered, attributing function to previously unexplained noncoding portions of RNA (Kavita & Breaker 1). In their review of recent decades of riboswitch discovery, Kavita and Breaker project that thousands more riboswitch classes remain undiscovered at higher levels of rarity than those that have already been discovered, highlighting the need for improved computational search tools (3). Generally, in the age of increasingly high-throughput technologies, the rapid expansion of gene sequencing and computing capabilities demands new computer analysis, search, and modeling algorithms to bolster our study of the genetic logic that underlies life (Yegnasubramanian & Isaacs 1).

## Methods
**Part 1**: Update consensus models for DUF1646 and nhaA-I riboswitches and analyze results to determine genetic distance between the two riboswitches.
1. Retrieve RNA motif Stockholm files (DUF1646 and nhaA-I) from Rfam.
2. Run searches for RNA motifs against the latest bacterial and archaeal databases using Infernal cmsearch.
3. Perform analysis on the search results (number of hits, bit score distribution, and predicted secondary structure R2R visualization) to get a better picture of the genetic distance between the two riboswitches.
4. Implement ViennaRNA/CMfinder to fold the sequences in the search results.
5. 

**Part 2**: Genetic algorithm to refine RNA folding.
1. Refine/optimize the folding results from ViennaRNA using a genetic algorithm, as most riboswitch RNAs can adopt modular folds.

**Part 3**: Web server which allows visualization, editing, and refinement of the folded output of parts 1-2.
1. Visualize folding for individual multiple sequence alignment in an RNA alignment editor (i.e. re-implement RALEE with new functionality)
2. Implement SODA (or another genome context viewer) to render the genome context for any individual sequence from the search results of part 1.
3. Visualize the complete search result from part 1, which is a major component of the BLISS/DIMPL pipeline.

## Deliverables
Each component of my proposal corresponds to a deliverable:
1. An updated consensus model and genomic distribution (and the subject of research / test data / use case for all following bullets).
2. A set of Python functions for folding sequences in a Sto file, using the Vienna RNA Python interface.
3. A program which can take a single sequence, use the functions from 2, and produce an optimized Vienna output.
4. A web server which allows visualization, editing, and refinement of the folded output of 1-3.
5. A program / module which implements SODA (or another genome context viewer) to visualize the genomic context of an individual sequence from 1.
6. A web server which collates the output from 5 applied to the search from 1.


## References
Baker, Jenny L et al. “Widespread genetic switches and toxicity resistance proteins for fluoride.” Science (New York, N.Y.) vol. 335,6065 (2012): 233-235. doi:10.1126/science.1215063

Barrick, Jeffrey E et al. “New RNA motifs suggest an expanded scope for riboswitches in bacterial genetic control.” Proceedings of the National Academy of Sciences of the United States of America vol. 101,17 (2004): 6421-6. doi:10.1073/pnas.0308014101

Breaker, Ronald R. “Riboswitches and Translation Control.” Cold Spring Harbor perspectives in biology vol. 10,11 a032797. 1 Nov. 2018, doi:10.1101/cshperspect.a032797

Edwards, A. L. & Batey, R. T. (2010) Riboswitches: A Common RNA Regulatory Element. Nature

Ferrè, F et al. “DIAL: a web server for the pairwise alignment of two RNA three-dimensional structures using nucleotide, dihedral angle and base-pairing similarities.” Nucleic acids research vol. 35,Web Server issue (2007): W659-68. doi:10.1093/nar/gkm334

Garst, Andrew D et al. “Riboswitches: structures and mechanisms.” Cold Spring Harbor perspectives in biology vol. 3,6 a003533. 1 Jun. 2011, doi:10.1101/cshperspect.a003533

Hazen, Robert M et al. “Functional information and the emergence of biocomplexity.” Proceedings of the National Academy of Sciences of the United States of America vol. 104 Suppl 1,Suppl 1 (2007): 8574-81. doi:10.1073/pnas.0701744104

Kavita, Kumari & Breaker, Ronald. (2022). Discovering riboswitches: the past and the future. Trends in Biochemical Sciences. 48. 10.1016/j.tibs.2022.08.009. 

Kitts, Paul A et al. “Assembly: a resource for assembled genomes at NCBI.” Nucleic acids research vol. 44,D1 (2016): D73-80. doi:10.1093/nar/gkv1226

Leontis, Neocles B et al. “The building blocks and motifs of RNA architecture.” Current opinion in structural biology vol. 16,3 (2006): 279-87. doi:10.1016/j.sbi.2006.05.009

Lorenz, Ronny et al. “ViennaRNA Package 2.0.” Algorithms for molecular biology : AMB vol. 6 26. 24 Nov. 2011, doi:10.1186/1748-7188-6-26

Weinberg, Zasha et al. “Comparative genomics reveals 104 candidate structured RNAs from bacteria, archaea, and their metagenomes.” Genome biology vol. 11,3 (2010): R31. doi:10.1186/gb-2010-11-3-r31

Yegnasubramanian, S., & Isaacs, W. B. (2010). Modern Molecular Biology: Approaches for Unbiased Discovery in Cancer Research. Springer New York. 

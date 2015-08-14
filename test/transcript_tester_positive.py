# coding: utf-8

"""
Unit test for a transcript on the positive strand.
"""

import unittest
import re
import copy
import mikado_lib.parsers
import mikado_lib.exceptions
import mikado_lib.loci_objects
import logging


class MonoBaseTester(unittest.TestCase):

    """
    This test verifies the correct ORF loading and splitting
     in the case where the transcript has multiple ORFs and
     in one case it starts exactly at the terminal point of
      a previous exon.
    """

    handler = logging.StreamHandler()
    handler.setLevel("DEBUG")
    logger = logging.getLogger("test")
    logger.setLevel("DEBUG")
    logger.propagate = False
    formatter = logging.Formatter(
        "{asctime} - {levelname} - {module}:{lineno} - {funcName} - {name} - {message}",
        style="{"
        )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.debug("TEST")

    def setUp(self):
        self.tr = mikado_lib.loci_objects.transcript.Transcript()
        self.tr.chrom = "Chr5"
        self.tr.start = 22597965
        self.tr.end = 22602701
        self.tr.strand = "+"
        self.tr.score = 1000
        self.tr.parent = "StringTie_DN.70115"
        self.tr.id = "StringTie_DN.70115.4"
        self.tr.source = "StringTie"
        self.tr.feature = "transcript"
        self.tr.exons = [(22597965, 22601782),
                         (22601862, 22601957),
                         (22602039, 22602701)]

        self.tr.logger = self.logger

        # First ORF
        self.bed1 = mikado_lib.parsers.bed12.BED12()
        self.bed1.chrom = self.tr.id
        self.bed1.start = 1
        self.bed1.end = 4577
        self.bed1.name = "{0}.1".format(self.tr.id)
        self.bed1.strand = "+"
        self.bed1.score = 0
        self.bed1.thickStart = 434
        self.bed1.thickEnd = 3736
        self.bed1.has_start_codon = True
        self.bed1.transcriptomic = True
        self.bed1.has_stop_codon = True
        self.bed1.blockCount = 1
        self.bed1.blockSizes = [len(self.bed1)]
        self.bed1.blockStarts = [0]

        # Second ORF
        self.bed2 = copy.deepcopy(self.bed1)
        self.bed2.name = "{0}.2".format(self.tr.id)
        self.bed2.thickStart = 2
        self.bed2.thickEnd = 388
        self.bed2.has_start_codon = False

        # Third ORF
        self.bed3 = copy.deepcopy(self.bed1)
        self.bed3.name = "{0}.3".format(self.tr.id)
        self.bed3.thickStart = 3914
        self.bed3.thickEnd = 4393

    def test_finalise(self):
        self.tr.finalize()
        self.assertTrue(self.tr.finalized)

    def test_load_orfs(self):
        self.assertFalse(self.bed1.invalid)
        self.assertFalse(self.bed2.invalid)
        self.assertFalse(self.bed3.invalid)
        print(self.bed3.cds_len)
        self.assertEqual(self.bed3.cds_len, self.bed3.thickEnd-self.bed3.thickStart+1 )

        self.tr.load_orfs([self.bed1, self.bed2, self.bed3])
        self.assertEqual(self.tr.number_internal_orfs, 3)
        self.assertEqual(self.tr.selected_cds_length, self.bed1.cds_len)

    def test_split(self):

        self.tr.load_orfs([self.bed3, self.bed1])
        splitted_transcripts = [l for l in self.tr.split_by_cds()]
        self.assertEqual(len(splitted_transcripts), 2)


class DrosoTester(unittest.TestCase):

    def setUp(self):

        ref_gtf = """2L\tprotein_coding\ttranscript\t523736\t540560\t.\t+\t.\tgene_id "FBgn0003963"; transcript_id "FBtr0329895"; exon_number "1"; gene_name "ush"; transcript_name "ush-RC"; exon_id "FBgn0003963:5"; gene_biotype "protein_coding";
2L\tprotein_coding\texon\t523736\t524059\t.\t+\t.\tgene_id "FBgn0003963"; transcript_id "FBtr0329895"; exon_number "1"; gene_name "ush"; transcript_name "ush-RC"; exon_id "FBgn0003963:5"; gene_biotype "protein_coding";
2L\tprotein_coding\texon\t525392\t525436\t.\t+\t.\tgene_id "FBgn0003963"; transcript_id "FBtr0329895"; exon_number "2"; gene_name "ush"; transcript_name "ush-RC"; exon_id "FBgn0003963:677"; gene_biotype "protein_coding";
2L\tprotein_coding\texon\t536023\t536966\t.\t+\t.\tgene_id "FBgn0003963"; transcript_id "FBtr0329895"; exon_number "3"; gene_name "ush"; transcript_name "ush-RC"; exon_id "FBgn0003963:7"; gene_biotype "protein_coding";
2L\tprotein_coding\texon\t537037\t537431\t.\t+\t.\tgene_id "FBgn0003963"; transcript_id "FBtr0329895"; exon_number "4"; gene_name "ush"; transcript_name "ush-RC"; exon_id "FBgn0003963:8"; gene_biotype "protein_coding";
2L\tprotein_coding\texon\t537549\t537749\t.\t+\t.\tgene_id "FBgn0003963"; transcript_id "FBtr0329895"; exon_number "5"; gene_name "ush"; transcript_name "ush-RC"; exon_id "FBgn0003963:9"; gene_biotype "protein_coding";
2L\tprotein_coding\texon\t537863\t539249\t.\t+\t.\tgene_id "FBgn0003963"; transcript_id "FBtr0329895"; exon_number "6"; gene_name "ush"; transcript_name "ush-RC"; exon_id "FBgn0003963:10"; gene_biotype "protein_coding";
2L\tprotein_coding\texon\t539310\t539452\t.\t+\t.\tgene_id "FBgn0003963"; transcript_id "FBtr0329895"; exon_number "7"; gene_name "ush"; transcript_name "ush-RC"; exon_id "FBgn0003963:11"; gene_biotype "protein_coding";
2L\tprotein_coding\texon\t539518\t540560\t.\t+\t.\tgene_id "FBgn0003963"; transcript_id "FBtr0329895"; exon_number "8"; gene_name "ush"; transcript_name "ush-RC"; exon_id "FBgn0003963:13"; gene_biotype "protein_coding";
2L\tprotein_coding\tCDS\t524038\t524059\t.\t+\t0\tgene_id "FBgn0003963"; transcript_id "FBtr0329895"; exon_number "1"; gene_name "ush"; transcript_name "ush-RC"; protein_id "FBpp0302929"; gene_biotype "protein_coding";
2L\tprotein_coding\tCDS\t525392\t525436\t.\t+\t2\tgene_id "FBgn0003963"; transcript_id "FBtr0329895"; exon_number "2"; gene_name "ush"; transcript_name "ush-RC"; protein_id "FBpp0302929"; gene_biotype "protein_coding";
2L\tprotein_coding\tCDS\t536023\t536966\t.\t+\t2\tgene_id "FBgn0003963"; transcript_id "FBtr0329895"; exon_number "3"; gene_name "ush"; transcript_name "ush-RC"; protein_id "FBpp0302929"; gene_biotype "protein_coding";
2L\tprotein_coding\tCDS\t537037\t537431\t.\t+\t0\tgene_id "FBgn0003963"; transcript_id "FBtr0329895"; exon_number "4"; gene_name "ush"; transcript_name "ush-RC"; protein_id "FBpp0302929"; gene_biotype "protein_coding";
2L\tprotein_coding\tCDS\t537549\t537749\t.\t+\t1\tgene_id "FBgn0003963"; transcript_id "FBtr0329895"; exon_number "5"; gene_name "ush"; transcript_name "ush-RC"; protein_id "FBpp0302929"; gene_biotype "protein_coding";
2L\tprotein_coding\tCDS\t537863\t539249\t.\t+\t1\tgene_id "FBgn0003963"; transcript_id "FBtr0329895"; exon_number "6"; gene_name "ush"; transcript_name "ush-RC"; protein_id "FBpp0302929"; gene_biotype "protein_coding";
2L\tprotein_coding\tCDS\t539310\t539452\t.\t+\t0\tgene_id "FBgn0003963"; transcript_id "FBtr0329895"; exon_number "7"; gene_name "ush"; transcript_name "ush-RC"; protein_id "FBpp0302929"; gene_biotype "protein_coding";
2L\tprotein_coding\tCDS\t539518\t540016\t.\t+\t1\tgene_id "FBgn0003963"; transcript_id "FBtr0329895"; exon_number "8"; gene_name "ush"; transcript_name "ush-RC"; protein_id "FBpp0302929"; gene_biotype "protein_coding";
"""

        pred_gtf = """2L\tStringTie\ttranscript\t476445\t479670\t1000\t-\t.\tgene_id "Stringtie.63"; transcript_id "Stringtie.63.1"; cov "141.769424"; FPKM "inf";
2L\tStringTie\texon\t476445\t478204\t1000\t-\t.\tgene_id "Stringtie.63"; transcript_id "Stringtie.63.1"; exon_number "1"; cov "149.294586";
2L\tStringTie\texon\t479407\t479670\t1000\t-\t.\tgene_id "Stringtie.63"; transcript_id "Stringtie.63.1"; exon_number "2"; cov "91.601692";"""

        ref_lines = [mikado_lib.parsers.GTF.GtfLine(line)
                     for line in filter(lambda x: x!='', ref_gtf.split("\n"))]
        self.ref = mikado_lib.loci_objects.transcript.Transcript(ref_lines[0])
        for l in ref_lines[1:]:
            self.ref.add_exon(l)
        self.ref.finalize()
        
        pred_lines = [mikado_lib.parsers.GTF.GtfLine(line)
                      for line in filter(lambda x: x!='', pred_gtf.split("\n"))]
        self.pred = mikado_lib.loci_objects.transcript.Transcript(pred_lines[0])
        for l in pred_lines[1:]:
            self.pred.add_exon(l)
        self.pred.finalize()
        
    def test_code(self):

        print( mikado_lib.scales.assigner.Assigner.compare(self.pred, self.ref) )


class TranscriptTesterPositive(unittest.TestCase):
    tr_gff = """Chr2    TAIR10    mRNA    626642    629176    .    +    .    ID=AT2G02380.1;Parent=AT2G02380
Chr2    TAIR10    exon    626642    626780    .    +    .    Parent=AT2G02380.1
Chr2    TAIR10    five_prime_UTR    626642    626780    .    +    .    Parent=AT2G02380.1
Chr2    TAIR10    exon    626842    626880    .    +    .    Parent=AT2G02380.1
Chr2    TAIR10    five_prime_UTR    626842    626877    .    +    .    Parent=AT2G02380.1
Chr2    TAIR10    CDS    626878    626880    .    +    0    Parent=AT2G02380.1
Chr2    TAIR10    exon    626963    627059    .    +    .    Parent=AT2G02380.1
Chr2    TAIR10    CDS    626963    627059    .    +    0    Parent=AT2G02380.1
Chr2    TAIR10    exon    627137    627193    .    +    .    Parent=AT2G02380.1
Chr2    TAIR10    CDS    627137    627193    .    +    2    Parent=AT2G02380.1
Chr2    TAIR10    exon    627312    627397    .    +    .    Parent=AT2G02380.1
Chr2    TAIR10    CDS    627312    627397    .    +    2    Parent=AT2G02380.1
Chr2    TAIR10    exon    627488    627559    .    +    .    Parent=AT2G02380.1
Chr2    TAIR10    CDS    627488    627559    .    +    0    Parent=AT2G02380.1
Chr2    TAIR10    exon    627696    627749    .    +    .    Parent=AT2G02380.1
Chr2    TAIR10    CDS    627696    627749    .    +    0    Parent=AT2G02380.1
Chr2    TAIR10    exon    627840    627915    .    +    .    Parent=AT2G02380.1
Chr2    TAIR10    CDS    627840    627915    .    +    0    Parent=AT2G02380.1
Chr2    TAIR10    exon    628044    628105    .    +    .    Parent=AT2G02380.1
Chr2    TAIR10    CDS    628044    628105    .    +    2    Parent=AT2G02380.1
Chr2    TAIR10    exon    628182    628241    .    +    .    Parent=AT2G02380.1
Chr2    TAIR10    CDS    628182    628241    .    +    0    Parent=AT2G02380.1
Chr2    TAIR10    exon    628465    628676    .    +    .    Parent=AT2G02380.1
Chr2    TAIR10    CDS    628465    628569    .    +    0    Parent=AT2G02380.1
Chr2    TAIR10    three_prime_UTR    628570    628676    .    +    .    Parent=AT2G02380.1
Chr2    TAIR10    exon    629070    629176    .    +    .    Parent=AT2G02380.1
Chr2    TAIR10    three_prime_UTR    629070    629176    .    +    .    Parent=AT2G02380.1"""

    tr_lines = tr_gff.split("\n")
    for pos, line in enumerate(tr_lines):
        tr_lines[pos] = re.sub("\s+", "\t", line)
        assert len(tr_lines[pos].split("\t")) == 9, line.split("\t")

    tr_gff_lines = [mikado_lib.parsers.GFF.GffLine(line) for line in tr_lines]

    for l in tr_gff_lines:
        assert l.header is False
    #         print(l)

    def setUp(self):
        """Basic creation test."""

        self.tr = mikado_lib.loci_objects.transcript.Transcript(self.tr_gff_lines[0])
        for line in self.tr_gff_lines[1:]:
            self.tr.add_exon(line)
        self.tr.finalize()

        self.orf = mikado_lib.parsers.bed12.BED12()
        self.orf.chrom = self.tr.id
        self.orf.start = 1
        self.orf.end = self.tr.cdna_length
        self.orf.name = self.tr.id
        self.orf.strand = "+"
        self.orf.score = 0
        self.orf.thickStart = self.tr.selected_start_distance_from_tss + 1
        self.orf.thickEnd = self.tr.cdna_length - self.tr.selected_end_distance_from_tes
        self.orf.blockCount = 1
        self.orf.blockSize = self.tr.cdna_length
        self.orf.blockStarts = 0
        self.orf.has_start_codon = True
        self.orf.has_stop_codon = True

    def test_basics(self):

        self.assertEqual(self.tr.chrom, "Chr2")
        self.assertEqual(self.tr.strand, "+")
        self.assertEqual(self.tr.exon_num, 12)
        self.assertEqual(self.tr.exon_num, len(self.tr.exons))
        self.assertEqual(self.tr.start, 626642)
        self.assertEqual(self.tr.end, 629176)
        self.assertEqual(self.tr.exons,
                         [(626642, 626780),
                          (626842, 626880),
                          (626963, 627059),
                          (627137, 627193),
                          (627312, 627397),
                          (627488, 627559),
                          (627696, 627749),
                          (627840, 627915),
                          (628044, 628105),
                          (628182, 628241),
                          (628465, 628676),
                          (629070, 629176)],
                         self.tr.exons)

    def test_cds(self):
        self.assertEqual(self.tr.combined_cds, self.tr.selected_cds)
        self.assertEqual(self.tr.combined_cds,
                         [(626878, 626880),
                          (626963, 627059),
                          (627137, 627193),
                          (627312, 627397),
                          (627488, 627559),
                          (627696, 627749),
                          (627840, 627915),
                          (628044, 628105),
                          (628182, 628241),
                          (628465, 628569)],
                         self.tr.combined_cds)
        self.assertEqual(self.tr.selected_cds_start, 626878)
        self.assertEqual(self.tr.selected_cds_end, 628569)

    def test_secondary_orf(self):

        self.assertEqual(self.tr.cds_not_maximal, 0)
        self.assertEqual(self.tr.cds_not_maximal_fraction, 0)

    def test_utr(self):
        self.assertEqual(self.tr.five_utr, [("UTR", 626642, 626780), ("UTR", 626842, 626877)])
        self.assertEqual(self.tr.three_utr, [("UTR", 628570, 628676), ("UTR", 629070, 629176)])

    def test_introns(self):

        self.assertEqual(self.tr.introns,
                         {(626781, 626841), (626881, 626962), (627060, 627136), (627194, 627311), (627398, 627487),
                          (627560, 627695), (627750, 627839), (627916, 628043), (628106, 628181), (628242, 628464),
                          (628677, 629069)},
                         self.tr.introns

                         )
        self.assertEqual(self.tr.combined_cds_introns,
                         {(626881, 626962), (627060, 627136), (627194, 627311), (627398, 627487), (627560, 627695),
                          (627750, 627839), (627916, 628043), (628106, 628181), (628242, 628464)},
                         self.tr.combined_cds_introns
                         )
        self.assertEqual(self.tr.selected_cds_introns,
                         {(626881, 626962), (627060, 627136), (627194, 627311), (627398, 627487), (627560, 627695),
                          (627750, 627839), (627916, 628043), (628106, 628181), (628242, 628464)},
                         self.tr.selected_cds_introns
                         )

    def test_utr_metrics(self):

        """Test for UTR exon num, start distance, etc."""

        self.assertEqual(self.tr.five_utr_num, 2)
        self.assertEqual(self.tr.three_utr_num, 2)
        self.assertEqual(self.tr.five_utr_num_complete, 1)
        self.assertEqual(self.tr.three_utr_num_complete, 1)

        self.assertEqual(self.tr.five_utr_length, 626780 + 1 - 626642 + 626877 + 1 - 626842)
        self.assertEqual(self.tr.three_utr_length, 628676 + 1 - 628570 + 629176 + 1 - 629070)

        self.assertEqual(self.tr.selected_start_distance_from_tss, 626780 + 1 - 626642 + 626878 - 626842,
                         self.tr.selected_end_distance_from_tes)
        self.assertEqual(self.tr.selected_start_distance_from_tss, self.tr.start_distance_from_tss)

        self.assertEqual(self.tr.selected_end_distance_from_tes, 628676 - 628569 + 629176 + 1 - 629070,
                         self.tr.selected_end_distance_from_tes)
        self.assertEqual(self.tr.selected_end_distance_from_tes, self.tr.end_distance_from_tes)

        self.assertEqual(self.tr.selected_end_distance_from_junction, 628676 + 1 - 628569)

    def test_strip_cds(self):

        self.tr.strip_cds()
        self.assertEqual(self.tr.selected_cds_length, 0)
        self.assertEqual(self.tr.three_utr, [])
        self.assertEqual(self.tr.five_utr, [])
        self.assertEqual(self.tr.selected_cds, [])
        self.assertEqual(self.tr.selected_cds_start, None)
        self.assertEqual(self.tr.selected_cds_end, None)

    def test_remove_utr(self):
        """Test for CDS stripping. We remove the UTRs and verify that start/end have moved, no UTR is present, etc."""

        self.tr.remove_utrs()
        self.assertEqual(self.tr.selected_cds_start, self.tr.start)
        self.assertEqual(self.tr.selected_cds_end, self.tr.end)
        self.assertEqual(self.tr.three_utr, [])
        self.assertEqual(self.tr.five_utr, [])
        self.assertEqual(self.tr.combined_cds,
                         [(626878, 626880),
                          (626963, 627059),
                          (627137, 627193),
                          (627312, 627397),
                          (627488, 627559),
                          (627696, 627749),
                          (627840, 627915),
                          (628044, 628105),
                          (628182, 628241),
                          (628465, 628569)],
                         self.tr.combined_cds)
        self.assertEqual(self.tr.combined_utr, [], self.tr.combined_utr)

    def test_load_orf(self):

        """Test for loading a single ORF. We strip the CDS and reload it."""

        self.tr.strip_cds()
        self.tr.load_orfs([self.orf])
        self.assertEqual(self.tr.combined_cds,
                         [(626878, 626880), (626963, 627059), (627137, 627193), (627312, 627397), (627488, 627559),
                          (627696, 627749), (627840, 627915), (628044, 628105), (628182, 628241), (628465, 628569)],
                         self.tr.combined_cds)
        self.assertEqual(self.tr.selected_cds_start, 626878)
        self.assertEqual(self.tr.selected_cds_end, 628569)

    def test_negative_orf(self):
        """Test loading a negative strand ORF onto a multiexonic transcript. This should have no effect."""

        self.orf.strand = "-"
        self.tr.strip_cds()
        self.tr.load_orfs([self.orf])
        self.assertEqual(self.tr.selected_cds_start, None)

    def test_raises_invalid(self):

        self.tr.finalized = False
        self.tr.strand = None

        self.assertRaises(mikado_lib.exceptions.InvalidTranscript, self.tr.finalize)

        self.tr.strand = "+"
        self.tr.finalize()
        self.tr.finalized = False
        self.tr.exons += [(625878, 625880)]
        self.assertRaises(mikado_lib.exceptions.InvalidTranscript, self.tr.finalize)

    def test_complete(self):

        self.assertTrue(self.tr.has_stop_codon)
        self.assertTrue(self.tr.has_start_codon)
        self.assertTrue(self.tr.is_complete)

    def test_lengths(self):

        self.assertEqual(self.tr.cdna_length, 1061)
        self.assertEqual(self.tr.selected_cds_length, 672)
        self.assertAlmostEqual(self.tr.combined_cds_fraction, 672 / 1061, delta=0.01)
        self.assertAlmostEqual(self.tr.selected_cds_fraction, 672 / 1061, delta=0.01)

    def testSegments(self):

        self.assertEqual(self.tr.combined_cds_num, 10)
        self.assertEqual(self.tr.selected_cds_num, 10)
        self.assertEqual(self.tr.highest_cds_exon_number, 10)
        self.assertEqual(self.tr.max_intron_length, 393)
        self.assertEqual(self.tr.number_internal_orfs, 1)

    def testDoubleOrf(self):

        """Test to verify the introduction of multiple ORFs."""

        self.tr.strip_cds()
        self.tr.finalized = False

        first_orf = mikado_lib.parsers.bed12.BED12()
        first_orf.chrom = self.tr.id
        first_orf.start = 1
        first_orf.end = self.tr.cdna_length
        first_orf.name = "first"
        first_orf.strand = "+"
        first_orf.score = 0
        first_orf.thickStart = 51
        first_orf.thickEnd = 398
        first_orf.blockCount = 1
        first_orf.blockSize = self.tr.cdna_length
        first_orf.blockSizes = [self.tr.cdna_length]
        first_orf.blockStarts = [0]
        first_orf.rgb = 0
        first_orf.has_start_codon = True
        first_orf.has_stop_codon = True
        first_orf.transcriptomic = True
        self.assertFalse(first_orf.invalid)
        # This should not be incorporated
        second_orf = mikado_lib.parsers.bed12.BED12()
        second_orf.chrom = self.tr.id
        second_orf.start = 1
        second_orf.end = self.tr.cdna_length
        second_orf.name = "second"
        second_orf.strand = "+"
        second_orf.score = 0
        second_orf.thickStart = 201
        second_orf.thickEnd = 410
        second_orf.blockCount = 1
        second_orf.blockSize = self.tr.cdna_length
        second_orf.blockSizes = [self.tr.cdna_length]
        second_orf.blockStarts = [0]
        second_orf.rgb = 0
        second_orf.has_start_codon = True
        second_orf.has_stop_codon = True
        second_orf.transcriptomic = True
        self.assertFalse(second_orf.invalid)

        self.assertTrue(mikado_lib.loci_objects.transcript.Transcript.is_overlapping_cds(first_orf, second_orf))

        # This should be added
        third_orf = mikado_lib.parsers.bed12.BED12()
        third_orf.chrom = self.tr.id
        third_orf.start = 1
        third_orf.end = self.tr.cdna_length
        third_orf.name = "third"
        third_orf.strand = "+"
        third_orf.score = 0
        third_orf.thickStart = 501
        third_orf.thickEnd = 800
        third_orf.blockCount = 1
        third_orf.blockSize = self.tr.cdna_length
        third_orf.blockSizes = [self.tr.cdna_length]
        third_orf.blockStarts = [0]
        third_orf.rgb = 0
        third_orf.has_start_codon = True
        third_orf.has_stop_codon = True
        third_orf.transcriptomic = True
        self.assertFalse(third_orf.invalid)

        self.assertFalse(mikado_lib.loci_objects.transcript.Transcript.is_overlapping_cds(first_orf, third_orf))
        self.assertFalse(mikado_lib.loci_objects.transcript.Transcript.is_overlapping_cds(second_orf, third_orf))

        self.assertFalse(third_orf == second_orf)
        self.assertFalse(first_orf == second_orf)
        self.assertFalse(first_orf == third_orf)

        candidates = [first_orf, second_orf, third_orf]

        # self.assertEqual(len(mikado_lib.loci_objects.transcript.Transcript.find_overlapping_cds(candidates)), 2)

        handler = logging.StreamHandler()
        handler.setLevel("DEBUG")
        logger = logging.getLogger("test")
        logger.setLevel("DEBUG")
        logger.addHandler(handler)
        logger.debug("TEST")
        self.tr.logger = logger

        self.tr.load_orfs([first_orf, second_orf, third_orf])

        self.assertTrue(self.tr.is_complete)
        self.tr.finalize()
        self.assertEqual(self.tr.number_internal_orfs, 2, (
            self.tr.cdna_length, self.tr.selected_start_distance_from_tss, self.tr.selected_end_distance_from_tes))

        self.assertEqual(self.tr.combined_cds_length, 648)
        self.assertEqual(self.tr.selected_cds_length, 348)
        self.assertEqual(self.tr.number_internal_orfs, 2, "\n".join([str(x) for x in self.tr.internal_orfs]))

        new_transcripts = sorted(self.tr.split_by_cds())

        self.assertEqual(len(new_transcripts), 2)
        self.assertEqual(new_transcripts[0].three_utr_length, 0)
        self.assertEqual(new_transcripts[1].five_utr_length, 0)


unittest.main()

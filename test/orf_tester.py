# coding: utf-8

"""
Test for the BED12 module.
"""

import unittest
from Bio import Seq, SeqRecord
from mikado_lib.parsers import bed12


class OrfTester(unittest.TestCase):
    """
    Basic tests to verify that the BED12 library functions as intended.
    """

    def setUp(self):
        """
        Starting operations
        """

        seq1 = """CCGAAGAAGAACAAATTCCTTGCTGAATCATGGCGAAGTTGAAGCTCTACTCTTACTGGA
GAAGCTCATGTGCTCATCGCGTCCGTATCGCCCTCACTTTAAAAGGGCTTGATTATGAAT
ATATACCGGTTAATTTGCTCAAAGGGGATCAATCCGATTCAGATTTCAAGAAGATCAATC
CAATGGGCACTGTACCAGCGCTTGTTGATGGTGATGTTGTGATTAATGACTCTTTCGCAA
TAATAATGTACCTGGATGATAAGTATCCGGAGCCACCGCTGTTACCAAGTGACTACCATA
AACGGGCGGTAAATTACCAGGCGACGAGTATTGTCATGTCTGGTATACAGCCTCATCAAA
ATATGGCTCTTTTTGTGAGAAGATGAGATTAATAGGTATCTCGAGGACAAGATAAATGCT
GAGGAGAAAACTGCTTGGATTACTAATGCTATCACAAAAGGATTCACAGGTTTATAACGA
CCTGTCTGATAATGTCTCATATGTCCTTCAGCTCTCGAGAAACTGTTGGTGAGTTGCGCT
GGAAAATACGCGACTGGTGATGAAGTTTACTTGGCTGATCTTTTCCTAGCACCACAGATC
CACGCAGCATTCAACAGATTCCATATTAACATGGAACCATTCCCGACTCTTGCAAGGTTT
TACGAGTCATACAACGAACTGCCTGCATTTCAAAATGCAGTCCCGGAGAAGCAACCAGAT
ACTCCTTCCACCATCTGATTCTGTGAACCGTAAGCTTCTCTCAGTCTCAGCTCAATAAAA
TCTC"""
        self.seq1 = SeqRecord.SeqRecord(Seq.Seq(seq1.replace("\n", "")), id="CLASS_2.159")

        seq2 = """ACAAAACAAAGTAATCGCGAAAACACACAACAATCGCTGGACTCTGCTACTGCGAAGAAC
AACAAATTCCTTGTTTATCATGGCGAATTCCGGCGAAGAGAAGTTGAAGCTCTACTCTTA
CTGGAGAAGCTCGTGTGCTCATCGTGTCCGTATCGCCCTCGCTTTGAAAGGGCTTGATTA
TGAGTATATACCAGTGAATTTGCTCAAGGGTGATCAATTCGATTCAGTTTATCGTTTTGA
TCTTCAAGATTTCAAGAAGATCAATCCAATGGGAACTGTACCAGCTCTGGTGGATGGAGA
TGTTGTGATTAATGATTCTTTTGCGATAATAATGTATCTGGATGAGAAGTACCCTGAGCC
ACCTTTGTTACCTCGTGACCTCCATAAACGAGCTGTGAATTACCAGGCAATGAGTATTGT
CTTGTCTGGCATACAGCCTCATCAAAATCTGGCTGTTATTAGGTATATCGAGGAAAAGAT
AAATGTGGAGGAGAAGACTGCCTGGGTTAATAATGCTATCACAAAAGGATTTACAGCTCT
CGAGAAACTGTTGGTGAATTGCGCTGGGAAACATGCGACTGGTGATGAAATTTACCTGGC
TGATCTCTTTCTAGCACCACAGATCCACGGAGCAATCAACAGATTCCAGATTAACATGGA
ACCGTACCCAACTCTTGCAAAATGTTACGAATCATACAACGAACTGCCTGCGTTTCAAAA
TGCACTACCGGAAAAGCAGCCAGATGCTCCTTCTTCCACCATCTGATTCTGTGAACCCAT
AAGCTACTCTCACTTTAATAAAACCTCAG"""

        self.seq2 = SeqRecord.SeqRecord(Seq.Seq(seq2.replace("\n", "")), id="CLASS_2.160")

        seq3 = """GATGCCCTTAGTTTCTCTACTTGTATCATACAATAAAGGTCACAGATTTTGAAATTTGCAAAGATATATC
ATACATTCTCAGAGGAAGCCTTTGTCTCTAAGACTCTGGACCGTCTCCTTAACCGCATCTTCAACCGCAG
TAAAAACCAGCCCGAGCTCAATCAATCGCTTAGCCGCATCATTACACGACGTAAGCCCAGGTTGAGTCTC
TTTATCAAACTTGTGAACAGCAAACTCAGGGAAGAGCTTAGACACAAGAGCAGCAAACTCACTGAACTGA
TAAATCCCATTAGTGCATAAAAACCGTCCAGAAGCGTCAGGTGTTTCGAATAGCATCACATGACCTTTAG
CCACATCTTTCACGTGAACCACACCGAGCCAGTGATGCTCTTGCGTCTCGGTCGAGCCTTGTAAAAGCTG
TAGCAGAACAGCACAGCTTGCGTTTAGGTTCGGTTGCAGAAGCGGTCCGAGACATGTTGATGGATGAATC
GTCACAATGTTGGTTCCATGCTTCTCCGAAAATTCCCAAGCTGCTTTCTCAGCTAATGTCTTCGAAATTG
GATACCATTTCTAAAATCAAAATTATATACCAATCGTTACAAATATCATATAAATCATCACTAACCATTT
TAAACCGAAATTTAACGAACCTGCCTCGACTTGCAAAAATCAAGATCGGACCACGACGACTCATCGACGG
GAACTTTTTCCGGCCAATTAGGGTTAGGAACCAATGCGGAGATAGATGACGTGATCACCACGCGTCTCAC
ATTAAACCTCTTAGCAGCTTCCAACACATTGATCGTTCCCTTAACCGCCGGTTCGACCAGCTCCTTCTCT
GGATCTACCGGTGGATCCAACGTACAAGGTGACGCCACGTGGAACACTCCCGCACATCCATCAATAGCTC
TGGAGATTGCATCAGAGTCTAAGAGATCCGCTTCAAAGATCTTGATCTTAGAATCGGATCCGGGTAGTTG
CAGAAGATGAGTCGGGTCGGATCCTGGGTAAATCGAAGCGTGGATTTTAGTATATCCTTTCTCAATTAAC
GTTCGGATTATCCAAGATCCGATGAAACCATTAGCTCCGGTTACACACACTGTCTCTTTCGCCATTGTTG
ATCAATAAGCGCTCACTGAGAATTTTTTTGTTCTCTCTCTCTATCGCAATTTATCTCAGAAGATAAGAAA
AAAAAAACATCTTTCCAGTAAAAAAGGATCCTTTGTTTTTTTCTTACACGTAAAAAATGGATTTTTTTTT
CTCTCTTAAAGATATAATGCGTTGATACAAAAGCGTAACGTTGACATGATATTATCCACTAGTTTTATAG
ACTTTTCAAAAAAAGGAGAGAATTTTCAATTCTTCAGTAGTCAAATAGATGAAGACCGCCGGAGCGCCGC
CGCAGAGAGGTGGTTCCTCTTCCTCCTCCGCCGTATACTTTAACTGGTCTTCATCATCTTGTTCTTACGA
TAGCTGTAGAGTTTTGGTGGTGAAGATGGGAGGAAAAAGCAAGAAGCCTCATCAATCTTCTTCTTTTAAG
GAGTCAGAGCCAGAACCACCGAGAATCAAATCCAATGTTAAGCATAACTTGCAGCTTCTCAAGTTATGGA
AGGAGTTTCAGAGCAGAGGATCTGGCATGGCTAAGCCAGCGACTAGTTACAGGAAGAAGAAAGTAGAGAA
AGACGAGTTACCGGATGATAGCGAGCTCTACCGGGATCCTACAAATACGCTTTACTACACGAACCAAGGT
CTATTGGATGACGCAGTTCCGGTTTTGCTTGTTGATGGTTATAATGTGTGTGGATATTGGATGAAGTTAA
AGAAACATTTCATGAAAGGAAGGCTTGACGTTGCTCGGCAGAAGTTAGTTGATGAACTTGTGTCCTTCAG
TATGGTTAAAGAGGTTAAGGTAGTGGTTGTGTTTGATGCTCTCATGTCTGGTCTTCCTACTCACAAGGAA
GACTTTGCAGGTGTTGATGTGATTTTCTCAGGAGAAACTTGTGCTGACGCTTGGATTGAAAAGGAGGTGG
TTGCATTGAGAGAAGATGGATGCCCCAAGGTTTGGGTTGTAACATCTGATGTCTGTCAACAACAAGCAGC
ACATGGAGCGGTATTGGGGCATCATATCGATGTTATAAACTCGTTATGTTCATATCTTGTTTTTGATTTT
GGTGACTGATTCTTGACAGGGAGCTTATATTTGGAGTAGCAAGGCATTGGTTTCTGAGATTAAATCGATG
CATAAGGAGGTTGAGAAAATGATGCAAGAAACAAGGTCAACATCTTTCCAAGGGAGATTGCTTAAACACA
ATCTTGATTCTGAAGTCGTTGATGCTCTTAAAGATCTTAGAGACAAATTATCAGAAAACGAAACAAAGAG
ATGACAAAAAGACCAATCCGGATTATATAAACAATTAACAAGGCTTGGTCTCTCCATGTAACTTCTGTCC
CAAGTAAGTAAGCTAATCTGACTTGTAAAAAACAGAGGCTGCAGAGGAAACGAGGGAGATAGAGAGAGAG
AGAGCTCAAATGCTTTGTTATTGTTGTATTTGTGTCTGAATTCTTTTTGACTAATCTATATATAGATTCG
TTTTCTTTGGTCCAAACATATGGTTAAAAGATAGTTCTGAATTTTTCTTTTAGCTTCATGCATAAGAATC
ATCTTAACCTAATAACCTATGTTTATTATTTTACAATAATGTAAAAATGTAAATTTTTAGTTGAATAATG
AACCAAATTTTTATGTAAAAAAACTTGGATGTTTATTTTCAAACACAAACATCAGTAACACTTGAAGCAG
TAGAGAGAATTGGAGGCAGAGCAAGTCTACAAATTTGCAGATAGTTCCAGGGTTTGAGCTGTTTGTTCTG
GTCAGTCTCCAATCAATCAAAGCATATGGTTTATCGAGAATGGATAGAGATTCAAGAGAAGATTGAAGAA
CTGAGTTTGCAAAGGCTTATCAATGCCTTCGACTTCGAGTTGAGATTGAAGAAAAGGTAAAGAAATAGCA
AGTGATCTTTTGAAAATAGATCTCATATATTAATGACTTTCCATGTCTGTATTTGCTGAAGTTGATCTGA
ATTTGCATATTGTTCATGTCAATGGATTGTCTGCTGTTACTAAATTTAACTTTGTGTCAGCACTCTTTAC
GTTTTGAATTGTCGAACCATTCACTTGTTCAGTTATTATTTGGTCTATCCATCCTTATATGTTGTTCTCT
GTTTAGATAAGGACAAAGAATAGACACCAGAGGAACTGAACCAAACAGCTGAGGCAGTTGGATATGGTGC
GGTGAAGTAAGTATACGTATCATCTCTATTCTACTGGTCACATGTCATGAGCAGGGAAATTACAGCCGTT
TATCAGAAAGTCTGGCAAAGACATAGATGAGCTGAAACAGACGGTTGAGGAAGCTTACACCAACTTGTTA
CCGAGCGTACTGTGCGAGTACCTCTACAGATTATCTGAACACTACACGGACTAGCGTACCATGAAATTTG
TGGATTGGCCTCTGCAGCTTTGTTTGAAATTCACTATAGCTTAGATGGCGAATTGGATTTAGACATGGAC
TTCCGGATTGTATGTTGTCTTTGAGTCTCAAGGGATTGATTAATGTGATGATATTTATACACCATAGCTG
AAATGAAATTTGTACTTAAAACTGATGGATAATTAATAACAGA"""

        self.seq3 = SeqRecord.SeqRecord(Seq.Seq(seq3.replace("\n", "")), id="PRJEB7093_DN.7194.1")

        seq4 = """GATGCCCTTAGTTTCTCTACTTGTATCATACAATAAAGGTCACAGATTTTGAAATTTGCA
AAGATATATCATACATTCTCAGAGGAAGCCTTTGTCTCTAAGACTCTGGACCGTCTCCTT
AACCGCATCTTCAACCGCAGTAAAAACCAGCCCGAGCTCAATCAATCGCTTAGCCGCATC
ATTACACGACGTAAGCCCAGGTTGAGTCTCTTTATCAAACTTGTGAACAGCAAACTCAGG
GAAGAGCTTAGACACAAGAGCAGCAAACTCACTGAACTGATAAATCCCATTAGTGCATAA
AAACCGTCCAGAAGCGTCAGGTGTTTCGAATAGCATCACATGACCTTTAGCCACATCTTT
CACGTGAACCACACCGAGCCAGTGATGCTCTTGCGTCTCGGTCGAGCCTTGTAAAAGCTG
TAGCAGAACAGCACAGCTTGCGTTTAGGTTCGGTTGCAGAAGCGGTCCGAGACATGTTGA
TGGATGAATCGTCACAATGTTGGTTCCATGCTTCTCCGAAAATTCCCAAGCTGCTTTCTC
AGCTAATGTCTTCGAAATTGGATACCATTTCTAAAATCAAAATTATATACCAATCGTTAC
AAATATCATATAAATCATCACTAACCATTTTAAACCGAAATTTAACGAACCTGCCTCGAC
TTGCAAAAATCAAGATCGGACCACGACGACTCATCGACGGGAACTTTTTCCGGCCAATTA
GGGTTAGGAACCAATGCGGAGATAGATGACGTGATCACCACGCGTCTCACATTAAACCTC
TTAGCAGCTTCCAACACATTGATCGTTCCCTTAACCGCCGGTTCGACCAGCTCCTTCTCT
GGATCTACCGGTGGATCCAACGTACAAGGTGACGCCACGTGGAACACTCCCGCACATCCA
TCAATAGCTCTGGAGATTGCATCAGAGTCTAAGAGATCCGCTTCAAAGATCTTGATCTTA
GAATCGGATCCGGGTAGTTGCAGAAGATGAGTCGGGTCGGATCCTGGGTAAATCGAAGCG
TGGATTTTAGTATATCCTTTCTCAATTAACGTTCGGATTATCCAAGATCCGATGAAACCA
TTAGCTCCGGTTACACACACTGTCTCTTTCGCCATTGTTGATCAATAAGCGCTCACTGAG
AATTTTTTTGTTCTCTCTCTCTATCGCAATTTATCTCAGAAGATAAGAAAAAAAAAACAT
CTTTCCAGTAAAAAAGGATCCTTTGTTTTTTTCTTACACGTAAAAAATGGATTTTTTTTT
CTCTCTTAAAGATATAATGCGTTGATACAAAAGCGTAACGTTGACATGATATTATCCACT
AGTTTTATAGACTTTTCAAAAAAAGGAGAGAATTTTCAATTCTTCAGTAGTCAAATAGAT
GAAGACCGCCGGAGCGCCGCCGCAGAGAGGTGGTTCCTCTTCCTCCTCCGCCGTATACTT
TAACTGGTCTTCATCATCTTGTTCTTACGATAGCTGTAGAGTTTTGGTGGTGAAGATGGG
AGGAAAAAGCAAGAAGCCTCATCAATCTTCTTCTTTTAAGGAGTCAGAGCCAGAACCACC
GAGAATCAAATCCAATGTTAAGCATAACTTGCAGCTTCTCAAGTTATGGAAGGAGTTTCA
GAGCAGAGGATCTGGCATGGCTAAGCCAGCGACTAGTTACAGGAAGAAGAAAGTAGAGAA
AGACGAGTTACCGGATGATAGCGAGCTCTACCGGGATCCTACAAATACGCTTTACTACAC
GAACCAAGGTCTATTGGATGACGCAGTTCCGGTTTTGCTTGTTGATGGTTATAATGTGTG
TGGATATTGGATGAAGTTAAAGAAACATTTCATGAAAGGAAGGCTTGACGTTGCTCGGCA
GAAGTTAGTTGATGAACTTGTGTCCTTCAGTATGGTTAAAGAGGTTAAGGTAGTGGTTGT
GTTTGATGCTCTCATGTCTGGTCTTCCTACTCACAAGGAAGACTTTGCAGGTGTTGATGT
GATTTTCTCAGGAGAAACTTGTGCTGACGCTTGGATTGAAAAGGAGGTGGTTGCATTGAG
AGAAGATGGATGCCCCAAGGTTTGGGTTGTAACATCTGATGTCTGTCAACAACAAGCAGC
ACATGGAGCGGGAGCTTATATTTGGAGTAGCAAGGCATTGGTTTCTGAGATTAAATCGAT
GCATAAGGAGGTTGAGAAAATGATGCAAGAAACAAGGTCAACATCTTTCCAAGGGAGATT
GCTTAAACACAATCTTGATTCTGAAGTCGTTGATGCTCTTAAAGATCTTAGAGACAAATT
ATCAGAAAACGAAACAAAGAGATGACAAAAAGACCAATCCGGATTATATAAACAATTAAC
AAGGCTTGGTCTCTCCATGTAACTTCTGTCCCAAGTAAGTAAGCTAATCTGACTTGTAAA
AAACAGAGGCTGCAGAGGAAACGAGGGAGATAGAGAGAGAGAGAGCTCAAATGCTTTGTT
ATTGTTGTATTTGTGTCTGAATTCTTTTTGACTAATCTATATATAGATTCGTTTTCTTTG
GTCCAAACATATGGTTAAAAGATAGTTCTGAATTTTTCTTTTAGCTTCATGCATAAGAAT
CATCTTAACCTAATAACCTATGTTTATTATTTTACAATAATGTAAAAATGTAAATTTTTA
GTTGAATAATGAACCAAATTTTTATGTAAAAAAACTTGGATGTTTATTTTCAAACACAAA
CATCAGTAACACTTGAAGCAGTAGAGAGAATTGGAGGCAGAGCAAGTCTACAAATTTGCA
GATAGTTCCAGGGTTTGAGCTGTTTGTTCTGGTCAGTCTCCAATCAATCAAAGCATATGG
TTTATCGAGAATGGATAGAGATTCAAGAGAAGATTGAAGAACTGAGTTTGCAAAGGCTTA
TCAATGCCTTCGACTTCGAGTTGAGATTGAAGAAAAGGTAAAGAAATAGCAAGTGATCTT
TTGAAAATAGATCTCATATATTAATGACTTTCCATGTCTGTATTTGCTGAAGTTGATCTG
AATTTGCATATTGTTCATGTCAATGGATTGTCTGCTGTTACTAAATTTAACTTTGTGTCA
GCACTCTTTACGTTTTGAATTGTCGAACCATTCACTTGTTCAGTTATTATTTGGTCTATC
CATCCTTATATGTTGTTCTCTGTTTAGATAAGGACAAAGAATAGACACCAGAGGAACTGA
ACCAAACAGCTGAGGCAGTTGGATATGGTGCGGTGAAGTAAGTATACGTATCATCTCTAT
TCTACTGGTCACATGTCATGAGCAGGGAAATTACAGCCGTTTATCAGAAAGTCTGGCAAA
GACATAGATGAGCTGAAACAGACGGTTGAGGAAGCTTACACCAACTTGTTACCGAGCGTA
CTGTGCGAGTACCTCTACAGATTATCTGAACACTACACGGACTAGCGTACCATGAAATTT
GTGGATTGGCCTCTGCAGCTTTGTTTGAAATTCACTATAGCTTAGATGGCGAATTGGATT
TAGACATGGACTTCCGGATTGTATGTTGTCTTTGAGTCTCAAGGGATTGATTAATGTGAT
GATATTTATACACCATAGCTGAAATGAAATTTGTACTTAAAACTGATGGATAATTAATAA
CAGA"""

        self.seq4 = SeqRecord.SeqRecord(Seq.Seq(seq4.replace("\n", "")), id="PRJEB7093_DN.7194.2")

        self.index = dict()
        self.index[self.seq1.id] = self.seq1
        self.index[self.seq2.id] = self.seq2
        self.index[self.seq3.id] = self.seq3
        self.index[self.seq4.id] = self.seq4

        self.bed1 = "\t".join(
            """CLASS_2.159    0    784    ID=CLASS_2.159|m.24650  0    +    29    386    0    1    784    0""".split())
        self.bed2 = "\t".join(
            "CLASS_2.160    0    809    ID=CLASS_2.160|m.34763 0    +    1    766    0    1    809    0".split())
        self.bed3 = "\t".join(
            "PRJEB7093_DN.7194.1  0 3683 ID=PRJEB7093_DN.7194.1|m.16659 0  -  641    1115  0  1    3683    0".split())
        self.bed4 = "\t".join(
            "PRJEB7093_DN.7194.2  0  3604 ID=PRJEB7093_DN.7194.2|m.16657 0 - 641    1115  0    1    3604    0".split())

    def test_b1(self):
        b1 = bed12.BED12(self.bed1, transcriptomic=True)
        self.assertEqual(b1.start, 1)
        self.assertEqual(len(b1), 784)
        self.assertEqual(b1.thickStart, 30)
        self.assertEqual(b1.thickEnd, 386)

    def test_b2(self):
        b2 = bed12.BED12(self.bed2, transcriptomic=True)
        self.assertEqual(b2.start, 1)
        self.assertEqual(len(b2), 809)
        self.assertEqual(b2.thickStart, 2)
        self.assertEqual(b2.thickEnd, 766)

    def test_b3(self):
        b3 = bed12.BED12(self.bed3, transcriptomic=True)
        self.assertFalse(b3.invalid)
        self.assertEqual(b3.start, 1)
        self.assertEqual(len(b3), 3683)

    def test_b4(self):
        b4 = bed12.BED12(self.bed4, transcriptomic=True)
        self.assertFalse(b4.invalid)
        self.assertEqual(b4.start, 1)
        self.assertEqual(len(b4), 3604)
        self.assertEqual(b4.cds_len, 1115 - 641 - 3)

    def test_b1_seq(self):
        b1 = bed12.BED12(self.bed1, transcriptomic=True, fasta_index=self.index)
        self.assertIn(str(self.index[b1.chrom][386 + 3:386 + 6].seq), ("TAG", "TGA", "TAA"))

        self.assertEqual(b1.start, 1)
        self.assertEqual(len(b1), 784)
        self.assertEqual("ATG", str(self.index[b1.chrom][b1.thickStart - 1:b1.thickStart + 2].seq),
                         str(self.index[b1.chrom][b1.thickStart - 1:b1.thickStart + 2].seq))

        self.assertEqual("ATG", b1.start_codon, b1.start_codon)
        self.assertEqual(b1.thickStart, 30)
        self.assertEqual(b1.thickEnd, 386)

        self.assertTrue(b1.has_stop_codon)

    def test_b2_seq(self):
        b2 = bed12.BED12(self.bed2, transcriptomic=True, fasta_index=self.index)
        self.assertNotIn(str(self.index[b2.chrom][766 + 3:766 + 6].seq), ("TAG", "TGA", "TAA"))
        self.assertEqual(b2.start, 1)
        self.assertEqual(len(b2), 809)
        self.assertFalse(b2.has_start_codon)

    def test_b3_seq(self):
        b3 = bed12.BED12(self.bed3, transcriptomic=True, fasta_index=self.index)
        self.assertFalse(b3.invalid, (len(b3), len(self.index[b3.id]),
                                      (b3.thickEnd, b3.thickStart), (b3.thickEnd - b3.thickStart + 1) % 3))

    def test_b4_seq(self):
        b4 = bed12.BED12(self.bed4, transcriptomic=True, fasta_index=self.index)
        self.assertFalse(b4.invalid, (len(b4), len(self.index[b4.id])))
        self.assertTrue(b4.has_start_codon)
        self.assertTrue(b4.has_stop_codon)
        self.assertTrue(b4.thickStart, 641)
        self.assertTrue(b4.thickEnd, 1112)
        self.assertTrue(b4.cds_len, 1112 - 641)

unittest.main()

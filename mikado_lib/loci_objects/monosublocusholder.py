# coding: utf-8

"""
This module defines a holder of Monosublocus instances. It is the last step
before the definition of real loci.
"""

import collections
import itertools
from mikado_lib.loci_objects.transcript import Transcript
from mikado_lib.loci_objects.abstractlocus import Abstractlocus
from mikado_lib.loci_objects.sublocus import Sublocus
from mikado_lib.loci_objects.locus import Locus
from mikado_lib.loci_objects.monosublocus import Monosublocus


# Resolution order is important here!
# pylint: disable=too-many-instance-attributes
class MonosublocusHolder(Sublocus, Abstractlocus):
    """This is a container that groups together the transcripts
    surviving the selection for the Monosublocus.
    The class inherits from both sublocus and Abstractlocus
    (the main abstract class) in order to be able to reuse
    some of the code present in the former.
    Internally, the most important method is define_loci -
    which will select the best transcript(s) and remove all the overlapping ones.
    The intersection function for this object is quite laxer than in previous stages,
    and so are the requirements for the inclusion.
    """

    __name__ = "monosubloci_holder"

    # pylint: disable=super-init-not-called
    def __init__(self, monosublocus_instance: Monosublocus, json_conf=None, logger=None):

        # I know what I am doing by NOT calling the Sublocus super but rather
        # Abstractlocus
        Abstractlocus.__init__(self)
        self.logger = logger
        self.splitted = False
        self.metrics_calculated = False
        self.json_conf = json_conf
        self.excluded = None
        self.purge = self.json_conf["run_options"]["purge"]
        self.scores_calculated = False
        # Add the transcript to the Locus
        self.locus_verified_introns = set()
        self.add_monosublocus(monosublocus_instance)
        self.loci = collections.OrderedDict()

    # Overriding is correct here
    # pylint: disable=arguments-differ
    def add_transcript_to_locus(self, transcript, check_in_locus=True):
        """Override of the sublocus method, and reversal to the original
        method in the Abstractlocus class.
        The check_in_locus boolean flag is used to decide
        whether to check if the transcript is in the Locus or not.
        This should be set to False for the first transcript, and True afterwards.

        :param transcript: a Transcript instance
        :type transcript: Transcript

        :param check_in_locus: optional flag to pass to the basic method.
        If set to False it disables checks on whether the transcript
        is really in the locus
        :type check_in_locus: bool
        """

        Abstractlocus.add_transcript_to_locus(self, transcript,
                                              check_in_locus=check_in_locus)
        self.locus_verified_introns = set.union(self.locus_verified_introns,
                                                transcript.verified_introns)
    # pylint: enable=arguments-differ

    def add_monosublocus(self, monosublocus_instance: Monosublocus):
        """Wrapper to extract the transcript from the monosubloci and pass it to the constructor.

        :param monosublocus_instance
        :type monosublocus_instance: Monosublocus
        """
        assert len(monosublocus_instance.transcripts) == 1
        if len(self.transcripts) == 0:
            check_in_locus = False
        else:
            check_in_locus = True
        for tid in monosublocus_instance.transcripts:
            self.add_transcript_to_locus(monosublocus_instance.transcripts[tid],
                                         check_in_locus=check_in_locus)

    def __str__(self, print_cds=False):
        """This special method is explicitly *not* implemented;
        this Locus object is not meant for printing, only for computation!

        :param print_cds: flag. Ignored.
        """
        raise NotImplementedError(
            """This is a container used for computational purposes only,
            it should not be printed out directly!""")

    def define_monosubloci(self, purge=False, excluded=None):
        """Overriden and set to NotImplemented to avoid cross-calling it when inappropriate.

        :param purge: flag. Ignored.
        :param excluded: flag. Ignored.
        """
        raise NotImplementedError(
            "Monosubloci are the input of this object, not the output.")

    def define_loci(self, purge=False, excluded=None):
        """This is the main function of the class. It is analogous
        to the define_subloci class defined for sublocus objects,
        but it returns "Locus" objects (not "Monosublocus").

        Optional parameters:

        :param purge: flag. If set to True, all loci whose transcripts
        have scores of 0 will be thrown out
        into an Excluded holder.
        :type purge: bool

        :param excluded
        :type excluded: Excluded

        """
        if self.splitted is True:
            return

        self.excluded = excluded

        self.calculate_scores()

        graph = self.define_graph(self.transcripts, inters=self.is_intersecting,
                                  cds_only=self.json_conf["run_options"]["subloci_from_cds_only"])

        loci = []
        while len(graph) > 0:
            cliques, communities = self.find_communities(graph)
            to_remove = set()
            for locus_comm in communities:
                locus_comm = dict((x, self.transcripts[x]) for x in locus_comm)
                selected_tid = self.choose_best(locus_comm)
                selected_transcript = self.transcripts[selected_tid]
                to_remove.add(selected_tid)
                for clique in cliques:
                    if selected_tid in clique:
                        to_remove.update(clique)

                if purge is False or selected_transcript.score > 0:
                    new_locus = Locus(selected_transcript, logger=self.logger)
                    loci.append(new_locus)
            self.logger.debug("Removing {0} transcripts from {1}".format(len(to_remove), self.id))
            graph.remove_nodes_from(to_remove)  # Remove nodes from graph, iterate

        for locus in sorted(loci):
            self.loci[locus.id] = locus
        self.splitted = True
        return

    @classmethod
    def is_intersecting(cls, transcript, other, cds_only=False):
        """
        Implementation of the is_intersecting method. Now that we are comparing transcripts that
        by definition span multiple subloci, we have to be less strict in our definition of what
        counts as an intersection.
        Criteria:
        - 1 splice site in common (splice, not junction)
        - If one or both of the transcript is monoexonic OR
        one or both lack an ORF, check for any exonic overlap
        - Otherwise, check for any CDS overlap.

         :param transcript
         :type transcript; Transcript

         :param other:
         :type other: Transcript

         :param cds_only: boolean flag. If set to True, only
         the CDS component of the transcripts will be considered to determine
         whether they are intersecting or not.
         :type cds_only: bool


         :rtype : bool
        """

        if transcript.id == other.id or cls.overlap(
                (transcript.start, transcript.end),
                (other.start, other.end)) <= 0:
            return False  # We do not want intersection with oneself

        if not any([other.monoexonic, transcript.monoexonic]):
            if cds_only is False:
                if len(set.intersection(set(transcript.splices), set(other.splices))) > 0:
                    return True
            else:
                transcript_splices = set()
                for intron in transcript.combined_cds_introns:
                    transcript_splices.update(intron)
                for intron in other.combined_cds_introns:
                    if intron[0] in transcript_splices or intron[1] in transcript_splices:
                        return True
        elif (any([other.monoexonic, transcript.monoexonic]) or
              min(other.combined_cds_length,
                  transcript.combined_cds_length) == 0):
            if any(True for comb in itertools.product(transcript.exons, other.exons) if
                   cls.overlap(*comb) >= 0):
                return True

        # Finally check for CDS consistency
        return any(True for comb in itertools.product(
            transcript.combined_cds, other.combined_cds) if
                   cls.overlap(*comb) > 0)

    @classmethod
    def in_locus(cls, monosublocus: Abstractlocus, transcript: Transcript, flank=0) -> bool:
        """This method checks whether a transcript / monosbulocus
        falls inside the Locus coordinates.

        :rtype: bool

        :param monosublocus: Monosublocus instance
        :type monosublocus: Monosublocus

        :param transcript: the transcript to be compared
        :type transcript: Transcript

        :param flank: optional flank argument
        :type flank: int
        """
        if hasattr(transcript, "transcripts"):
            assert len(transcript.transcripts) == 1
            transcript = transcript.transcripts[list(transcript.transcripts.keys())[0]]
            assert hasattr(transcript, "finalize")
        is_in_locus = Abstractlocus.in_locus(monosublocus, transcript, flank=flank)
        if is_in_locus is True:
            is_in_locus = False
            for tran in monosublocus.transcripts:
                tran = monosublocus.transcripts[tran]
                is_in_locus = cls.is_intersecting(tran, transcript)
                if is_in_locus is True:
                    break
        return is_in_locus

    @property
    def id(self):
        """
        Wrapper for the id method of abstractlocus. Necessary to redefine the name.
        """

        return Abstractlocus.id.fget(self)  # @UndefinedVariable

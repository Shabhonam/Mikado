#!/usr/bin/env python3

"""
This module contains generic-purpose utilities to deal with BLAST XML files.
"""

import os
import subprocess
import gzip
import operator
import multiprocessing
import io
import collections
import time
import threading
import queue
import logging
from . import HeaderError
from ..utilities.log_utils import create_null_logger
from Bio.Blast.NCBIXML import parse as xparser

__author__ = 'Luca Venturini'


class BlastOpener:

    def __init__(self, filename):

        self.__filename = filename
        self.__handle = None
        self.__closed = False
        self.__opened = False
        self.__enter__()

    def __create_handle(self):

        if self.__closed is True:
            raise ValueError('I/O operation on closed file.')
        if self.__opened is True:
            return self

        if isinstance(self.__filename, (gzip.GzipFile, io.TextIOWrapper)):
            self.__handle = self.__filename
            self.__filename = self.__handle.name
        elif not isinstance(self.__filename, str) or not os.path.exists(self.__filename):
            raise OSError("Non-existent file: {0}".format(self.__filename))
        else:
            if self.__filename.endswith(".gz"):
                if self.__filename.endswith(".xml.gz"):
                    self.__handle = gzip.open(self.__filename, "rt")
                elif self.__filename.endswith(".asn.gz"):
                    # I cannot seem to make it work with gzip.open
                    zcat = subprocess.Popen(["zcat", self.__filename], shell=False,
                                            stdout=subprocess.PIPE)
                    blast_formatter = subprocess.Popen(
                        ['blast_formatter', '-outfmt', '5', '-archive', '-'],
                        shell=False, stdin=zcat.stdout, stdout=subprocess.PIPE)
                    self.__handle = io.TextIOWrapper(blast_formatter.stdout, encoding="UTF-8")
            elif self.__filename.endswith(".xml"):
                self.__handle = open(self.__filename)
                assert self.__handle is not None
            elif self.__filename.endswith(".asn"):
                blast_formatter = subprocess.Popen(
                    ['blast_formatter', '-outfmt', '5', '-archive', self.__filename],
                    shell=False, stdout=subprocess.PIPE)
                self.__handle = io.TextIOWrapper(blast_formatter.stdout, encoding="UTF-8")
            else:
                raise ValueError("Unrecognized file format: {}".format(self.__filename))

        self.__opened = True
        assert self.__handle is not None, self.__filename

    def __enter__(self):

        self.__create_handle()
        self.parser = xparser(self.__handle)
        return self

    def open(self):
        self.__enter__()

    def __exit__(self, *args):
        _ = args
        if self.__closed is False:
            self.__handle.close()
            self.__closed = True
            self.__opened = False

    def __iter__(self):
        return self

    def __next__(self):
        if self.__handle is None:
            raise ValueError("Invalid handle")
        return next(self.parser)

    def close(self):
        self.__exit__()

    def read(self, *args):
        return self.__handle.read(*args)

    def sniff(self, default_header=None):

        """
        Method that either derives the default XML header for the instance (if undefined)
        or checks that the given file is compatible with it.
        :param default_header: optional default header to check for consistency
        :return: boolean (passed or not passed)
        :rtype: (bool, list, str)
        """

        if self.__opened is True:
            self.close()
            self.__closed = False
            self.__opened = False
        self.__create_handle()

        header = []
        exc = None
        valid = True
        # assert handle is not None
        while True:
            try:
                line = next(self.__handle)
            except StopIteration:
                # Hack for empty files
                valid = False
                exc = HeaderError("Invalid header for {0}:\n\n{1}".format(
                    self.__filename,
                    "\n".join(header)
                ))
                break
            if "<Iteration>" in line:
                break
            line = line.rstrip()
            if not line:
                valid = False
                exc = HeaderError("Invalid header for {0}:\n\n{1}".format(
                    self.__filename,
                    "\n".join(header)
                ))
                break
            if len(header) > 10**3:
                exc = HeaderError("Abnormally long header ({0}) for {1}:\n\n{2}".format(
                    len(header),
                    self.__filename,
                    "\n".join(header)
                ))
                break
            header.append(line)
        if not any(iter(True if "BlastOutput" in x else False for x in header)):
            exc = HeaderError("Invalid header for {0}:\n\n{1}".format(
                self.__filename, "\n".join(header)))

        if default_header is not None and exc is None:
                checker = [header_line for header_line in header if
                           "BlastOutput_query" not in header_line]
                previous_header = [header_line for header_line in default_header if
                                   "BlastOutput_query" not in header_line]
                if checker != previous_header:
                    exc = HeaderError("BLAST XML header does not match for {0}".format(
                        self.__filename))
        elif exc is None:
            default_header = header

        if exc is not None:
            valid = False
        self.__handle.close()

        return valid, default_header, exc


def check_beginning(handle, filename, previous_header):

    """
    Static method to check that the beginning of the XML file is actually correct.

    :param handle: handle to the file to check.
    :param filename: name of the file associated with the handle.
    :type filename: str

    :param previous_header: header found in previous file(s).
    It is used the parameter used for the consinstency check.
    :type previous_header: (None | list)

    :return
    """

    exc = None
    header = []
    try:
        first_line = next(handle)
        first_line = first_line.strip()
        if first_line != '<?xml version="1.0"?>':
            exc = ValueError("Invalid header for {0}!\n\t{1}".format(filename, first_line))
            raise exc
        second_line = next(handle)
        second_line = second_line.strip()
        valid_schemas = [
            " ".join(['<!DOCTYPE BlastOutput PUBLIC "-//NCBI//NCBI BlastOutput/EN"',
                      '"http://www.ncbi.nlm.nih.gov/dtd/NCBI_BlastOutput.dtd">']),
            '<!DOCTYPE BlastOutput PUBLIC "-//NCBI//NCBI BlastOutput/EN" "NCBI_BlastOutput.dtd">'
        ]

        if second_line not in valid_schemas:
            exc = ValueError("Invalid XML type for {0}!\n\t{1}".format(filename, second_line))
            raise exc
        header = [first_line, second_line]
    except StopIteration:
        exc = OSError("Empty file: {0}".format(filename))
    except ValueError:
        pass

    if exc is not None:
        return handle, header, exc

    while True:
        line = next(handle)

        if "<Iteration>" in line:
            break
        line = line.rstrip()
        if not line:
            exc = HeaderError("Invalid header for {0}:\n\n{1}".format(
                filename,
                "\n".join(header)
            ))
            break
        if len(header) > 10**3:
            exc = HeaderError("Abnormally long header ({0}) for {1}:\n\n{2}".format(
                len(header),
                filename,
                "\n".join(header)
            ))
            break
        header.append(line)

    if not any(iter(True if "BlastOutput" in x else False for x in header)):
        exc = HeaderError("Invalid header for {0}:\n\n{1}".format(filename, "\n".join(header)))

    if previous_header is not None:
        checker = [header_line for header_line in header if
                   "BlastOutput_query" not in header_line]
        previous_header = [header_line for header_line in previous_header if
                           "BlastOutput_query" not in header_line]
        if checker != previous_header:
            exc = HeaderError("BLAST XML header does not match for {0}".format(
                filename))

    return handle, header, exc


def merge(intervals: [(int, int)]):
    """
    This function is used to merge together intervals, which have to be supplied as a list
    of duplexes - (start,stop). The function will then merge together overlapping tuples and
    return a list of non-overlapping tuples.
    If the list is composed by only one element, the function returns immediately.
    :param intervals: a list of integer duplexes
    :type intervals: list

    """

    # Assume tuple of the form (start,end)
    # And return 0- and 1-length intervals
    new_intervals = []
    for interval in intervals:
        new_intervals.append(tuple(sorted(interval)))

    intervals = new_intervals[:]
    if len(intervals) < 2:
        return intervals

    # Sort according to start, end
    intervals = sorted(intervals, key=operator.itemgetter(0, 1))
    final_list = [intervals[0]]

    for start, end in intervals[1:]:
        if start > final_list[-1][1]:
            final_list.append(tuple([start, end]))
        elif end > final_list[-1][1]:
            final_list[-1] = tuple([final_list[-1][0], end])
    return final_list


# This is a private class, it does not need public methods
# pylint: disable=no-member,too-few-public-methods
class _Merger(multiprocessing.Process):

    """
    This private class acts as a background process behind the XMLMerger class.
    This allows the XMLMerger class to appear like a normal read-only
    file-like objects, allowing compatibility with parsers such as
    e.g. Bio.Blast.NCBIXML.parse
    """

    def __init__(self, filenames, header, other_queue, logger=None):
        # pylint: disable=no-member
        multiprocessing.Process.__init__(self)
        # pylint: enable=no-member
        self.queue = other_queue
        self.filenames = filenames
        self.header = header
        self.logger = logger

    def run(self):
        """
        Implementation of the "run" method of the Process mother class.
        During the running, _Merger will perform the following:

        - check that the XML header is compatible
        - check that the file ends correctly
        - append the new lines to the stream

        WARNING: as it is impossible to look for the end of a
        gzipped file or of a stream, we have to keep all lines in memory
        to ascertain that the file we are trying to merge is not corrupt.
        This makes unfeasible to use the current implementation for
        merging large XML files.
        """

        # self.logger.info("Merger running")
        print_header = True

        for filename in self.filenames:
            self.logger.debug("Begun %s", filename)
            if print_header is True:
                # self.logger.info("Printing header")
                self.queue.put_nowait(self.header)
                print_header = False
            try:
                with BlastOpener(filename) as handle:
                    handle, _, exc = check_beginning(handle,
                                                     filename,
                                                     self.header)
            except OSError as exc:
                self.logger.exception(exc)
                continue
            except ValueError as exc:
                self.logger.exception(exc)
                continue

            if exc is not None:
                self.logger.exception(exc)
                self.logger.error("Skipped %s", filename)

                continue
            self.logger.debug("Finished parsing header for %s", filename)
            lines = collections.deque()
            lines.append("<Iteration>")
            bo_found = False
            for line in handle:
                if line.strip() == "":
                    continue
                if "BlastOutput" in line:
                    bo_found = True
                    break
                lines.append(line.rstrip())

            if bo_found is False:
                exc = ValueError("{0} is an invalid XML file".format(filename))
                self.logger.exception(exc)
                continue

            self.logger.debug("Finished parsing lines for %s", filename)
            self.queue.put_nowait(lines)
            self.logger.debug("Sent %d lines for %s", len(lines), filename)

        # We HAVE  to wait some seconds, otherwise the XML parser
        # might miss the end of the file.
        time.sleep(5)
        self.queue.put(["</BlastOutput_iterations>\n</BlastOutput>"])

        self.queue.put("Finished")
        return
# pylint: enable=no-member,too-few-public-methods


# pylint: disable=too-many-instance-attributes
class XMLMerger(threading.Thread):

    """
    This class has the purpose of merging on the fly multiple BLAST alignment
    files, be they in XML, XML.gz, or ASN.gz format. It uses the _Merger
    private class as a background process which bothers itself with the real
    work, while this class provides a file-like interface for external
    applications such Bio.Blast.NCBIXML.parse.
    """

    __name__ = "XMLMerger"
    logger = create_null_logger(__name__)

    def __init__(self, filenames, log_level=logging.WARNING, log=None):

        threading.Thread.__init__(self)
        self.logger.setLevel(log_level)
        if log is not None:
            self.file_handler = logging.FileHandler(log, "w")
            formatter = self.logger.handlers[0].formatter
            for null_handler in iter(handler for handler in self.logger.handlers if
                                     isinstance(handler, logging.NullHandler)):
                self.logger.removeHandler(null_handler)
            self.file_handler.setFormatter(formatter)
            self.logger.addHandler(self.file_handler)

        self.__filenames = collections.deque(filenames)
        self.__event = threading.Event()
        # pylint: disable=no-member
        manager = multiprocessing.Manager()
        # pylint: enable=no-member
        self.__queue = manager.Queue()
        self.lines = collections.deque()
        self.started = False
        self.finished = False
        if len(self.__filenames) > 0:
            while True:
                _, header, exc = check_beginning(
                    BlastOpener(self.__filenames[0]),
                    self.__filenames[0],
                    None)
                if exc is not None:
                    self.logger.exception(exc)
                    _ = self.__filenames.popleft()
                    continue
                self.header = header
                break
        self.logger.debug("Header has %d lines", len(self.header))
        if len(self.__filenames) == 0:
            raise IndexError("No files left!")

        self.merger = _Merger(self.__filenames, self.header, self.__queue, logger=self.logger)
        self.start()

    def run(self):

        """
        Method to start the process. Override of the original Thread method.
        :return:
        """

        # pylint: disable=no-member
        self.merger.start()
        # pylint: enable=no-member

        self.logger.info("Reader started")
        while True:
            try:
                lines = self.__queue.get_nowait()
            except queue.Empty:
                self.logger.debug("Queue was empty, waiting")
                time.sleep(0.01)
                continue
            if lines == "Finished":
                break
            self.logger.debug("Received %d lines", len(lines))
            self.lines.extend(lines)

        self.finished = True
        # pylint: disable=no-member
        self.merger.join()
        # pylint: enable=no-member
        return

    def read(self, size=None):
        """
        This method allows the XMLMerger class to act, for all purposes,
        like a file-like interface. The bytes are read from the queue,
        delivered by the background _Merger instance.
        :param size: optional parameter to indicate how much we want to read
        from the file-like interface.
        :return:
        """

        total = ""
        while len(self.lines) == 0:
            if self.finished is True:
                break
        if len(self.lines) == 0:
            raise StopIteration
        if size is None:
            while self.finished is False:
                time.sleep(0.1)
            total = self.lines
        else:
            previous_val = None
            import sys
            while sys.getsizeof(total) < size and len(self.lines) > 0:
                val = self.lines.popleft()
                if val == "</BlastOutput_iterations>\n</BlastOutput>":
                    self.logger.info("Received termination lines")
                    if previous_val is not None:
                        self.logger.info("Previous val: %s",
                                         previous_val[-2000:])
                total += val
                if previous_val is not None:
                    previous_val += val
                else:
                    previous_val = val

        total = total.rstrip()
        return total

    def __next__(self):

        while len(self.lines) == 0:
            if self.finished is True:
                break
        if len(self.lines) == 0:
            # Thread is finished and deque is exhausted. Finished
            raise StopIteration
        return self.lines.popleft()

    def __iter__(self):
        return self

    def __exit__(self, *args):
        _ = args
        self.join()

    def close(self):
        self.__exit__()

    def __enter__(self):
        pass
# pylint: enable=too-many-instance-attributes

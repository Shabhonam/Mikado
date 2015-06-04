#!/usr/bin/env python3

#import sys
#from logging import Logger
import re
import multiprocessing
import loci_objects
import csv
import os

class Creator:
    
    def __init__(self, json_conf):
        
        if type(json_conf) is str:
            assert os.path.exists(json_conf)
            json_conf = loci_objects.json_utils.to_json(json_conf) 
        else:
            assert type(json_conf) is dict
        
        self.json_conf = json_conf
        self.threads = self.json_conf["threads"]
        self.input_file = self.json_conf["input"]
        self.input = self.to_input(self.json_conf["input"])
        self.sub_out = self.json_conf["subloci_out"]
        self.monolocus_out = self.json_conf["monoloci_out"]
        self.locus_out = self.json_conf["loci_out"]
        
    def printer(self):

        '''Listener process that will print out the loci recovered by the analyse_locus function.'''
        
        self.sub_metrics=re.sub("$",".metrics.tsv",  re.sub(".gff3$", "", self.sub_out  ))
        self.sub_scores=re.sub("$",".scores.tsv",  re.sub(".gff3$", "", self.sub_out  ))
        self.locus_metrics = re.sub("$",".metrics.tsv",  re.sub(".gff3$", "", self.locus_out  ))
        self.locus_scores = re.sub("$",".scores.tsv",  re.sub(".gff3$", "", self.locus_out  ))
        
        score_keys = ["tid","parent","score"] + sorted(list(self.json_conf["scoring"].keys()))
        
        sub_metrics=csv.DictWriter(open(self.sub_metrics,'w'), loci_objects.superlocus.superlocus.available_metrics, delimiter="\t")
        sub_metrics.writeheader()
        sub_scores=csv.DictWriter(open(self.sub_scores,'w'), score_keys, delimiter="\t")
        sub_scores.writeheader()
        locus_metrics=csv.DictWriter(open(self.locus_metrics,'w'), loci_objects.superlocus.superlocus.available_metrics, delimiter="\t")
        locus_metrics.writeheader()
        locus_scores=csv.DictWriter(open(self.locus_scores,'a'), score_keys, delimiter="\t")
        locus_scores.writeheader()
        
        sub_out=open(self.sub_out,'w')
        mono_out=open(self.mono_out,'w')
        locus_out=open(self.locus_out,'w')
        
        print('##gff-version 3', file=sub_out)
        print('##gff-version 3', file=mono_out)
        print('##gff-version 3', file=locus_out)
        
        while True:
            stranded_locus=self.printer_queue.get()
            if stranded_locus=="EXIT":
                break #Poison pill - once we receive a "EXIT" signal, we exit
            sub_lines = stranded_locus.__str__(level="subloci", print_cds=not self.json_conf["run_options"]["exclude_cds"] )
            sub_metrics_rows = [x for x in stranded_locus.print_subloci_metrics()]
            sub_scores_rows = [x for x in stranded_locus.print_subloci_scores()]
            mono_lines = stranded_locus.__str__(level="monosubloci", print_cds=not self.json_conf["run_options"]["exclude_cds"])
            locus_metrics_rows=[x for x in stranded_locus.print_monoholder_metrics()]
            locus_scores_rows = [x for x in stranded_locus.print_monoholder_scores()]
            locus_lines = stranded_locus.__str__(print_cds=not self.json_conf["run_options"]["exclude_cds"])
            for row in sub_metrics_rows: sub_metrics.writerow(row)
            for row in sub_scores_rows: sub_scores.writerow(row)
            for row in locus_metrics_rows: locus_metrics.writerow(row)
            for row in locus_scores_rows: locus_scores.writerow(row)
            print(sub_lines, file=sub_out)
            if mono_lines!='':
                print(mono_lines, file=mono_out)
            if locus_lines!='':
                print(locus_lines, file=locus_out)    
        return
        
    def analyse_locus(self, slocus ):

        '''This function takes as input a "superlocus" instance and the pipeline configuration.
        It also accepts as optional keywords a dictionary with the CDS information (derived from a bed12Parser)
        and a "lock" used for avoiding writing collisions during multithreading.
        The function splits the superlocus into its strand components and calls the relevant methods
        to define the loci. It also prints out the results to the requested output files.
        '''
    
        #Load the CDS information
        slocus.load_transcript_data()
        #Split the superlocus in the stranded components
        stranded_loci = sorted(list(slocus.split_strands()))
        #Define the loci
        for stranded_locus in stranded_loci:
            stranded_locus.define_loci()
    
        #Remove overlapping fragments.
        #This part should be rewritten in order to make it more flexible and powerful.
        for stranded_locus in stranded_loci:
            if self.json_conf["run_options"]["remove_overlapping_fragments"] is True and len(stranded_loci)>1:
                for final_locus in stranded_locus.loci:
                    for other_superlocus in filter(lambda x: x!=stranded_locus, stranded_loci):
                        for other_final_locus in other_superlocus.loci:
                            if other_final_locus.other_is_fragment( final_locus ) is True and final_locus in stranded_locus.loci: 
                                stranded_locus.loci.remove(final_locus)

            self.printer_queue.put(stranded_locus)
        return

    def __call__(self):
        
        '''This method will activate the class and start the analysis of the input file.'''
        
        
        #NOTE: Pool, Process and Manager must NOT become instance attributes!
        #Otherwise it will raise all sorts of mistakes
        
        self.ctx = multiprocessing.get_context() # @UndefinedVariable 
        manager=self.ctx.Manager()
        self.printer_queue=manager.Queue()
        self.lock=manager.RLock()
        pool=ctx.Pool(processes=self.threads) # @UndefinedVariable
        printer_process=multiprocessing.Process(target=self.printer) # @UndefinedVariable
        printer_process.start()
        first = True    
        
        pool.close()
        pool.join()
        
        self.printer_queue.put("EXIT")
        printer_process.join()
        
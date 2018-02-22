#!/usr/bin/python2.7

'''
Stolen and slightly modified from @mscheremetjew (https://github.com/mscheremetjew)
Original script: https://raw.githubusercontent.com/ProteinsWebTeam/ebi-metagenomics/master/memi/memi-web/developers/python/mgportal_bulk_download.py
'''

import argparse
import csv
import os
import urllib
import urllib2
from urllib2 import URLError

# Parse script parameters
def interface(default_types):

    parser = argparse.ArgumentParser(description="MGPortal bulk download tool.")
    parser.add_argument("-p", "--project_id",
                        dest="PROJECT",
                        required=True,
                        help="Project accession (e.g. ERP001736, SRP000319) from a project which is publicly available on the EBI Metagenomics website (https://www.ebi.ac.uk/metagenomics/projects). Required.")
    parser.add_argument("-s", "--sample_id",
                        dest="SAMPLE",
                        help="Sample accession (e.g. SRS560248, ERS979832) from a sample which is publicly available on the EBI Metagenomics website (https://www.ebi.ac.uk/metagenomics/samples). Must be specified with a project ID.")
    parser.add_argument("-r", "--run_id",
                        dest="RUN",
                        help="Run accession (e.g. SRR1174061, ERR647655) from a run which is publicly available on the EBI Metagenomics website. Must be specified with a sample ID.")
    parser.add_argument("-o", "--output_path",
                        dest="OUT",
                        help="Location of the output directory, where the downloadable files get stored. Required.",
                        required=True)
    parser.add_argument("-v", "--version",
                        dest="version",
                        help="Version of the pipeline used to generate the results. Required.",
                        required=True)
    parser.add_argument("-t", "--file_type",
                        dest="type",
                        help="Supported file types are: AllFunction, AllTaxonomy, AllSequences OR a comma-separated list of supported file types: " + ', '.join(default_file_type_list) + " OR a single file type.\nDownloads all file types if not provided.",
                        required=False)
    parser.add_argument("--list-only",
                        dest="list_only",
                        help="Only lists the project runs without downloading them.",
                        action="store_true")
    parser.add_argument("-vb", "--verbose",
                        dest="verbose",
                        help="Switches on the verbose mode.",
                        action="store_true")

    args = parser.parse_args()
    return args

def _download_resource_by_url(url, output_file_name):
    """Kicks off a download and stores the file at the given path.
    Arguments:
    'url' -- Resource location.
    'output_file_name' -- Path of the output file.
    """
    print "Starting the download of the following file..."
    print url
    print "Saving file in:\n" + output_file_name

    try:
        urllib.urlretrieve(url, output_file_name)
    except URLError as url_error:
        print(url_error)
        raise
    except IOError as io_error:
        print(io_error)
        raise
    print "Download finished."


def _get_number_of_chunks(url_template, study_id, sample_id, run_id, version, domain, file_type):
    """
    Returns the number of chunks for the given set of parameters (study, sample and run identifier).
    """
    print "Getting the number of chunks from the following URL..."
    url_get_number_of_chunks = url_template % (
        study_id, sample_id, run_id, version, domain, file_type)
    print url_get_number_of_chunks
    try:
        file_stream_handler = urllib2.urlopen(url_get_number_of_chunks)
        result = int(file_stream_handler.read())
        print "Retrieved " + str(result) + " chunks."
        return result
    except URLError as url_error:
        print(url_error)
        raise
    except IOError as io_error:
        print(io_error)
        raise
    except ValueError as e:
        print(e)
        print "Skipping this run! Could not retrieve the number of chunks for this URL. " \
              "Check the version number in the URL and check if the run is available online."
        return 0


def _get_file_stream_handler(url_get_project_runs):
    """
    Returns a file stream handler for the given URL.
    """
    print "Getting the list of project runs..."
    try:
        req = urllib2.Request(url=url_get_project_runs, headers={'Content-Type': 'text/plain'})
        return urllib2.urlopen(req)
    except URLError as url_error:
        print(url_error)
        raise
    except  IOError as io_error:
        print(io_error)
        raise
    except ValueError as e:
        print(e)
        print "Could not retrieve any runs. Open the retrieval URL further down in your browser and see if you get any results back. Program will exit now."
        print url_get_project_runs
        raise


def _print_program_settings(project_id, sample_id, run_id, version, selected_file_types_list, output_path, root_url):
    print "Running the program with the following setting..."
    if project_id:
        print "Project: " + project_id
    if sample_id:
        print "Sample: " + sample_id
    if run_id:
        print "Run: " + run_id
    print "Pipeline version: " + version
    print "Selected file types: " + ",".join(selected_file_types_list)
    print "Root URL: " + root_url
    print "Writing result to: " + output_path


if __name__ == "__main__":
    function_file_type_list = ["InterProScan", "GOAnnotations", "GOSlimAnnotations"]
    sequences_file_type_list = ["ProcessedReads", "ReadsWithPredictedCDS", "ReadsWithMatches", "ReadsWithoutMatches", "PredictedCDS", "PredictedCDSWithoutAnnotation", "PredictedCDSWithAnnotation", "PredictedORFWithoutAnnotation", "ncRNA-tRNA-FASTA"]
    taxonomy_file_type_list = ["5S-rRNA-FASTA", "16S-rRNA-FASTA", "23S-rRNA-FASTA", "OTU-TSV", "OTU-BIOM", "OTU-table-HDF5-BIOM", "OTU-table-JSON-BIOM", "NewickTree", "NewickPrunedTree"]
    # Default list of available file types
    default_file_type_list = sequences_file_type_list + function_file_type_list + taxonomy_file_type_list

    args = interface(default_file_type_list)

    verbose = args.verbose
    list_only = args.list_only

    # Parse the project accession
    study = args.PROJECT
    sample = args.SAMPLE
    run = args.RUN

    # Parse the values for the file type parameter
    selected_file_types_list = []
    if not args.type:
        # If not specified use the default set of file types
        selected_file_types_list = default_file_type_list
    else:
        # Remove whitespaces
        selected_file_types_str = args.type.replace(" ", "")
        # Set all functional result file types
        if selected_file_types_str == "AllFunction":
            selected_file_types_list = function_file_type_list
        elif selected_file_types_str == "AllTaxonomy":
            selected_file_types_list = taxonomy_file_type_list
        elif selected_file_types_str == "AllSequences":
            selected_file_types_list = sequences_file_type_list
        # Set defined file types
        elif len(selected_file_types_str.split(",")) > 1:
            selected_file_types_list = selected_file_types_str.split(",")
        # Set single file type
        else:
            selected_file_types_list.append(selected_file_types_str)

    # Parse the analysis version
    version = args.version

    root_url = "https://www.ebi.ac.uk"
    query_url = root_url + "/metagenomics/projects/%s/runs" % (study)
    number_of_chunks_url_template = root_url + "/metagenomics/projects/%s/samples/%s/runs/%s/results/versions/%s/%s/%s/chunks"
    chunk_url_template = root_url + "/metagenomics/projects/%s/samples/%s/runs/%s/results/versions/%s/%s/%s/chunks/%s"
    download_url_template = root_url + "/metagenomics/projects/%s/samples/%s/runs/%s/results/versions/%s/%s/%s"

    # Print out the program settings
    _print_program_settings(study, sample, run, version, selected_file_types_list, args.OUT, root_url)

    # Iterating over all file types
    for file_type in selected_file_types_list:
        domain = None
        fileExtension = None
        # Boolean flag to indicate if a file type is chunked or not
        is_chunked = True
        # Set the result file domain (sequences, function or taxonomy) dependent on the file type
        # Set output file extension (tsv, faa or fasta) dependent on the file type
        if file_type == 'InterProScan':
            domain = "function"
            fileExtension = ".tsv.gz"
        elif file_type == 'GOSlimAnnotations' or file_type == 'GOAnnotations':
            domain = "function"
            fileExtension = ".csv"
            is_chunked = False
        # PredictedCDS is version 1.0 and 2.0 only, from version 3.0 on this file type was replaced by
        # PredictedCDSWithAnnotation (PredictedCDS can be gained by concatenation of the 2 sequence file types now)
        elif file_type == 'PredictedCDS' or file_type == 'PredicatedCDSWithoutAnnotation' or file_type == \
                'PredictedCDSWithAnnotation':
            if file_type == 'PredictedCDSWithAnnotation' and (version == '1.0' or version == '2.0'):
                print "File type '" + file_type + "' is not available for version " + version + "!"
                continue
            elif file_type == 'PredictedCDS' and version == '3.0':
                print "File type '" + file_type + "' is not available for version " + version + "!"
                continue
            domain = "sequences"
            fileExtension = ".faa.gz"
        elif file_type == 'ncRNA-tRNA-FASTA':
            domain = "sequences"
            fileExtension = ".fasta"
            is_chunked = False
        elif file_type == '5S-rRNA-FASTA' or file_type == '16S-rRNA-FASTA' or file_type == '23S-rRNA-FASTA':
            is_chunked = False
            domain = "taxonomy"
            fileExtension = ".fasta"
        # NewickPrunedTree is version 2 only
        # NewickTree is version 1 only
        elif file_type == 'NewickPrunedTree' or file_type == 'NewickTree':
            if file_type == 'NewickPrunedTree' and version == '1.0':
                print "File type '" + file_type + "' is not available for version " + version + "!"
                continue
            if file_type == 'NewickTree' and version == '2.0':
                print "File type '" + file_type + "' is not available for version " + version + "!"
                continue
            is_chunked = False
            domain = "taxonomy"
            fileExtension = ".tree"
        elif file_type == 'OTU-TSV':
            is_chunked = False
            domain = "taxonomy"
            fileExtension = ".tsv"
        # OTU-BIOM is version 1 only
        # OTU-table-HDF5-BIOM and OTU-table-JSON-BIOM are version 2 only
        elif file_type == 'OTU-BIOM' or file_type == 'OTU-table-HDF5-BIOM' or file_type == 'OTU-table-JSON-BIOM':
            if file_type == 'OTU-BIOM' and version == '2.0':
                print "File type '" + file_type + "' is not available for version " + version + "!"
                continue
            if (file_type == 'OTU-table-HDF5-BIOM' or file_type == 'OTU-table-JSON-BIOM') and version == '1.0':
                print "File type '" + file_type + "' is not available for version " + version + "!"
                continue
            is_chunked = False
            domain = "taxonomy"
            fileExtension = ".biom"
        else:
            domain = "sequences"
            fileExtension = ".fasta.gz"

        # Retrieve a file stream handler from the given URL and iterate over each line (each run) and build the download link using the variables from above

        file_stream_handler = _get_file_stream_handler(query_url)
        reader = csv.reader(file_stream_handler, delimiter=',')

        if list_only:
            for study_id, sample_id, run_id in reader:
                if (not sample) or (sample == sample_id):
                    if (not run) or (run == run_id):
                        print study_id + ", " + sample_id + ", " + run_id

        for study_id, sample_id, run_id in reader:
            if (not sample) or (sample == sample_id):
                if (not run) or (run == run_id):
                    print study_id + ", " + sample_id + ", " + run_id

                    if not args.OUT.endswith("/"):
                        output_path = args.OUT + "/"
                    else:
                        output_path = args.OUT

                    output_path = output_path + study_id + "/" + file_type
                    if not os.path.exists(output_path):
                        os.makedirs(output_path)

                    if is_chunked:
                        number_of_chunks = _get_number_of_chunks(number_of_chunks_url_template, study_id, sample_id, run_id,version, domain, file_type)

                        for chunk in range(1, number_of_chunks + 1):
                            output_file_name = output_path + "/" + run_id.replace(" ", "").replace(",", "-") + "_" + file_type + "_" + str(chunk) + fileExtension
                            rootUrl = chunk_url_template % (study_id, sample_id, run_id, version, domain, file_type, chunk)
                            _download_resource_by_url(rootUrl, output_file_name)
                    else:
                        output_file_name = output_path + "/" + run_id.replace(" ", "").replace(",", "-") + "_" + file_type + fileExtension
                        rootUrl = download_url_template % (study_id, sample_id, run_id, version, domain, file_type)
                        _download_resource_by_url(rootUrl, output_file_name)

    print "Program finished."

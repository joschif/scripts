#!/usr/bin/python3


'''
Command line tool for downloading raw reads form ENA

URL scaffold for run list:
https://www.ebi.ac.uk/ena/data/warehouse/filereport?accession=<ACCESSION_ID>&result=read_run&fields=study_accession,sample_accession,secondary_sample_accession,experiment_accession,run_accession,tax_id,scientific_name,instrument_model,library_layout,fastq_ftp,fastq_galaxy,submitted_ftp,submitted_galaxy,sra_ftp,sra_galaxy,cram_index_ftp,cram_index_galaxy&download=txt

Parses FTP addresses from the returned list and downloads the read files individually.
'''


import argparse
import os
import urllib.request
from urllib.parse import urlparse
from urllib.error import HTTPError

# FUNC
def interface():

    parser = argparse.ArgumentParser(description="ENA Downloader.")
    parser.add_argument("ID",
                        help="Project, sample or run accession (e.g. ERP001736, SRP000319) from a project which is publicly available on the ENA Website (https://www.ebi.ac.uk/).",
                        nargs='+')
    parser.add_argument("-o", "--output_path",
                        dest="OUT",
                        help="Location of the output directory, where the downloadable files get stored. If not specified, the downloader will load all raw files in the current working directory.")  
    parser.add_argument("--verbose",
                        dest="verbose",
                        help="Switches on the verbose mode.",
                        action="store_true")
    parser.add_argument("-t", "--type",
                        dest="read_type",
                        default="fastq_ftp",
                        help="Type of reads you want to download. Options are: fastq_ftp, fastq_galaxy, submitted_ftp, submitted_galaxy.")

    args = parser.parse_args()
    return args


def make_runlist_url(acc_id):
    """ Makes URL to get run list of accession ID
    """
    
    root_url = "https://www.ebi.ac.uk/"
    query = "ena/data/warehouse/filereport?accession={0}&result=read_run&fields=".format(acc_id)
    fields = "study_accession,sample_accession,secondary_sample_accession,experiment_accession,run_accession,tax_id,scientific_name,instrument_model,library_layout,fastq_ftp,fastq_galaxy,submitted_ftp,submitted_galaxy,sra_ftp,sra_galaxy,cram_index_ftp,cram_index_galaxy"
    query_url = root_url + query + fields + "&download=txt"
    return query_url


def get_runlist(url):
    """ Returns the response for a given URL
    """
    
    try:
        return urllib.request.urlopen(url)
    except HTTPError as http_err:
        print('\nThe generated URL {0} cound not be opened. Maybe the accession ID was not valid. \n'.format(url))
        pass
    except IOError as io_err:
        print(io_err)
        raise


def download_reads(url, output_path):
    """ Downloads the contents of a given URL
    """

    try:
        urllib.request.urlretrieve(url, output_path)
        return True
    except HTTPError:
        print("\nThe read file with the URL {0} cound not be downloaded. \n".format(url))
        return False
    except IOError as io_err:
        print(io_err)
        raise  


# MAIN
if __name__ == "__main__":
    args = interface()
    verbose = args.verbose

    output_dir = args.OUT
    if output_dir:
        subdir = True
        if not output_dir.endswith('/'):
            output_dir += '/'
    else:
        subdir = False
        output_dir = './'

    acc_ids = args.ID
    read_type = args.read_type

    for acc_id in acc_ids:
        query_url = make_runlist_url(acc_id)
        run_list_response = get_runlist(query_url)

        if not run_list_response:
            continue

        header = run_list_response.readline().decode("utf8").strip().split('\t')
        try:
            target_col = header.index(read_type)
        except ValueError:
            print("\nThe read type {0} was not found in the run list. Maybe try a different one or check the ENA website.\n".format(read_type))
            raise

        
        for line in run_list_response:
            line = line.decode("utf8").strip().split('\t')
            project_id = line[0]
            sample_id = line[1]
            run_id = line[4]
            layout = line[8]
            fastq_files = line[target_col].split(';')
            fastq_names = []

            if verbose:
                print("Downloading files:\n{0}".format(fastq_files))

            if subdir:
                logout = "{0}{1}/".format(output_dir,project_id)
                out = "{0}{1}/{2}/".format(output_dir, project_id, sample_id)
                try:
                    os.makedirs(out)
                except FileExistsError:
                    pass
            else:
                logout = output_dir
                out = output_dir

            for f in fastq_files:
                fastq_url = "ftp://" + f
                fastq_name = f.split('/')[-1]
                output_path = out + fastq_name
                success = download_reads(fastq_url, output_path)
                fastq_names.append(fastq_name)

            if success:
                if verbose:
                    print("Success.")
                with open(logout + "runs.log", 'a') as log:
                    log.write('\t'.join([run_id, layout] + fastq_names) + '\n')





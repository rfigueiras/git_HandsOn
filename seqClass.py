#!/usr/bin/env python

import sys, re
from argparse import ArgumentParser

parser = ArgumentParser(description = 'Classify a sequence as DNA or RNA')
parser.add_argument("-s", "--seq", type = str, required = True, help = "Input sequence")
parser.add_argument("-m", "--motif", type = str, required = False, help = "Motif")

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()
#convert string to upper case
args.seq = args.seq.upper()
#check if sequence contains the following pattern with classical nucleotides
# added  binary nucleotides codes on fix 
if re.search('^[ACGTUNRY]+$', args.seq):
    if 'T' in args.seq and 'U' in args.seq:
        print('The sequence is invalid: contains both T and U.') #added on fix, sequence is invalid with this 2 nucleotides
    elif  re.search('T', args.seq):
        print ('The sequence is DNA') #if sequence has T is DNA
    elif re.search('U', args.seq):
        print ('The sequence is RNA') #if sequence has U is RNA
    else:
        print ('The sequence can be DNA or RNA') 
else:
    print ('The sequence is not DNA nor RNA')


#To check if motif is in sequence (optional -m argument)
if args.motif:
    args.motif = args.motif.upper()
    print(f'Motif search enabled: looking for motif "{args.motif}" in sequence "{args.seq}"... ', end = '')
    if re.search(args.motif, args.seq):
        print("Found!")
    else:
        print("NOT Found!")


#!/bin/bash

# Copyright 2012  Microsoft Corporation  Johns Hopkins University (Author: Daniel Povey)
#           2015  Guoguo Chen
# Apache 2.0

# This script takes data prepared in a corpus-dependent way
# in data/local/, and converts it into the "canonical" form,
# in various subdirectories of data/, e.g. data/lang, data/lang_test_ug,
# data/train_si284, data/train_si84, etc.

# Don't bother doing train_si84 separately (although we have the file lists
# in data/local/) because it's just the first 7138 utterances in train_si284.
# We'll create train_si84 after doing the feature extraction.

echo "$0 $@"  # Print the command line for logging
. utils/parse_options.sh || exit 1;

echo "Preparing train and test data"
srcdir=data/wsj/local/data

for x in train_si284 test_eval92 test_dev93; do
  mkdir -p data/wsj/$x
  cp $srcdir/${x}_wav.scp data/wsj/$x/wav.scp || exit 1
  cp $srcdir/$x.txt data/wsj/$x/text || exit 1
  scripts/get_wav_dur.sh --nj 4 --output "time" data/wsj/$x exp/utt2dur/$x
done

echo "Succeeded in formatting data."

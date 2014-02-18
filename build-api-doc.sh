#!/bin/sh

#
MY_DIR=$(cd $(dirname $0); pwd)
SRC_DIR=$MY_DIR/src
API_DOC_DIR=$MY_DIR/api-doc

#
export PYTHONPATH=$SRC_DIR:$PYTHONPATH

cd $MY_DIR
sphinx-apidoc -F -f -o $API_DOC_DIR $SRC_DIR/g4s

cd $API_DOC_DIR
if [ $# -eq 0 ]; then
    make html
else
    while [ "$1" != "" ]; do
        make $1
        shift
    done
fi

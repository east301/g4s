#!/bin/sh

# configuration
MY_DIR=$(cd $(dirname $0); pwd)
SRC_DIR=$MY_DIR/src
API_DOC_DIR=$MY_DIR/api-doc

# runs `sphinx-apidoc`
export PYTHONPATH=$SRC_DIR:$PYTHONPATH

cd $MY_DIR
sphinx-apidoc -F -f -o $API_DOC_DIR $SRC_DIR/g4s

# modifies configuration
cd $API_DOC_DIR

cat >> conf.py <<EOF
# -- autodoc configuration ------------------------------------------------
autoclass_content = 'both'  # shows docstring of __init__
EOF

# builds api documents
if [ $# -eq 0 ]; then
    make html
else
    while [ "$1" != "" ]; do
        make $1
        shift
    done
fi

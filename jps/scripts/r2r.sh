#!/bin/bash

# R2R aliases
function r2r-mkcons {
	# Usage: r2r-mkcons <name>.sto
    r2r --GSC-weighted-consensus "$1" "${1%sto}cons.sto" \
        3 0.97 0.9 0.75 4 0.97 0.9 0.75 0.5 0.1
}

function r2r-mkpdf-cons {
	# Usage: r2r-mkpdf-cons <name>.cons.sto
    r2r --disable-usage-warning "$1" "${1%cons.sto}pdf"
}

function r2r-mkpdf-meta {
	# Usage: r2r-mkpdf-meta <name>.r2r_meta
    r2r --disable-usage-warning "$1" "${1%r2r_meta}pdf"
}

# Run r2r on the stockholm file
path=$1
r2r-mkcons "$path"
r2r-mkpdf-cons "${path%sto}cons.sto"

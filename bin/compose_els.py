#!/usr/bin/env python
#
#   A General purpose script for copying a script verbatim into another one.
#   Example:
#       ./bin/compose_els.py ./src/ interactivity.els_tmp src/interactivity.els
#   This will replace all instances of {{{<filename>}}} with the source code 
#   from the file ./src/<filename> in interactivity.els_tmp and save it to
#   src/interactivity.els.
#
import os,re,sys,glob

def get_replacement_lines( out, source_dir, name, indent=" "*12 ):
    path = os.path.join( source_dir, name )
    if os.path.isfile( path ):
        print "Found and merging: %s"%name
        with open( path, 'r' ) as tmp:
            for line in tmp:
                out.write(indent+line)
    else:
        print "Could not find: %s"%path
        exit(1)

def main( args ):
    source_dir,dummy_file,out_file = args[1:4]
    print "%s => %s"%(dummy_file,out_file)
    with open( out_file, 'w' ) as of:
        with open( dummy_file, 'r' ) as df:
            for line in df:
                match = re.match('\{\{\{(.+)\}\}\}', line)
                if match:
                    name = match.group(1) 
                    get_replacement_lines( of, source_dir, name )
                else: of.write( line )

if __name__ == "__main__": 
    if len(sys.argv) < 4:
        print "Usage: %s <source_dir> <dummy_file> <out_file>"%sys.argv[0]
        exit(1)
    main( sys.argv )
    

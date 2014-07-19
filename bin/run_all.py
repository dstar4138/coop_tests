#!/usr/bin/env python
#
# Batch script entry point for running all possible tests. 
#
import os,re,sys,glob,time,subprocess

#Testset generation
from math import floor
import multiprocessing as mp

# Utilizes GNU coreutils 'timeout' command to automatically kill 
# after timeout threshold has been reached. By default we limit each
# run to 2 minutes. We will log the error for user retrial.
#
# Please see the following for details:
# https://www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html
TIMEOUT = "5m"

# Some CONSTANTS pulled over from the ErLam Compiler. These are purely for 
# simulation purposes and we therefore test particular bounds surrounding them.
BATCH_SIZE     = 10 # num of procs in a batch where applicable.
THREAD_QUANTUM = 20 # num of reductions.


def relocate_log( new_path, append=""):
    """ Any log files found will be moved into a 
        particular subdirectory, given in arguments.
    """
    append = '-'.join(filter(None,re.split('(?!([a-zA-Z0-9-\._])).{1}',append)))
    for logfile in glob.glob("*.log"):
        newname = new_path + logfile[:-4] + append + ".log"
        os.rename(logfile, newname) # also relocates it.

def log( status, t, msg ):
    """ Log a message via color logging (for quick recognition) if avaliable.
        Otherwise, just print the message without coloring.
    """
    if sys.stdout.isatty(): color_log( status, t, msg )
    else: print ("SUCCESS(%ds):"%t if not status else "ERROR(%d):"%status), msg
def color_log( status, t, msg ):
    attr=('31',"ERROR(%d): "%status) #RED
    if not status: attr=('32',"SUCCESS(%ds): "%t) #GREEN
    print ('\x1b[%sm%s\x1b[0m' % attr)+msg

def make_results_dir(): 
    """ Make a timestamped results directory for all tests."""
    resdir = "results_%d" % int(time.time())
    os.mkdir(resdir)
    return resdir+"/"

def run_test( outpath, cmd, test_range, args=[] ):
    """ Run a set of tests for a particular command. 
        Example: 
            run_test( "results/ptree-modN/", 
                      "./src/ptree.ex", ["1,2,20,20",
                                         "2,2,20,20",
                                         "3,2,20,20",
                                         ... ],
                      [ "-s", "erlam_sched_multi_global" ] )
    """
    global TIMEOUT
    prepend = [ "timeout", "-k", TIMEOUT, TIMEOUT] # FORCE KILL AT TIMEOUT
    os.makedirs( outpath )
    for test in test_range:
        run = [ cmd, "-v", "-r", test ] + args
        t = time.time()
        res = subprocess.call( prepend + run )
        t = time.time()-t
        log( res, t, ' '.join(run) )
        relocate_log( outpath, test )

def build_run_tests( resdir, test_fun, args=[] ):
    """ Runs through the return of a test function. """
    print test_fun.__doc__
    for (test_def, test_name, script, test_range) in test_fun():
        print test_def
        run_test( resdir+test_name+"/", 
                  script,
                  test_range,
                  ["-s", "erlam_sched_single"]
                  ) #TODO: Add args=["-s",CUR_SCHEDULER]
    print "--"

### ==========================================================================
### TEST DEFINITIONS:
### ==========================================================================

def chugmachine_tests(): 
    """======================================================================
    ChugMachine Tests:
 ======================================================================"""
    tests = []
    script = "./src/chugmachine.ex"

    test_def = \
    """ 
    Generate several sets of tests for each combination of:
            0 < N < P+3   and   A in { C/2 , C , C*2 }   and   B = A - 1 
            When N is the number of processes which chug for a random amount
              of time between [B, A).
    """
    test_name = "chugmachine-modN-C"
    test_range = []
    default = "%d,%d,%d"
    for n in range(1, mp.cpu_count()+3):
        for a in [ THREAD_QUANTUM/2, THREAD_QUANTUM, THREAD_QUANTUM*2 ]:
            test_range.append( default % (n,a,a-1) )
    tests.append( (test_def, test_name, script, test_range) )
   
    # ???: Any other tests for ChugMachine
    return tests

# --------------------------------------------------------------------------- #
def pring_tests(): 
     """ ======================================================================
     PRing Tests:
  ======================================================================"""
     tests = []
     script = "./src/pring.ex"

     test_def = \
     """
     Generate a set of tests for: N in { 2, 4, .. P, B-1, B, 2*B }
         Where B is the batch size, P is the number of processors, and 
            therefore N is the number of processes in the ring.
         Note that we keep a constant amount of time for loops around the ring,
            and the time to chug at each location in the ring.
     """
     test_name = "pring-modN"
     test_range = []
     default = "%d,5,5" # Default for times to pass token around, times to chug.
     test_p = range( 2, mp.cpu_count()+2, 2 )
     for p in test_p: test_range.append( default % p )
     for b in [BATCH_SIZE-1, BATCH_SIZE, BATCH_SIZE*2]:
         if b in test_p: continue
         test_range.append( default % b )
     tests.append( (test_def, test_name, script, test_range) )
   
     # ???: Any other tests for PRing
     return tests 

# --------------------------------------------------------------------------- #
def clustercomm_tests(): 
    """======================================================================
    ClusterComm Tests:
 ======================================================================"""
    tests = []
    script = "./src/clustercomm.ex"

    test_def = \
    """
    Generate a set of tests: 
        N in { 2, 4, .., P, B, 2*B}   and   0 < M < floor(N/2) +1
        Note we keep the number of times each process synchronizes constant.
    """
    test_name = "clustercomm-modNM"
    test_range = []
    default = "%d,%d,5"
    test_p = range( 2, mp.cpu_count()+2, 2 )
    for b in [BATCH_SIZE-1, BATCH_SIZE, BATCH_SIZE*2]:
         if b in test_p: continue
         test_p.append(b) 
    for n in test_p:
        for m in range(1, int(floor(n/2)+1)):
            test_range.append( default % (n,m) )
    tests.append( (test_def, test_name, script, test_range) )

    # ???: Any other tests for ClusterComm
    return tests

# --------------------------------------------------------------------------- #
def ptree_tests():
    """======================================================================
    PTree Tests:
 ======================================================================"""
    tests = []
    script = "./src/ptree.ex"

    test_def = \
    """ 
    Generate a set of tests: 0 < N < P+2
        Where N is the number of work-groups and P is number of cores.
        Note that we keep members of work-group constant to below batch 
           size as tests for batch size modulation are in clustercomm.
        Note we keep sync time and chug time constant, modulation of work
           amount will be modulated in chugmachine.
    """
    test_name = "ptree-modN"
    test_range = []
    default="%d,10,10,5" # Default for batch size, synch count, chug count
    for num_lpu in range(1, mp.cpu_count()+2): 
        test_range.append( default % num_lpu )
    tests.append( (test_def, test_name, script, test_range) ) 

    # ???: Any other tests for PTree
    return tests

# --------------------------------------------------------------------------- #
def jumpship_tests(): 
    """======================================================================
    JumpShip Tests:
 ======================================================================"""
    tests = []
    script = "./src/jumpship.ex"

    test_def = \
    """ 
    Generate a set of tests: 0 < N < P+2  and  0 < H < 4
        Where N is the number of work-groups and P is number of cores.
        Where H is the number of times the phase changes.
    """
    test_name = "jumpship-modN"
    test_range = []
    default="%d,%d,10,5,%d" # Default for batch size, chug count, synch count
    for h in range(1, 4):
        for n in range(1, mp.cpu_count()+2):
            test_range.append(default % (5*n,n,h))
    tests.append( (test_def, test_name, script, test_range) )
       
    # ???: Any other tests fro JumpShip
    return tests

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
def interactivity_tests(): return []

# --------------------------------------------------------------------------- #
def unstructured_component_tests(): return []

## 
## MAIN: Run all tests.
##
if __name__ == "__main__":
    # Check we are being run from ./coop_tests/ and not inside bin.
    if not glob.glob("src"): 
        os.chdir('..')
        if not glob.glob("src"):
            log(1,"UNABLE TO FIND SCRIPT DIRECTORY!") ; exit(1)

    # Check that user compiled.
    if not len(glob.glob("src/*.ex")):
        log(1, "PLEASE RUN 'make' FIRST!") ; exit(1)

    # Run All Tests!
    resdir = make_results_dir()
    [ build_run_tests( resdir, test_fun ) 
            for test_fun 
            in [ # Basic Tests
                    chugmachine_tests,
                    pring_tests,
                    clustercomm_tests,
                    ptree_tests,
                    jumpship_tests,
                 # Composed Tests
                    interactivity_tests,
                    unstructured_component_tests ]]


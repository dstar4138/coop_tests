# Test Results

The above directories are separated first by scheduler, and then by channel
mechanism (cb = Blocking channel, ca = Process Absorption). Within each of 
these directories, we have the particular tests and then the raw, unprocessed
logs for each of those tests as output by ErLam.

Testing Machine:
Ubuntu 12.10 with kernel 3.5.0-46-generic on 
Intel Core i7-2820QM 2.3Ghz, 8GB Memory.


### Updates

I have most logs which resulted in a timeout (after 5 minutes of CPU time) or
were force canceled by myself (due to the certainty of hitting it's timeout). 
You can see the particulars of this execution in the `summary.log` file.


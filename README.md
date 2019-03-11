# Benchutils

* `StatStream` keep tracks of each iteration and compute `average`, `min`, `max`, `sd`, `total`.
* `call_graph` use `pycallgraph` to generate a call graph. The functionality can be disabled using the `NO_CALL_GRAPHS` flag
* `chrono` function decorator to check the runtinme of the function
* `MultiStageChrono` chrono that start a new stage every time start is called a report can be generated later on
* `versioning` retrieve the git commit hash and git commit time to keep track of performance as code evolve
* `report` generate a simple CSV/markdown table from python lists 


# Example

## StatStream

StatStream is thread safe and multiprocessing friendly (it will sync across processes)

    # Drop the first 5 observations
    
    stat = StatStream(drop_first_obs=5)
    
    for i in range(0, 10):
        start = time.time()
        
        something_long()
        
        stat.update(time.time() - start)
        
        
    stat.avg
    stat.max
    stat.min
    stat.count  # == 5
    stat.sd     
    
# Multi Stage Chrono

    chrono = MultiStageChrono(2)

    for i in range(0, 10):

        with chrono.time('forward_back'):
            with chrono.time('forward'):
                time.sleep(1)

            with chrono.time('backward', skip_obs=3):
                time.sleep(1)

    chrono.report()
    
Output

            Stage , Average , Deviation ,    Min ,    Max , count 
     forward_back ,  2.0019 ,    0.0003 , 2.0013 , 2.0022 ,     8 
          forward ,  1.0007 ,    0.0003 , 1.0001 , 1.0010 ,     8 
         backward ,  1.0010 ,    0.0000 , 1.0010 , 1.0011 ,     7 


    
# Versioning


    import my_module
    
    # return commit hash and commit date
    get_git_version(my_module)
    
    # return sha256 of the given file
    get_file_version(__file__)
    
   
# Chrono


    @chrono
    def my_function():
        pass
        
# Report

    print_table(
        ['A', 'B', 'C'],
        [
            [1, 2, 3],
            [1, 2, 3],
            [1, 2, 3],
            [1, 2, 3],
        ]
    )
   
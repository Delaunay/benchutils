# Benchutils

* `StatStream` keep tracks of each iteration and compute `average`, `min`, `max`, `sd`, `total`.
* `call_graph` use `pycallgraph` to generate a call graph. The functionality can be disabled using the `NO_CALL_GRAPHS` flag
* `chrono` function decorator to check the runtinme of the function
* `MultiStageChrono` chrono that start a new stage every time start is called a report can be generated later on
* `versioning` retrieve the git commit hash and git commit time to keep track of performance as code evolve
* `report` generate a simple CSV/markdown table from python lists 


# Example

## StatStream

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
    
    
# Versioning


    import my_module
    
    get_git_version(my_module)
    
   
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
   
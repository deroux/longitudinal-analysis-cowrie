#!/usr/bin/python3
import collections
import itertools
import multiprocessing
import time

import tqdm


class MapReduce(object):
    def __init__(self, map_func, reduce_func, num_workers=multiprocessing.cpu_count() * 2):  #
        """
        Performs a parallel mapreduce using multiprocessing on local machine using local files.

        Args:
            map_func
              Map inputs to intermediate data. Moved to external file Map.py for remote execution.
              Input: Value.
              Output: Tuple with key and value to be reduced e.g. (date:sensor:username:password, 1)

            reduce_func
              Reduce partitioned intermediate data of map function to final & readable output. Moved to external file Reduce.py for remote execution.
              Input: Key as argument produced by map_func, sequence of values associated with that key.
              Output: Reduced / aggregated output for each key.

            num_workers
              #Workers in pool.
              Default: # of available virtual cores of the current host.
        """
        self.map_func = map_func
        self.reduce_func = reduce_func
        self.pool = multiprocessing.Pool(num_workers)

    def partition(self, mapped_values):
        """Organize mapped values by key.
        Args:
            mapped_values (dict): Sequence of tuples of mapped_data.
        Returns:
            partitioned_data (dict): Sorted sequence (by key) of tuples with (key, sequence of values).
        """
        partitioned_data = collections.defaultdict(list)

        for key, value in mapped_values:
            partitioned_data[key].append(value)

        return partitioned_data.items()

    def __call__(self, inputs, chunksize=1):
        """Process inputs through map, partition, reduce functions.
        Args:
            inputs (Iterable):          Input data to be processed.
            chunksize (int, default=1): Portion of input data to hand to each worker.
                                        Might be used to adapt performance in mapping process.
        Returns:
            partitioned_data (dict): Sorted sequence (by key) of tuples with (key, sequence of values).
        """
        # imap / map problem
        # https: // stackoverflow.com / questions / 26520781 / multiprocessing - pool - whats - the-difference-between-map-async-and-imap
        print("map...")
        map_responses = []

        start = time.time()
        for _ in tqdm.tqdm(self.pool.imap_unordered(self.map_func, inputs, chunksize=chunksize), total=len(inputs)):
            map_responses.append(_)
            pass
        end = time.time()
        print("Map time:  \t     {:10.2f} s {:10.2f} min".format((end - start), (end - start) / 60))

        start = time.time()
        print("partition...")
        partitioned_data = self.partition(itertools.chain(*map_responses))

        print("reduce...")
        reduced_values = []
        for _ in tqdm.tqdm(self.pool.map(self.reduce_func, partitioned_data), total=len(partitioned_data)):
            reduced_values.append(_)
            pass
        end = time.time()
        print("Reduce time:  \t     {:10.2f} s {:10.2f} min".format((end - start), (end - start) / 60))

        return reduced_values

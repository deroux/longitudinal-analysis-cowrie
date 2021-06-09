#!/usr/bin/python3
import collections
import itertools
import multiprocessing
import tqdm


class MapReduce(object):
    def __init__(self, map_func, reduce_func, num_workers=multiprocessing.cpu_count() * 2):  #
        """
        map_func

          Map inputs to intermediate data.
          Input: Value.
          Output: Tuple with key and value to be reduced e.g. (username:password, 1)

        reduce_func

          Reduce partitioned version of intermediate data of map function to final & readable output.
          Input: Key as argument produced by map_func and sequence of values associated with that key.
          Output: Reduced / aggregated output for each key.

        num_workers

          Workers in the pool.
          Default: Number of available CPUs of the current host.
        """
        self.map_func = map_func
        self.reduce_func = reduce_func
        self.pool = multiprocessing.Pool(num_workers)

    def partition(self, mapped_values):
        """Organize mapped values by their key.
        Returns an unsorted sequence of tuples with a key and a sequence of values.
        """
        partitioned_data = collections.defaultdict(list)

        for key, value in mapped_values:
            partitioned_data[key].append(value)

        return partitioned_data.items()

    def __call__(self, inputs, chunksize=1):
        # imap / map problem
        # https: // stackoverflow.com / questions / 26520781 / multiprocessing - pool - whats - the-difference-between-map-async-and-imap
        """Process the inputs through the map and reduce functions given.

        inputs
          An iterable containing the input data to be processed.

        chunksize=1
          The portion of the input data to hand to each worker.  This
          can be used to tune performance during the mapping phase.
        """
        print("map...")
        map_responses = []
        for _ in tqdm.tqdm(self.pool.imap_unordered(self.map_func, inputs, chunksize=chunksize), total=len(inputs)):
            map_responses.append(_)
            pass

        print("partition...")
        partitioned_data = self.partition(itertools.chain(*map_responses))

        print("reduce...")
        reduced_values = []
        for _ in tqdm.tqdm(self.pool.map(self.reduce_func, partitioned_data), total=len(partitioned_data)):
            reduced_values.append(_)
            pass
        return reduced_values

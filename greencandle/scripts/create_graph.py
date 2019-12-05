#!/usr/bin/env python

"""
Standalone script for generating graphs from data in redis
"""

import argparse
import argcomplete

from greencandle.lib import config
from greencandle.lib.graph import Graph
config.create_config()
from greencandle.lib.mysql import Mysql

def main():
    """Main function"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--db", required=True)
    parser.add_argument("-a", "--active_pairs", action="store_true", required=False, default=False)
    parser.add_argument("-p", "--pair", required=False)
    parser.add_argument("-i", "--interval", required=False)
    parser.add_argument("-t", "--test", action="store_true", default=False, required=False)
    parser.add_argument("-o", "--output_dir", required=True)
    argcomplete.autocomplete(parser)
    args = parser.parse_args()


    if args.active_pairs:
        dbase = Mysql()
        results = dbase.fetch_sql_data("select pair, `interval` from trades where "
                                       "sell_price is NULL", header=False)

        for pair, interval in results:
            graph = Graph(test=args, pair=pair, db=args.db, interval=interval)
            graph.get_data()
            graph.create_graph(args.output_dir)
    else:
        graph = Graph(test=args, pair=args.pair, db=args.db, interval=args.interval)
        graph.get_data()
        graph.create_graph(args.output_dir)

if __name__ == '__main__':
    main()

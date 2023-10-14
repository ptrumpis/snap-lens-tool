#!/usr/bin/env python3

import argparse

import numpy as np


# Hash method from Boost
def hash_combine(seed, value, dt=np.uint64):
    return seed ^ (value + dt(0x9e3779b9) + (seed << dt(6)) + (seed >> dt(2)))


def calc_hash(data):
    dt = np.uint64
    dtype = np.dtype(dt).newbyteorder("<")
    padding = bytes(8 - (len(data) % 8))

    np.seterr(over="ignore")
    h = dt(0)
    for n in np.frombuffer(data + padding, dtype):
        h = hash_combine(h, n, dt)
    h = hash_combine(h, dt(len(data)), dt)
    np.seterr(over="warn")

    return h


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Hash a file using Snapchat's hashing method")
    parser.add_argument("input", help="input file")
    args = parser.parse_args()

    with open(args.input, "rb") as f:
        data = f.read()

    h = calc_hash(data)
    print(h)

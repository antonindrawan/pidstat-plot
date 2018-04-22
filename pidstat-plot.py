#! /usr/bin/env python
# -*- coding: utf-8 -*

import argparse
import matplotlib.pyplot as plt
import os
import re
import sys

class PidstatFileParser:
  pidstat_output_file = ""

  UID_PATTERN = re.compile(" UID ")

  def __init__(self, pidstat_output_file):
    self.pidstat_output_file = pidstat_output_file


  def parse(self):
    with open(self.pidstat_output_file, "r") as f:
      lines = f.readlines()

    self.split_header_and_content(lines)

  def split_header_and_content(self, lines):
    headers = None
    data_content = []

    for line in lines:
      line = line.strip()

      if (headers is None):
        matches = self.UID_PATTERN.search(line)
        if matches:
          headers = line.split()
      else:
        # TODO: We can expect another header if the measurement iteration number (count) is 1 and tasks are listed (-t)
        data_content.append(line.split())

    cpu = CpuPlot(headers, data_content)

  def find_header(self):
      split_header_and_content

class CpuPlot:
  def __init__(self, headers, data_content):
    print "helo"
    print headers
    idx_time = 0

    try:
      idx_cpu = headers.index("%CPU")
      for line in data_content:
          print line[idx_time] + " - " + line[idx_cpu]

    except ValueError:
      print("Unable to plot CPU because there is no %CPU in the header")


def parse_args():
  """
  Parse arguments
  """
  parser = argparse.ArgumentParser(description="Plot pidstat output file")
  parser.add_argument("-f",
                      type=file,
                      dest="pidstat_output_file")

  global args
  args = parser.parse_args()

  if not args.pidstat_output_file:
    parser.error("Please provide a pidstat output file")


def main():
  parse_args()

  parser = PidstatFileParser(args.pidstat_output_file.name)
  parser.parse()


if __name__ == "__main__":
  main()

#! /usr/bin/env python
# -*- coding: utf-8 -*

import argparse
import matplotlib
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
    cpu.plot()

  def find_header(self):
      split_header_and_content

class CpuPlot:
  timestamp_list = []
  cpu_usage_list = []
  samples = []
  def __init__(self, headers, data_content):
    idx_time = 0

    try:
      i = 0
      idx_cpu = headers.index("%CPU")
      for line in data_content:
          print line[idx_time] + " - " + line[idx_cpu]
          self.timestamp_list.append(line[idx_time])
          self.cpu_usage_list.append(line[idx_cpu])
          self.samples.append(i)
          i = i + 1

      # Remove the last element from the list, because it contains the average value.
      self.samples = self.samples[:-1]
      self.timestamp_list = self.timestamp_list[:-1]
      self.cpu_usage_list = self.cpu_usage_list[:-1]

    except ValueError:
      print("Unable to plot CPU because there is no %CPU in the header")

  def plot(self):
    # Set the plot title
    plot_figure = plt.figure(1)
    plot_figure.canvas.set_window_title("CPU usage")

    # Assign data set
    plot = plt.plot(self.samples, self.cpu_usage_list)
    # We want the timestamp list instead of the sample number, so set the timestamp list to the label.
    plt.xticks(self.samples, self.timestamp_list)
    plt.xticks(rotation=90)

    # Set the y limit from 0
    plt.ylim(bottom = 0, top = 400)

    plt.xlabel("timestamp")
    plt.ylabel("%cpu")
    plt.grid(True)

    manager = plt.get_current_fig_manager()
    manager.resize(*manager.window.maxsize())
    plot_figure.set_size_inches((19.2, 10.8), forward=True)
    plot_figure.savefig(args.pidstat_output_file.name + ".png", dpi=300)
    plt.show()


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

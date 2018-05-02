#! /usr/bin/env python
# -*- coding: utf-8 -*

import argparse
import matplotlib
import matplotlib.pyplot as plt
import os
import re
import sys

class PidstatFileParser:
  pidstat_file = ""

  UID_PATTERN = re.compile(" UID ")
  AVERAGE_PATTERN = re.compile("Average: ")

  def __init__(self, pidstat_file):
    self.pidstat_file = pidstat_file


  def parse(self):
    with open(self.pidstat_file, "r") as f:
      lines = f.readlines()

    self.do_parse_and_plot(lines)


  def do_parse_and_plot(self, lines):
    '''
    Example data:
        Linux 4.4.70 (8x96auto)         02/28/18        _aarch64_       (4 CPU)

        07:58:27      UID       PID    %usr %system  %guest   %wait    %CPU   CPU  Command
        07:58:32        0      1210    2.59    2.00    0.00    0.00    4.59     2  NavApp
        07:58:32        0       966    0.40    0.20    0.00    0.00    0.60     0  NavigationServi
        07:58:32        0       965    0.00    0.00    0.00    0.00    0.00     0  PositioningServ

        07:58:32      UID       PID    %usr %system  %guest   %wait    %CPU   CPU  Command
        07:58:37        0      1210   19.80   11.00    0.00    0.60   30.80     0  NavApp
        07:58:37        0       966    3.40    0.80    0.00    0.00    4.20     0  NavigationServi
        07:58:37        0       965    0.00    0.00    0.00    0.00    0.00     0  PositioningServ
    '''
    header = None
    data_content = []

    data = {}

    for line in lines:
      line = line.strip()
      if len(line) == 0:
        continue

      matches = self.UID_PATTERN.search(line)
      if matches:
        header = line.split()

        # parse the column header
        try:
          i = 0
          idx_cpu = header.index("%CPU")
          idx_process = header.index("Command")

        except ValueError:
          print("Unable to plot CPU because there is no %CPU in the header")
      else:
        # Only process if the first column header (UID) is found
        # We are not interested in the first line contains the Linux kernel version and target arch:
        #   Linux 4.4.70 (8x96auto) 	02/28/18 	_aarch64_	(4 CPU)

        if not header is None:
          matches = self.AVERAGE_PATTERN.search(line)
          if matches is None:
            data_content.append(line.split())
            line_array = line.split()

            #print "idx_process: {0}->{1}".format(idx_process, line)
            process_name = line_array[idx_process]
            data[process_name] = data.get(process_name, CpuSamples())
            cpu_samples = data[process_name]
            cpu_samples.timestamp_list.append(line_array[0])
            cpu_samples.cpu_usage_list.append(line_array[idx_cpu])

    cpu_plot = ComponentCpuObject()
    cpu_plot.plot(data)


class CpuSamples:
  def __init__(self):
      self.timestamp_list = []
      self.cpu_usage_list = []
      self.samples = []

class ComponentCpuObject:
  def plot(self, data):

    # Create plots with pre-defined labels.
    fig, ax = plt.subplots()

    sample_list = []
    timestamp_list = []
    for key, value in data.items():
      count = len(value.cpu_usage_list)

      sample_list = []
      for i in range(count):
        sample_list.append(i)

      timestamp_list = data[key].timestamp_list

      ax.set_xticklabels(sample_list, data[key].timestamp_list)
      ax.tick_params(axis='x', which='major', pad=15)
      ax.plot(sample_list, data[key].cpu_usage_list, 'o-', label=key)

    legend = ax.legend(loc='upper center', shadow=True, fontsize='x-large')

    # Put a nicer background color on the legend.
    legend.get_frame().set_facecolor('#00FFCC')

    reduced_sample_list, reduced_timestamp_list = self.get_xticks_labels(sample_list, timestamp_list)
    plt.xticks(reduced_sample_list, reduced_timestamp_list)
    plt.xticks(rotation=90)

    # Set the y limit from 0
    plt.ylim(bottom = 0)

    manager = plt.get_current_fig_manager()
    manager.resize(*manager.window.maxsize())
    fig.set_size_inches((19.2, 10.8), forward=True)
    fig.savefig(args.pidstat_file.name + ".png", dpi=300)

    plt.show()

  def get_xticks_labels(self, sample_list, timestamp_list):
    max_x_labels = 40
    samples_count = len(sample_list)
    interval = samples_count / max_x_labels

    if interval <= 0:
      interval = 1

    reduced_sample_list = []
    reduced_timestamp_list = []
    for i in sample_list[0:samples_count-1:interval]:
        reduced_sample_list.append(i)
        reduced_timestamp_list.append(timestamp_list[i])

    # Append the last sample
    reduced_sample_list.append(samples_count - 1)
    reduced_timestamp_list.append(timestamp_list[samples_count - 1])

    return reduced_sample_list, reduced_timestamp_list

  def test_data_structure(self):
    # Make some fake data.
    data = {}
    data["Process1"] = CpuSamples()
    data["Process2"] = CpuSamples()

    for i in range(1, 5):
      cpu_sample = data["Process1"]
      cpu_sample.samples.append(i)
      cpu_sample.timestamp_list.append(i)
      cpu_sample.cpu_usage_list.append(i + 1)

      cpu_navs = data["Process2"]
      cpu_navs.samples.append(i)
      cpu_navs.timestamp_list.append(i)
      cpu_navs.cpu_usage_list.append(i + 5)


    # Create plots with pre-defined labels.
    fig, ax = plt.subplots()
    ax.plot(data["Process1"].samples, data["Process1"].cpu_usage_list, 'k--', label='Process 1')
    ax.plot(data["Process2"].samples, data["Process2"].cpu_usage_list, 'k', label='Process 2')

    legend = ax.legend(loc='upper center', shadow=True, fontsize='x-large')

    # Put a nicer background color on the legend.
    legend.get_frame().set_facecolor('#00FFCC')
    plt.xticks([1,2,3,4], ["a", "b", "c", "d"])
    plt.xticks(rotation=90)

    plt.show()

def parse_args():
  """
  Parse arguments
  """
  parser = argparse.ArgumentParser(description="Plot pidstat file")
  parser.add_argument("-f",
                      type=file,
                      dest="pidstat_file")

  global args
  args = parser.parse_args()

  if not args.pidstat_file:
    parser.error("Please provide a pidstat output file")


def main():
  parse_args()

  pidstat_file_parser = PidstatFileParser(args.pidstat_file.name)
  pidstat_file_parser.parse()

if __name__ == "__main__":
  main()

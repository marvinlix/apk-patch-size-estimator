#!/usr/bin/python
#
# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import apk_patch_size_estimator
from mock import patch
import os
import subprocess
import unittest


class TestCalculateSizes(unittest.TestCase):

  def test_calculate_sizes_success(self):
    sizes = apk_patch_size_estimator.calculate_sizes(
        'tests/1.zip',
        'tests/2.zip',
        'mypatch',
        '/tmp/patch.tmp')
    self.assertRegexpMatches(
        apk_patch_size_estimator.bsdiff_path, 'bsdiff')
    self.assertRegexpMatches(
        apk_patch_size_estimator.gzip_path, 'gzip')
    self.assertRegexpMatches(
        apk_patch_size_estimator.head_path, 'head')
    self.assertRegexpMatches(
        apk_patch_size_estimator.tail_path, 'tail')
    self.assertRegexpMatches(
        apk_patch_size_estimator.bunzip2_path, 'bunzip2')
    ## Using a delta of 10% to compensate for
    ## different bsdiff implemantations
    self.assertAlmostEqual(
        sizes['gzipped_new_file_size']/float(6863020), 1, delta=0.1)
    self.assertAlmostEqual(
        sizes['bsdiff_patch_size']/float(2228571), 1, delta=0.1)
    self.assertTrue(os.path.isfile('mypatch.gz'))
    os.remove('mypatch.gz')

  def test_calculate_sizes_fail(self):
    class PopenMocked(object):

      def wait(self):
        return -1

    with patch.object(subprocess, 'check_output', return_value=''):
      with patch.object(subprocess, 'Popen', return_value=PopenMocked()):
        with self.assertRaises(Exception) as context:
          apk_patch_size_estimator.calculate_sizes(
              '', '', None, '/tmp/patch.tmp')
    self.assertEqual(context.exception.message,
                     'Problem at the bsdiff step, returned code: -1')

  def test_find_binary_fail(self):
    with self.assertRaises(Exception) as context:
      apk_patch_size_estimator.find_binary('does_not_extist_command')
    self.assertEqual(
        context.exception.message,
        'No "does_not_extist_command" on PATH, please install or fix PATH.')

  def test_find_binary_success(self):
    with patch.object(subprocess, 'check_output', return_value=''):
      apk_patch_size_estimator.find_binary('ls')
      subprocess.check_output.assert_any_call(['which', 'ls'])

  def test_human_file_size(self):
    self.assertEqual(
        apk_patch_size_estimator.human_file_size(0), '0B')
    self.assertEqual(
        apk_patch_size_estimator.human_file_size(100), '100B')
    self.assertEqual(
        apk_patch_size_estimator.human_file_size(1024), '1KB')
    self.assertEqual(
        apk_patch_size_estimator.human_file_size(1048576), '1MB')
    self.assertEqual(
        apk_patch_size_estimator.human_file_size(1073741824), '1GB')
    self.assertEqual(
        apk_patch_size_estimator.human_file_size(1099511627776), '1TB')
    self.assertEqual(
        apk_patch_size_estimator.human_file_size(1981633), '1.89MB')
    self.assertEqual(
        apk_patch_size_estimator.human_file_size(15654267), '14.9MB')
    self.assertEqual(
        apk_patch_size_estimator.human_file_size(353244297), '337MB')


if __name__ == '__main__':
  unittest.main()

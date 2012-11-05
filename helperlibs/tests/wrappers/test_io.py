try:
    import unittest2
except ImportError:
    import unittest as unittest2
import os
import tempfile
import shutil
from minimock import mock, restore, TraceTracker, assert_same_trace
from helperlibs.wrappers.io import TemporaryPipe, TemporaryFile

class TestTemporaryPipe(unittest2.TestCase):
    def test__init(self):
        "Test TemporaryPipe object creation"
        pipe = TemporaryPipe()
        self.assertIsNone(pipe.tempdir)
        self.assertEqual(pipe.pipename, "pipe")


    def setUp(self):
        self.tt = TraceTracker()
        mock("os.mkfifo", tracker=self.tt)
        mock("tempfile.mkdtemp", tracker=self.tt, returns="/fake/tmp/dir")
        mock("shutil.rmtree", tracker=self.tt)


    def tearDown(self):
        restore()


    def test__enter(self):
        "Test TemporaryPipe __enter__() method"
        expected = "/fake/tmp/dir/pipe"
        trace = """    Called tempfile.mkdtemp()
    Called os.mkfifo('/fake/tmp/dir/pipe')"""
        pipe = TemporaryPipe()
        path = pipe.__enter__()
        self.assertEqual(path, expected)
        assert_same_trace(self.tt, trace)


    def test__exit(self):
        "Test TemporaryPipe __exit__() method"
        trace = ""
        pipe = TemporaryPipe()
        pipe.__exit__(None, None, None)
        assert_same_trace(self.tt, trace)

        pipe.tempdir = "foo"
        trace = "    Called shutil.rmtree('foo')"
        pipe.__exit__(None, None, None)
        assert_same_trace(self.tt, trace)


class TestTemporaryFile(unittest2.TestCase):
    def setUp(self):
        self.handle = 42
        self.tt = TraceTracker()
        mock("os.unlink", tracker=self.tt)
        mock("tempfile.mkstemp", tracker=self.tt, returns=(self.handle, "/fake/tmp/file"))

    def tearDown(self):
        restore()

    def test__init(self):
        "Test TemporaryFile object creation"
        tfile = TemporaryFile()
        self.assertEqual(tfile.handle, 42)
        self.assertEqual(tfile.name, '/fake/tmp/file')

    def test__enter(self):
        "Test TemporaryFile __enter__() method"
        expected = "/fake/tmp/file"
        trace = """    Called tempfile.mkstemp('', 'tmp', None, False)"""
        tfile = TemporaryFile()
        f = tfile.__enter__()
        self.assertEqual(f.name, expected)
        self.assertEqual(f.handle, 42)
        assert_same_trace(self.tt, trace)

    def test__exit(self):
        "Test TemporaryFile __exit__() method"
        tfile = TemporaryFile()

        trace = """    Called tempfile.mkstemp('', 'tmp', None, False)
    Called os.unlink('/fake/tmp/file')"""
        tfile.__exit__(None, None, None)
        assert_same_trace(self.tt, trace)

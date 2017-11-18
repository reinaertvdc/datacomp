#!/usr/bin/env python3


import glob
import os
import subprocess
from subprocess import DEVNULL
import sys
from typing import Any, Dict, List


BUILD_DIR = 'cmake-build-debug'
TEST_DIR = 'test'


class DecoderConf:
    def __init__(self, name: str, entries: Dict[str, str]):
        self.decfile = '%s.out.yuv' % name
        self.encfile = '%s.enc' % name
        self.logfile = '%s.dec.log' % name
        self.motioncompensation = 1

        self.__dict__.update(entries)

        self.motioncompensation = 1 if bool(self.motioncompensation) else 0


class EncoderConf:
    def __init__(self, name: str, entries: Dict[str, str]):
        self.rawfile = '%s.in.yuv' % name
        self.encfile = '%s.enc' % name
        self.width = 352
        self.height = 288
        self.rle = 1
        self.quantfile = '%s.mat' % name
        self.logfile = '%s.enc.log' % name
        self.gop = 4
        self.merange = 16

        self.__dict__.update(entries)

        self.width = int(self.width)
        self.height = int(self.height)
        self.rle = 1 if bool(self.rle) else 0
        self.gop = int(self.gop)
        self.merange = int(self.merange)


def build() -> None:
    call_wait('cmake --build ' + BUILD_DIR + ' --target all -- -j 4')


def call(command: List[str]) -> None:
    subprocess.Popen(command, stdout=DEVNULL, stderr=DEVNULL)


def call_wait(command: List[str]) -> int:
    return subprocess.call(command, stdout=DEVNULL, stderr=DEVNULL)


def conf_read(path: str) -> Dict[str, str]:
    conf = dict()

    if not os.path.isfile(path):
        return conf

    with open(path) as conf_file:
        for line in conf_file.readlines():
            words = line.strip().split('=', 1)

            key = words[0]
            value = words[1] if len(words) > 1 else ''

            conf[key] = value

    return conf


def conf_write(path: str, conf: Dict[str, Any]) -> None:
    with open(path, 'w') as conf_file:
        for key, value in sorted(conf.items()):
            conf_file.write('%s=%s\n' % (key, str(value)))


def decode(conf_path: str) -> int:
    return call_wait(['%s/decoder' % BUILD_DIR, conf_path])


def encode(conf_path: str) -> int:
    return call_wait(['%s/encoder' % BUILD_DIR, conf_path])


def vlc_open_yuv(video_path: str, width: int, height: int, fps: int=25) -> int:
    call([
        'vlc',
        '--demux', 'rawvideo',
        '--rawvid-fps', str(fps),
        '--rawvid-width', str(width),
        '--rawvid-height', str(height),
        '--rawvid-chroma=I420',
        video_path
    ])


def main() -> None:
    for path in glob.iglob('%s/**/*.enc.conf' % TEST_DIR):
        directory, name = path[0:-len('.enc.conf')].rsplit('/', 1)
        base_path = '%s/%s' % (directory, name)

        encoder_conf_dict = conf_read('%s.enc.conf' % base_path)
        decoder_conf_dict = conf_read('%s.dec.conf' % base_path)

        encoder_conf = EncoderConf(name=name, entries=encoder_conf_dict)
        decoder_conf = DecoderConf(name=name, entries=decoder_conf_dict)

        conf_write('%s.enc.conf' % base_path, encoder_conf.__dict__)
        conf_write('%s.dec.conf' % base_path, decoder_conf.__dict__)

        if not os.path.isfile(encoder_conf.quantfile):
            if not os.path.isdir('%s/%s' % (directory, os.path.dirname(encoder_conf.quantfile))):
                os.makedirs('%s/%s' % (directory, os.path.dirname(encoder_conf.quantfile)))

            with open('%s/%s' % (directory, encoder_conf.quantfile), 'w') as f:
                f.write('2 4 8 16\n' +
                        '4 4 8 16\n' +
                        '8 8 32 64\n' +
                        '16 32 64 128')

        #vlc_open_yuv(path, 352, 288)


main()
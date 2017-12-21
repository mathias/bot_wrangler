Bot Wrangler
===

WIP: A framework for using the existing halite executable from halite.io to RL train bots, and other ML experiments.

Thanks to:

- @sigmavirus24 for pairing and teaching me more Python 3!
- Two Sigma for creating halite.io

## Installation

```shell
pip install -r requirements.txt
```

Also, make sure you have halite executable for your platform in the current dir. You can get it here: https://halite.io/learn-programming-challenge/downloads-and-starter-kits/

## Usage

```shell
python server.py
```

## TODO:

- [ ] Parse win/lose JSON at the end of each run of `halite`
- [ ] Extract out efficient string send/read methods
- [ ] Rewrite Python3 starter bot to use these methods from `server.py` rather than send/receiver STDIN/STDOUT directly.
- [ ] Possibly an example RL starter bot kit, someday.

# License

Copyright (c) 2017 Matt Gauger

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

# pygdo-irc-spider

An optional PyGDO extension point for building consent-aware IRC discovery and
indexing features.

The module deliberately does **not** connect to IRC, crawl channels, capture
messages, or publish collected data by itself. The `irc` module owns protocol
connections. Future spider features must be explicitly configured, scoped to
the server/channel in question, and documented before collection begins.

## Installation

Clone this repository into `gdo/irc_spider` in a PyGDO checkout, then install
the module:

```sh
.venv/bin/python gdoadm.py install irc_spider
```

It depends on the `irc` module.

## Status

This initial release only provides the module boundary, translations, and a
dependency test. It is intentionally inert until a concrete, reviewed feature
is added.

## License

Proprietary software licensed under the PyGDOv8 License.

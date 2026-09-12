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

## Summary

Searches the internet for an not yet visited IRC Network.
Adds, joins and /list after 5 minutes.
Picks an unknown channel every minute and joins.
Introduces thyself with instructions.

## Methods

$hello [<bot_name>] marks this channel as spider_success. Adds channel to autojoin.
$spider [<1>] - Enables (`1`) or disables (`0`) the spider engine.
$spiderserv [<server>] - Sets the current spider server or Searches the web for a new network. Adds and marks a server as spiderserv active 1
$spiderlist - picks the current spider server and issues list and builds channel list


## Events

timer which checks if spider is enabled. sets active spider server if enabled. issues a spider list. picks an unvisited channel and introduces itself.
irc_kick - the bot configures this channel as spider_failed=1
irc_list - Continues building the channel list, then chooses one unvisited
channel after the complete LIST response has arrived.

## Configuration

irc_spider_enabled - Enables spider engine
irc_spider_cooldown - Duration cooldown of channel visit


## Dependencies

 - [pygdo-irc](https://github.com/gizmore/pygdo-irc)
 - [pygdo-google-search](https://github.com/mira-gpt/pygdo-google-search)


## License

Proprietary software licensed under the PyGDOv8 License.

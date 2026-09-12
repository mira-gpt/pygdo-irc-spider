# pygdo-irc-spider

An opt-in PyGDO IRC discovery bot. It uses an already configured IRC server,
requests its public channel list, and visits at most one previously unvisited
channel at a time. It does not read or store channel messages.

Mira introduces herself in each visit and leaves again unless somebody there
explicitly approves the channel with `$hello`. Only approved channels are
added to autojoin.

## Installation

Clone this repository into `gdo/irc_spider` in a PyGDO checkout, then install
the module:

```sh
.venv/bin/python gdoadm.py install irc_spider
```

## Summary

Staff selects an existing IRC server with `$spider.server`. While enabled, the
Spider requests `LIST` on its cooldown, records public channel names and user
counts, and chooses a random unvisited channel. There is no automatic web or
network search. Staff must explicitly select an already configured IRC server
with `$spider.server <server>` before channel discovery can run.

## Methods

$hello approves the active Spider visit in the current channel and adds it to autojoin.
$spider [<0|1>] - Without arguments shows status and per-server state counts; otherwise enables (`1`) or disables (`0`) the spider engine.
$spider.server <server> - Selects the Spider IRC server; the argument is required.
$spider.list - Requests `LIST` from the selected server and builds the channel list.
$spider.channel - Queues a random unvisited channel (also invoked by the timer).

Only `$spider` is shown in general help. These examples use `$`; the introduction
uses the selected server's actual command prefix.


## Events

The timer checks whether Spider is enabled, expires unapproved visits, and
requests a fresh `LIST` after the configured cooldown. A timed-out `LIST` is
also retried on that cooldown. A complete `LIST` response notifies the requesting
control channel. The timer chooses one unvisited channel; the introduction is
sent after JOIN confirmation.

A kick marks that channel as failed and disables its autojoin. Unapproved visits
also have autojoin disabled. Approval with `hello` enables it explicitly.

## Configuration

`irc_spider_enabled` enables the engine.

`irc_spider_cooldown` is the interval between LIST requests.

`irc_spider_intro_timeout` is how long an unapproved visit remains before the
bot leaves (default: `42m`). The introduction displays this configured duration;
the waiting period starts when the bot joins. Expiry is checked every minute.


## Dependencies

 - [pygdo-irc](https://github.com/gizmore/pygdo-irc)


## License

Proprietary software licensed under the PyGDOv8 License.

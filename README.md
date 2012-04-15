jSocket API
=======

jSocket is a Python/Twisted server with a javascript client API.

The goal is to easyly bring real-time communications into any webapp thanks a transparent javascript API.

The Javascript API is responsible of establishing the best transport available and switch to fallbacks transports if needed. 

For some reasons, the API is similar to IRC but it should be much simpler.

 - A `room` is created with an initial password
 - Users can join the room with that password
 - A `master` user can join the room with a special admin password and have more control

 - A standard user can only send `messages` to the `master`user. 
 - `Master`user broadcast messages to any client
 - Standard users are not allowed to communicate together. (This behaviour should be configurable 'per channel')

See working examples in `client/examples`


Features
---
 - Multiple transports:
     - Websocket protocols hiby-07 and hiby-10
     - FlashSocket failover
     - Http polling failover
 - Automatic browser features discovery
 - Users isolation per channel
 - Admin brodcast message to all users
 - Presence detection
 - Watchdog to kill empty rooms, inactive users...


Usage
---
 - server :
     - edit `server/config/settings.py`
     - run with `python main.py`
 - client :
     - add jsocket.js to your webpage
     - declare jsocket configuration
     - connect to the service


Notes 
---
 - Host example pages on an http server


Todo
---
 - Server and client API redesign & docs: things should be **much much simpler**
 - think about encryption/security
 - implement JSONP+CORS for the http failover
 - BUG MacOSX + restart srv. the Ctrl+C never closes


Requirements:
--

- Twisted 10.0.0+
- Python 2.5+


Brought to you by revolunet team !

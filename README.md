# varnish-cache-reaper

Simple python/twisted HTTP daemon forwarding PURGE and BAN requests to multiple varnish (or other proxy) instances.

The daemon forwards all HTTP PURGE and BAN requests using the original Host-header and URL to all configured endpoints.
See [Varnish documentation](https://www.varnish-cache.org/docs/3.0/tutorial/purging.html#) for VCL examples able to
handle these kind of requests.

This script is designed to run in a supervised environment like *supervisord*, *daemontools* or *runit*.
For *runit* example code see runit-run and runit-log-run.

## Usage

```
usage: varnish-cache-reaper.py [-h] [-v] [-l IP] [-p PORT]
                               targets [targets ...]

Varnish cache reaper

positional arguments:
  targets               Endpoint(s) to send PURGE/BAN requests to

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -l IP, --listen-ip IP
                        IP to listen on, default *
  -p PORT, --listen-port PORT
                        TCP port to listen on, default 8042
```

## Example

The following command line will start a service listening on 127.0.0.1:8042 (default port) and will forward all incoming PURGE or BAN
requests to http://127.0.0.1:8080 and http://127.0.0.1:8081.

```
./varnish-cache-reaper.py -l 127.0.0.1 http://127.0.0.1:8080 http://127.0.0.1:8081
```

To issue a PURGE request, then use
```
curl -X PURGE -H "Host: vhost.whatever" "http://127.0.0.1:8042/foo/bar"  > /dev/null
```

which will send PURGE requests to all endpoints using *vhost.whatever* as *Host:* header and */foo/bar* as URL.

## Dependencies

* Python 2.7
* [Twisted](http://twistedmatrix.com/trac/wiki/Downloads), Debian/Ubuntu Package: *python-twisted*
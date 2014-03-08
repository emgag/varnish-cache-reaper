#!/usr/bin/env python2
#
# Simple web service to dispatch purge requests to multiple proxies
#

from __future__ import print_function
from argparse import ArgumentParser
from sys import stderr, stdout, exit
from twisted.web import server, resource, client, http_headers
from twisted.internet import reactor, error

def onFailure(err):
    """
    :type err: twisted.python.failure.Failure
    """
    print("[!!] Server response: " + str(err.getBriefTraceback()), end="\n", file=stderr)


def onSuccess(res):
    """
    :type res: twisted.web.client.Response
    """
    if(res.code < 400):
        indicator = "OK"
    else:
        indicator = "!!"

    print("[" + indicator + "] " + res.request.method + " response for " + res.request.absoluteURI + ": " + str(res.code), end="\n", file=stdout)


class DispatchResource(resource.Resource):
    isLeaf = True

    def dispatch(self, method, request):
        """ Asynchronously dispatches requests to all targets

        :type method: str
        :type request: twisted.web.http.Request
        """
        for target in self.targets:
            print("[II] Sending " + method + " request for " + request.getRequestHostname() + request.uri + " to: " + target, end="\n", file=stdout)
            d = self.agent.request(method,target + request.uri, http_headers.Headers({"Host": [request.getRequestHostname()]}))
            d.addCallbacks(onSuccess, onFailure)

    def render_BAN(self, request):
        """ Handles BAN request method

        :type request: twisted.web.http.Request
        """
        request.setHeader("content-type", "text/plain")
        self.dispatch("BAN", request)
        return "BAN requested for: " + request.getRequestHostname() + request.uri + "\n"

    def render_PURGE(self, request):
        """ Handles PURGE request method

        :type request: twisted.web.http.Request
        """
        request.setHeader("content-type", "text/plain")
        self.dispatch("PURGE", request)
        return "PURGE requested for: " + request.getRequestHostname() + request.uri + "\n"

# parse cli argumennts
parser = ArgumentParser(description="Varnish cache reaper",version="0.1")
parser.add_argument("-l", "--listen-ip", action="store", dest="ip", default="", help="IP to listen on, default *")
parser.add_argument("-p", "--listen-port", action="store", dest="port", type=int, default=8042, help="TCP port to listen on, default 8042")
parser.add_argument("targets", action="store", nargs="+", help="Endpoint(s) to send PURGE/BAN requests to")
args = parser.parse_args()

# initialize client and server resources
agent = client.Agent(reactor, connectTimeout=5)
purge = DispatchResource()
purge.agent = agent
purge.targets = args.targets
site = server.Site(purge)

try:
    reactor.listenTCP(args.port, site, interface=args.ip)
    reactor.run()
except error.CannotListenError as e:
    print("[!!] Could not start service: " + str(e.socketError), end="\n", file=stderr)
    exit(1)


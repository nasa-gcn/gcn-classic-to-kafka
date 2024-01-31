#
# Copyright © 2023 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
"""Command line interface."""
import asyncio
import logging
import urllib
import signal
import sys

import click
import gcn_kafka
import prometheus_client

from .socket import client_connected
from . import metrics

log = logging.getLogger(__name__)


def signal_handler(signum, frame):
    log.info("Exiting due to signal %d", signum)
    sys.exit(128 + signum)


def kafka_delivered_cb(err, msg):
    successful = not err
    metrics.delivered.labels(msg.topic(), msg.partition(), successful).inc()


def host_port(host_port_str):
    # Parse netloc like it is done for HTTP URLs.
    # This ensures that we will get the correct behavior for hostname:port
    # splitting even for IPv6 addresses.
    return urllib.parse.urlparse(f"http://{host_port_str}")


@click.command()
@click.option(
    "--listen",
    type=host_port,
    default=":8081",
    show_default=True,
    help="Hostname and port to listen on for GCN Classic",
)
@click.option(
    "--prometheus",
    type=host_port,
    default=":8000",
    show_default=True,
    help="Hostname and port to listen on for Prometheus metric reporting",
)
@click.option(
    "--loglevel",
    type=click.Choice(logging._levelToName.values()),
    default="DEBUG",
    show_default=True,
    help="Log level",
)
def main(listen, prometheus, loglevel):
    """Pump GCN Classic notices to a Kafka broker.

    Specify the Kafka client configuration in environment variables using the
    conventions described in
    https://docs.confluent.io/platform/current/installation/docker/config-reference.html#confluent-enterprise-ak-configuration:

    * Start the environment variable name with `KAFKA_`.
    * Convert to upper-case.
    * Replace periods (`.`) with single underscores (`_`).
    * Replace dashes (`-`) with double underscores (`__`).
    * Replace underscores (`-`) with triple underscores (`___`).
    """
    logging.basicConfig(level=loglevel)

    prometheus_client.start_http_server(
        prometheus.port, prometheus.hostname or "0.0.0.0"
    )
    log.info("Prometheus listening on %s", prometheus.netloc)

    config = gcn_kafka.config_from_env()
    config["client.id"] = __package__
    config["on_delivery"] = kafka_delivered_cb

    producer = gcn_kafka.Producer(config)
    client = client_connected(producer)

    async def serve():
        server = await asyncio.start_server(client, listen.hostname, listen.port)
        log.info("GCN server listening on %s", listen.netloc)
        async with server:
            await server.serve_forever()

    # Exit cleanly on SIGTERM
    signal.signal(signal.SIGTERM, signal_handler)

    asyncio.run(serve())

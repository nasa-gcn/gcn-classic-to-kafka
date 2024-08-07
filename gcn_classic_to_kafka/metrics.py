#
# Copyright © 2023 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
"""Prometheus metrics."""

import prometheus_client

connected = prometheus_client.Gauge(
    "connected", "Number of active connections from GCN Classic", namespace=__package__
)

iamalive = prometheus_client.Counter(
    "iamalive",
    "GCN notices received of any type, including iamalives",
    namespace=__package__,
)

received = prometheus_client.Counter(
    "received",
    "GCN Classic notices received by notice type and flavor",
    labelnames=["notice_type_int", "notice_type_str", "flavor"],
    namespace=__package__,
)

delivered = prometheus_client.Counter(
    "delivered",
    "Kafka messages delivered",
    labelnames=["topic", "partition", "successful"],
    namespace=__package__,
)

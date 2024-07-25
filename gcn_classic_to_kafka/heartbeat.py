#
# Copyright © 2023 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
import asyncio
import datetime
import json
import logging

import confluent_kafka

log = logging.getLogger(__name__)

TIMEOUT = 1
TOPIC = "gcn.heartbeat"


async def run(producer: confluent_kafka.Producer):
    """Produce a heartbeat message once per second."""
    log.info("Producing heartbeats every %d second(s) on topic %s", TIMEOUT, TOPIC)
    while True:
        producer.produce(
            TOPIC,
            json.dumps(
                {
                    "$schema": "https://gcn.nasa.gov/docs/schema/v4.1.0/gcn/notices/core/Alert.schema.json",
                    "alert_datetime": datetime.datetime.now(datetime.UTC).isoformat(),
                }
            ),
        )

        # Wait for any outstanding messages to be delivered and delivery
        # report callbacks to be triggered.
        producer.poll(0)

        await asyncio.sleep(TIMEOUT)

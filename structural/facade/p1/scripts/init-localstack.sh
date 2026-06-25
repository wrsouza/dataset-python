#!/usr/bin/env bash
# Runs automatically when LocalStack becomes ready (init/ready.d hook).
# Creates the "orders" SQS queue used by SQSNotificationService in dev mode.
set -euo pipefail

awslocal sqs create-queue --queue-name orders

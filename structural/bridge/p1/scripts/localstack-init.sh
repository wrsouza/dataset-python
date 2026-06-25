#!/bin/bash
# Initialize LocalStack SES with verified email identities.
set -e

echo "==> Verifying SES email identities..."
awslocal ses verify-email-identity --email-address noreply@example.com
awslocal ses verify-email-identity --email-address recipient@example.com
echo "==> LocalStack SES initialized."

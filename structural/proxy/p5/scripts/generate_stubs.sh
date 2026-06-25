#!/usr/bin/env bash
# Regenerate the gRPC Python stubs from proto/service.proto.
#
# Run from the project root (structural/proxy/p5/):
#   bash scripts/generate_stubs.sh
#
# Requires grpcio-tools (installed via the project's dev extra):
#   pip install -e ".[dev]"
set -euo pipefail

OUT_DIR="src/rate_limiting/infrastructure/generated"

python -m grpc_tools.protoc \
    -I proto \
    --python_out="${OUT_DIR}" \
    --grpc_python_out="${OUT_DIR}" \
    --pyi_out="${OUT_DIR}" \
    proto/service.proto

# protoc generates a flat "import service_pb2 as service__pb2" in the
# *_grpc.py file, which only works if the generated/ directory is on
# sys.path directly. We rewrite it to an absolute import so the generated
# package can be imported normally as part of rate_limiting.infrastructure.
sed -i \
    's/^import service_pb2 as service__pb2$/from rate_limiting.infrastructure.generated import service_pb2 as service__pb2/' \
    "${OUT_DIR}/service_pb2_grpc.py"

echo "Stubs regenerated in ${OUT_DIR}"

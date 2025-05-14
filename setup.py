from setuptools import setup, find_namespace_packages
import os
import shutil
import subprocess
import tempfile

import logging

logger = logging.getLogger(__name__)

# Create a temporary directory for cloning the repo
temp_dir = tempfile.mkdtemp()
try:
    # Clone the OpenTelemetry proto repository
    subprocess.check_call(
        [
            "git",
            "clone",
            "https://github.com/open-telemetry/opentelemetry-proto.git",
            os.path.join(temp_dir, "opentelemetry-proto"),
        ]
    )
    subprocess.check_call(
        [
            "git",
            "checkout",
            "ae87ce7c56e5fd356b77097b1d9a655ff00aa24f",  # February 11, 2025 commit
        ],
        cwd=os.path.join(temp_dir, "opentelemetry-proto")
    )
    
    # Create output directories
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Create directories for profiles and dependencies
    profiles_dir = os.path.join(
        base_dir, "opentelemetry", "proto", "profiles", "v1development"
    )
    collector_profiles_dir = os.path.join(
        base_dir, "opentelemetry", "proto", "collector", "profiles", "v1development"
    )
    common_dir = os.path.join(base_dir, "opentelemetry", "proto", "common", "v1")
    resource_dir = os.path.join(base_dir, "opentelemetry", "proto", "resource", "v1")

    os.makedirs(profiles_dir, exist_ok=True)
    os.makedirs(collector_profiles_dir, exist_ok=True)
    os.makedirs(common_dir, exist_ok=True)
    os.makedirs(resource_dir, exist_ok=True)

    # Create all __init__.py files
    for path in [
        os.path.join(base_dir, "opentelemetry"),
        os.path.join(base_dir, "opentelemetry", "proto"),
        os.path.join(base_dir, "opentelemetry", "proto", "profiles"),
        profiles_dir,
        os.path.join(base_dir, "opentelemetry", "proto", "collector"),
        os.path.join(base_dir, "opentelemetry", "proto", "collector", "profiles"),
        collector_profiles_dir,
        os.path.join(base_dir, "opentelemetry", "proto", "common"),
        common_dir,
        os.path.join(base_dir, "opentelemetry", "proto", "resource"),
        resource_dir,
    ]:
        with open(os.path.join(path, "__init__.py"), "w") as f:
            pass

    # Generate Python files from the proto files
    proto_dir = os.path.join(temp_dir, "opentelemetry-proto")

    # Find the profiles proto files (check both v1experimental and v1development)
    profiles_proto_experimental = os.path.join(
        proto_dir,
        "opentelemetry",
        "proto",
        "profiles",
        "v1experimental",
        "profiles.proto",
    )
    profiles_proto_development = os.path.join(
        proto_dir,
        "opentelemetry",
        "proto",
        "profiles",
        "v1development",
        "profiles.proto",
    )

    profiles_proto = (
        profiles_proto_development
        if os.path.exists(profiles_proto_development)
        else profiles_proto_experimental
    )

    # Find the collector profiles service proto files
    collector_profiles_proto_experimental = os.path.join(
        proto_dir,
        "opentelemetry",
        "proto",
        "collector",
        "profiles",
        "v1experimental",
        "profiles_service.proto",
    )
    collector_profiles_proto_development = os.path.join(
        proto_dir,
        "opentelemetry",
        "proto",
        "collector",
        "profiles",
        "v1development",
        "profiles_service.proto",
    )

    collector_profiles_proto = (
        collector_profiles_proto_development
        if os.path.exists(collector_profiles_proto_development)
        else collector_profiles_proto_experimental
    )

    # Common dependencies
    common_proto = os.path.join(
        proto_dir, "opentelemetry", "proto", "common", "v1", "common.proto"
    )
    resource_proto = os.path.join(
        proto_dir, "opentelemetry", "proto", "resource", "v1", "resource.proto"
    )

    # Generate the Python code
    subprocess.check_call(
        [
            "python",
            "-m",
            "grpc_tools.protoc",
            f"-I{proto_dir}",
            f"--python_out={base_dir}",
            f"--grpc_python_out={base_dir}",
            profiles_proto,
            collector_profiles_proto,
            common_proto,
            resource_proto,
        ]
    )

    # If we used the experimental path, move profiles files to development
    if profiles_proto == profiles_proto_experimental:
        v1experimental_dir = os.path.join(
            base_dir, "opentelemetry", "proto", "profiles", "v1experimental"
        )
        if os.path.exists(v1experimental_dir):
            for file_name in os.listdir(v1experimental_dir):
                if file_name.endswith(".py"):
                    shutil.copy2(
                        os.path.join(v1experimental_dir, file_name),
                        os.path.join(profiles_dir, file_name),
                    )

    # If we used the experimental path, move collector profiles files to development
    if collector_profiles_proto == collector_profiles_proto_experimental:
        collector_v1experimental_dir = os.path.join(
            base_dir,
            "opentelemetry",
            "proto",
            "collector",
            "profiles",
            "v1experimental",
        )
        if os.path.exists(collector_v1experimental_dir):
            for file_name in os.listdir(collector_v1experimental_dir):
                if file_name.endswith(".py"):
                    shutil.copy2(
                        os.path.join(collector_v1experimental_dir, file_name),
                        os.path.join(collector_profiles_dir, file_name),
                    )

except Exception as e:
    logger.exception(
        "Error in setup.py - opentelemetry-proto-profile dependency: %s", str(e)
    )
    raise
finally:
    # Clean up temporary directory
    shutil.rmtree(temp_dir, ignore_errors=True)

setup(
    packages=find_namespace_packages(include=["opentelemetry.*"]),
)

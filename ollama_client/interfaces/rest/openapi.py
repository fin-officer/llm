#!/usr/bin/env python
"""
Generate OpenAPI schema documentation for the REST API
"""
import json
import os
import sys
from pathlib import Path

from fastapi.openapi.utils import get_openapi
from ollama_client.interfaces.rest.app import app


def generate_openapi_schema(output_file: str = None):
    """Generate OpenAPI schema for the REST API"""
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    if output_file:
        # Make sure directory exists
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write schema to file
        with open(output_file, "w") as f:
            json.dump(openapi_schema, f, indent=2)

        print(f"OpenAPI schema written to {output_file}")
    else:
        # Print schema to stdout
        print(json.dumps(openapi_schema, indent=2))


if __name__ == "__main__":
    # Get output file from command line argument
    output_file = sys.argv[1] if len(sys.argv) > 1 else None
    generate_openapi_schema(output_file)
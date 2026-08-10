#!/usr/bin/env bash
# Build the image, then serve the site at http://localhost:8080
docker build -t mycelium-docs-mkdocs .
docker run --rm -it \
  -p 8080:8000 \
  -v "$(pwd)":/docs \
  mycelium-docs-mkdocs

#!/bin/bash
docker run --rm -v .:/docs igordejanovic/mdbook-textx:latest mdbook build

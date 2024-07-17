#!/bin/bash
docker run --rm -v .:/p igordejanovic/mdbook-textx:latest mdbook build

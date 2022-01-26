#!/usr/bin/env bash
isort .
yapf -ri .
pylint **/*.py

#!/bin/bash

COMMAND=./send_command.py

${COMMAND} reset

${COMMAND} characters "Hello, World!"
${COMMAND} return


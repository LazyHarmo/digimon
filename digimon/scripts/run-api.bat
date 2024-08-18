#!/bin/bash

uvicorn "digimon.main:create_app" --factory --reload

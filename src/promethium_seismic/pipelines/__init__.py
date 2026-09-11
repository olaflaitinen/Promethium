# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
# Promethium Pipelines Module

"""
High-level end-to-end workflows for seismic data reconstruction.

This module provides pipeline abstractions that combine preprocessing,
model inference, and postprocessing into cohesive workflows.
"""

from promethium_seismic.pipelines.recovery import SeismicRecoveryPipeline

__all__ = [
    "SeismicRecoveryPipeline",
]

#!/usr/bin/env python3
"""
Constants associated with the model OpenABM-Covid19
"""

from COVID19.model import AgeGroupEnum, EVENT_TYPES, TransmissionTypeEnum, OccupationNetworkEnum

# Define arrays associated with networks/ages
interaction_labels = [c.name[1:].title() for c in TransmissionTypeEnum]
interaction_types = [c.value for c in TransmissionTypeEnum ]

# Define age groups and labels
n_age = len(AgeGroupEnum) + 1
age_group_labels = [enum.name[1:].replace("_","-") for enum in AgeGroupEnum]
age_group_labels[-1] = "80+"
n_age_groups = len(age_group_labels)

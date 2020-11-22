#!/usr/bin/env python3

import cProfile
import os
import pstats
import uuid
from io import StringIO
from pathlib import Path

from app.comparison.scenarios.scenario_2 import ComparisonScenarioTwo


def get_dump_filename(profiler_uuid, file_format="stats"):
    dump_file_name = "{}.{}".format(profiler_uuid, file_format)
    dump_path = os.path.join(os.environ['DATA_DIR'], 'profiler')
    Path(dump_path).mkdir(parents=True, exist_ok=True)
    return os.path.join(dump_path, dump_file_name)


def run_test_case():
    scenario_two = ComparisonScenarioTwo(simulation_options={
        'max_steps': 5000,
        'max_steps_without_train_movement': 0,
        'max_cost': 10e6,
    }, solutions_size=5, max_iterations=5)
    scenario_two.run(export_results=False)


def run_profiling():
    profiler_uuid = str(uuid.uuid4())
    pr = cProfile.Profile()
    pr.enable()
    run_test_case()
    pr.disable()
    s = StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    profile_dump_file = get_dump_filename(profiler_uuid)
    ps.dump_stats(profile_dump_file)
    return profile_dump_file


if __name__ == '__main__':
    filename = run_profiling()
    p = pstats.Stats(filename)
    p.sort_stats('cumulative').print_stats(100)

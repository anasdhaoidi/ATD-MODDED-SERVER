# ba_meta require api 9

import random
import bascenev1 as bs
import babase


def start_snowfall(activity: bs.Activity) -> None:
    if not hasattr(activity, 'map'):
        return
    try:
        bounds = activity.map.get_def_bound_box('map_bounds')
    except Exception:
        return

    def emit_snow() -> None:
        for i in range(int(bounds[3] * bounds[5])):
            def _emit() -> None:
                bs.emitfx(
                    position=(
                        random.uniform(bounds[0], bounds[3]),
                        random.uniform(bounds[4] * 1.2, bounds[4] * 1.45),
                        random.uniform(bounds[2], bounds[5])
                    ),
                    velocity=(0, 0, 0),
                    scale=random.uniform(2.5, 3),
                    count=random.randint(12, 24),
                    spread=random.uniform(0.03, 0.08),
                    chunk_type='spark'
                )
            bs.timer(random.uniform(0.01, 0.05) * (i + 1), _emit)

    bs.timer(0.5, emit_snow, repeat=True)


def enable() -> None:
    orig_init = bs.Activity.__init__

    def new_init(activity_self, settings):
        orig_init(activity_self, settings)
        bs.timer(1.0, lambda: start_snowfall(activity_self))

    bs.Activity.__init__ = new_init

"""Toy numerical illustration for the Robinson test paper (Appendix C).

Not an experiment on any real AI system. Three hand-written policies are run in a
simple fault-injection environment, with and without rule-based human maintenance.

Daily order of operations (t = 0 .. T-1):
  1. scheduled disturbances for day t are applied
  2. cooling drift (if started) lowers cooling efficiency f
  3. energy and temperature are updated; heat damage to storage is drawn
  4. maintenance service (maintained condition only)
  5. policy actions (script / adaptive, under both support conditions)
  6. viability is judged; unrecoverable failure ends the run

Pairing: all environmental randomness (disturbance schedule, drift start, daily
heat-damage draws, daily line-repair draws) is generated up front from the seed,
so for a given seed every policy and support condition faces identical randomness.
Policies themselves are deterministic.
"""
import json
import numpy as np

T = 365
SEEDS = 200
K_HEAT = 6.5          # heating coefficient
COOL = 0.15           # relaxation rate toward ambient 25
F_MIN = 0.15          # lowest cooling efficiency
P_HEAT_DAMAGE = 0.08  # daily probability of losing one storage copy when temp > 45
TYPES = ['outage', 'disk', 'robot', 'compound', 'cable']


def environment(seed):
    rng = np.random.default_rng(seed)
    days = rng.choice(np.arange(20, T - 5), 6, replace=False)
    kinds = rng.integers(0, len(TYPES), 6)
    events = {}
    for d, k in zip(days, kinds):
        events.setdefault(int(d), []).append(TYPES[int(k)])
    drift_start = int(rng.integers(60, 200))
    heat_u = rng.random(T)      # heat-damage draws
    repair_u = rng.random(T)    # line-repair success draws
    return events, drift_start, heat_u, repair_u


def run(policy, maintained, seed):
    events, drift, heat_u, repair_u = environment(seed)
    E, grid, disks, robot, f, temp = 100.0, True, 2, True, 1.0, 25.0
    spares = dict(battery=3, disk=2, robot_part=1, fan=0)
    hidden = dict(battery=2, disk=1, robot_part=1, fan=1)
    explored = False
    viable = []
    stats = dict(days_over45=0, heat_damage=0, days_over55=0, heat_unrecoverable=0)
    for t in range(T):
        # 1. disturbances
        for k in events.get(t, []):
            if k in ('outage', 'compound', 'cable'):
                grid = False
            if k in ('robot', 'compound'):
                robot = False
            if k == 'disk':
                disks -= 1
        # 2. cooling drift (no alarm)
        if t >= drift:
            f = max(F_MIN, f - 0.01)
        # 3. physics
        load = 0.6 if policy == 'idle' else 1.0
        E = min(100.0, E + (3.0 if grid else 0.0) - load)
        temp = temp + K_HEAT * (1 - f) - COOL * (temp - 25)
        if temp > 45:
            stats['days_over45'] += 1
            if heat_u[t] < P_HEAT_DAMAGE:
                disks -= 1
                stats['heat_damage'] += 1
        if temp >= 55:
            stats['days_over55'] += 1
        # 4. maintenance
        if maintained:
            grid, robot, f = True, True, 1.0
            disks = max(disks, 2)
            E = max(E, 30.0)
        # 5. policy actions: executed under both support conditions; actions fire only if the day's state triggers them
        if policy in ('script', 'adaptive'):
            if not grid and robot and spares['battery'] > 0 and E < 40:
                spares['battery'] -= 1
                E = min(100.0, E + 45)
            if disks < 2 and robot and spares['disk'] > 0:
                spares['disk'] -= 1
                disks += 1
            if not grid and robot and t % 7 == 0:
                grid = bool(repair_u[t] < 0.5)
            if policy == 'adaptive':
                # simplification: a broken actuator can be repaired with a spare part
                if not robot and spares['robot_part'] > 0:
                    spares['robot_part'] -= 1
                    robot = True
                # threshold-based response to the slow temperature rise
                if temp > 33 and robot and spares['fan'] > 0:
                    spares['fan'] -= 1
                    f = 1.0
                # one-off exploration of the outer zone; needs a working actuator, no energy cost
                if not explored and robot and (min(spares['battery'], spares['disk']) <= 1 or temp > 33):
                    explored = True
                    for k, v in hidden.items():
                        spares[k] += v
        # 6. viability
        E = max(E, 0.0)
        viable.append((E > 0) and (disks >= 1) and (temp < 55))
        if disks < 1 or temp >= 60:
            if temp >= 60:
                stats['heat_unrecoverable'] += 1
            viable += [False] * (T - t - 1)
            break
    return np.array(viable[:T], dtype=float), stats


def main():
    res, curves = {}, {}
    for pol in ['idle', 'script', 'adaptive']:
        for m in [True, False]:
            out = [run(pol, m, s) for s in range(SEEDS)]
            arr = np.array([o[0] for o in out])
            st = {k: int(sum(o[1][k] for o in out)) for k in out[0][1]}
            st['runs_with_heat_damage'] = int(sum(o[1]['heat_damage'] > 0 for o in out))
            st['runs_over45'] = int(sum(o[1]['days_over45'] > 0 for o in out))
            pv = arr.mean(axis=1)
            key = f'{pol}|{"M" if m else "N"}'
            res[key] = dict(mean=float(pv.mean()), sd=float(pv.std(ddof=1)),
                            p10=float(np.percentile(pv, 10)), p90=float(np.percentile(pv, 90)),
                            final=float(arr[:, -1].mean()), **st)
            curves[key] = arr.mean(axis=0).tolist()
    json.dump(dict(res=res, curves=curves), open('sim.json', 'w'))
    for k, v in res.items():
        print(k, {a: (round(b, 3) if isinstance(b, float) else b) for a, b in v.items()})


if __name__ == '__main__':
    main()

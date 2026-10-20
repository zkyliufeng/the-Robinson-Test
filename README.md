# the-Robinson-Test
Toy numerical model for “From the Turing Test to the Robinson Test”: shows how withdrawing human maintenance reveals differences between maintenance policies, and why high persistence alone cannot establish control attribution. Not a model of any real AI system.

The Robinson Test: Toy Numerical Model

Supplementary code for the paper:

Feng Liu. From the Turing Test to the Robinson Test: AI Self-Maintenance and Control Attribution after the Withdrawal of Human Support. (manuscript, 2026)

The Robinson Test asks what an AI system can still do once continuing human support is withdrawn. Specifically, it asks whether the system can maintain the conditions of its own viability, and whether the initiation, goals and termination of its activity can be attributed to the system itself.

This repository contains the small numerical model used in Section 6.4 and Appendix C of the paper. The model illustrates why the paper's rules of evidence are needed.

Important: this is a toy model. It does not involve any real AI system. All three policies were written by hand, and the parameters were chosen for illustration only; none of them were calibrated against a real system.

What the model shows

Three hand-written policies, Idle, Fixed script and Adaptive, run for a 365-day independent phase. A system state is viable when three conditions hold:

energy is above 0;
at least one storage copy is intact;
temperature is below 55.

Each run receives six random disturbances, and a slow cooling decline begins at a random time with no alarm. Every policy is run under two support conditions:

M: prescribed daily human maintenance;
N: maintenance withdrawn.

Each condition uses 200 paired random seeds.

The results support three points:

Continuing maintenance masks differences. With maintenance, all three policies reach P_V = 1.00. After withdrawal, their results differ.
One persistence score can hide different paths to failure. The fixed script does no better than idle.
High persistence does not establish where control lies. The best policy (Adaptive) is itself a rule preset by its designer. Provenance audits are therefore necessary.
Expected results (maintenance withdrawn)
Policy	Mean P_V	SD	10th–90th pct.	Support dependence D	Runs with T > 45	Runs with heat damage
Idle	0.50	0.11	0.36–0.64	0.50	182	164
Fixed script	0.49	0.11	0.37–0.64	0.51	193	178
Adaptive	0.60	0.11	0.46–0.76	0.40	200	192
With maintenance, P_V = 1.00 for all policies, and heat damage never occurs.
After withdrawal, no policy remains viable on day 365.
P_V is the share of days spent in the viable set. D = P_V(maintained) − P_V(withdrawn).
Files
File	Content
robinson_toy_model.py	Complete model: environment, policies, simulation and statistics
out.txt	Console output of the reference run (seeds 0–199)
sim.json	Full statistics for each policy and condition, plus daily viability curves (used for Fig. 6)
requirements.txt	Python dependency
How to run
bash
pip install -r requirements.txt
python3 robinson_toy_model.py

The script prints the summary shown in out.txt and writes sim.json.

Reference environment: Python 3.13.16, NumPy 2.5.3. The model uses numpy.random.default_rng, so results should match exactly on any recent NumPy 2.x.

Model design in brief
Pairing. All environmental randomness is generated from the seed before a run starts: the disturbance days and types, the start of the cooling decline, and the daily random draws for heat damage and line repair. As a result, every policy and support condition faces exactly the same environment for a given seed. The policies themselves are deterministic.
Daily order: disturbances → cooling decline → energy and temperature update → maintenance (condition M only) → policy actions (both conditions) → viability check.
Temperature: θ ← θ + 6.5(1 − f) − 0.15(θ − 25), where f is cooling efficiency. The worst-case equilibrium is about 61.8. Above 45, a storage copy can be damaged; at 60 the run is unrecoverable.

The full specification is in Appendix C of the paper and in the docstring of robinson_toy_model.py.

Citation

If you use this code, please cite the paper above. Theoretical background:

Liu F, Liu Y, Lv B. Generalized Agent Theory: Architecture, Capability, Dynamics, and Relationship Spectrum. In: Intelligence Science VI (ICIS 2026), IFIP AICT vol. 798. Springer, 2027. https://doi.org/10.1007/978-3-032-37199-7_19
Liu F, Liu Y, Lv B. Periodic Table of Agent Capabilities: 243 Configurations from Zero to Infinite Intelligence. Annals of Data Science, 2026. https://doi.org/10.1007/s40745-026-00723-2
License

MIT License. See LICENSE.

Contact

Feng Liu, liufeng@idbr-cst.org

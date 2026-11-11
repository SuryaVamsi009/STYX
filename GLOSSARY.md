# STYX Research and Paper Execution

Language for the research and paper-trading workflow.

## Execution boundary

**Paper order**:
An order instruction handled using virtual funds that is not transmitted to a real broker. Analyzer Mode is not considered paper execution for Gate 0 until its isolation is verified for the installed version.
_Avoid_: Sandbox order (when referring to Analyzer Mode without verified isolation)

**Real-broker order path**:
Any active component or route capable of transmitting an order to a real broker. A broker data connection or read-only account query is not, by itself, a real-broker order path.
_Avoid_: Broker client (when order capability is meant)

**Analyzer Mode**:
OpenAlgo mode described by STYX as virtual capital on real broker prices. Whether it prevents a real-broker order path is **UNVERIFIED** until established for the installed version.
_Avoid_: Sandbox (unless isolation is verified)

## Gate 0

**Gate 0 test-only capital**:
Surya-approved virtual capital for the single Gate 0 paper-order exercise. It is not planning capital, and results from the exercise are not strategy evidence.
_Avoid_: Planning capital

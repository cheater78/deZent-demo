# deZent demo
*A refactored implementation of the [deZent algorithm](https://github.com/carolin-brunn/deZent-local_zanon) extended by a visualization using the Qt-Framework.*

## Setup and Execution
The repo provides a one-shot script performing first time setup and running the demonstrator.
```
# Installs dependencies + dezent_demo into a .venv and runs the package.
./run.sh
```

## UI
Pan the network graph view by:
- pressing Mouse2 (Right Click) and dragging

#### (Debug-) Hotkeys
```
Space - commences to next state (equiv. to "Next" button)
R - recenters the network graph view
T - toggle CBF Plot view visibility
```

## Project Structure

```text
data/
src/
└── deZent_demo/
    ├── ami/
    ├── instrument/
    ├── network/
    ├── presentation/
    ├── sandbox/
    ├── ui/
    ├── utils/
    └── zanon/
...
run.sh
```

- **[`ami/`](src/deZent_demo/ami/)** — Models the Advanced Metering Infrastructure (AMI), including its entities and measurement handling. It also provides loading and sampling of standard load profiles from data/.

- **[`instrument/`](src/deZent_demo/instrument/)** — Provides the instrumentation framework and instrumentor implementations for gateways and the deZent gateway.

- **[`network/`](src/deZent_demo/network/)** — Defines network nodes identified by NetworkNodeID, network protocol, node abstractions, and the virtual communication layer based on message queues. It includes centralized star and deZent ring–star topologies, including their edge nodes.

- **[`presentation/`](src/deZent_demo/presentation/)** — Implements the presentation sandbox window and the visualization-specific logic used to demonstrate the deZent algorithm.

- **[`sandbox/`](src/deZent_demo/sandbox/)** — Defines the simulation environment and network participants independently of visualization. The sandbox's contents can subsequently be instrumented and presented through the UI.

- **[`ui/`](src/deZent_demo/ui/)** — Contains the PySide6-based elements, including styling, scene views, reusable widgets, and the window abstraction.

- **[`utils/`](src/deZent_demo/utils/)** — Provides shared infrastructure: configuration, protocol-related data structures and counting Bloom filter, threading primitives, and a fully virtualized time environment.

- **[`zanon/`](src/deZent_demo/zanon/)** — Contains the standalone deZent algorithm implementation, with gateway and central-entity components communicating through the abstract network-node interface.

The resulting dependency structure separates the simulation model (ami, network, zanon, sandbox) from instrumentation (instrument) and presentation (presentation, ui), while utils provides shared infrastructure. The application entry points are located in [\_\_main\_\_.py](src/deZent_demo/__main__.py) and by extension [app.py](src/deZent_demo/app.py).

## Known Issues / Future Work

- the presentation logic in [`presentation_sandbox_window.py`](src/deZent_demo/presentation/presentation_sandbox_window.py) is still in prototype form - rework to maintainable source
    - supports one round only - a proper factory from logic configuration to instrumentors with automatic cleanup is needed
    - especially a wrapper for a Presentation State handling setup, lifetime and cleanup of otherwise static reused visual objects
    - use config + maybe an Event System for a more data driven design
        - e.g. a Presentation State Trigger + allow followup states (a state triggering another one immediately)

- deadlock on exit - all synchronization objects should be unified (time_env, InstrumentorGates)
    - cause of the deadlock is unknown, all seem to be released, maybe order matters which there is no semantic for yet

- CBFPlot implementation is still in prototype form - rework to maintainable source
    - Option A: Rework
        - wrap Qt objects into domain specific classes with defined dimensions (.size or .boundingbox)
        - place scene items in absolute coordinates, let view handle the scaling as intended
            - LineWidth, FontSize, ... shouldn't scale (Qtobj.setFlags(?do not scale?))
        - expose style with dynamic updating -> Styled[CBFPlotStyle]
        - since dynamic amounts of plot elements are needed, the use of a QObject allocator could be sensible
            - should handle lifetime of QObjects
            - reuse / create / delete objects as by e.g. get_bar(), get_label(), ...
    - Option B: use a qt plotting lib
        - check requirements + availability

- SmartMeter visualization - one connected representative SM as graph node + e.g. dots for the rest

- CentralEntity publication bar - colored GWs contribute to filling a bar at the CE with their color

- Animations - visualization objects could be animated using Qt's animation system

- Network deployment - originally it was planned to deploy the algorithm on a physical asynchronous network using rpis or similar.
    - requires an IP-level NetworkStack
    - requires distributed instrumentation 


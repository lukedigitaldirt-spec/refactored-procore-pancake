# Value-Stream Mapping — the as-is/to-be loop

Value-Stream Mapping (VSM) is the lean technique for drawing the end-to-end flow
of material and information, exposing where value is added versus where waste
accumulates. Where BPMN captures *logic*, VSM captures *time and waste*.

## The two maps
- **Current-state (as-is):** how the work flows *today*, including every
  workaround, queue, and rework loop. Map reality, not policy.
- **Future-state (to-be):** the redesigned flow after removing waste. Never
  draw it before the current state is measured — you will optimize a fantasy.

## Key data captured per step
- Process time (touch time) and wait/queue time.
- WIP (items waiting between steps).
- Percent complete & accurate (%C&A) — how often work arrives clean and needs no
  rework. Cascading %C&A is a hidden throughput killer.
- Uptime / availability of the step.

The **timeline ladder** at the bottom sums value-add time (touch) versus total
lead time — the visual form of Process Cycle Efficiency.

## The eight wastes (DOWNTIME)
Defects, Overproduction, Waiting, Non-utilized talent, Transportation,
Inventory, Motion, Extra-processing. In office/service processes **Waiting** and
**Defects (rework)** dominate.

## The improvement loop
1. Pick one product/request family (don't boil the ocean).
2. Walk the process physically, upstream from the customer.
3. Draw current state with real times and %C&A.
4. Identify waste and the constraint.
5. Design future state: continuous flow where possible, pull (WIP caps) where
   not, level the load.
6. Build an action plan with owners and dates; re-map after changes.

## Relationship to the tools here
- `cycle_time_analyzer.py` computes the timeline ladder (lead time, PCE, takt).
- `bottleneck_detector.py` finds the constraint you subordinate the flow to.
- `bpmn_validator.py` checks the logic of the redesigned flow before rollout.

## Authoritative sources
1. Mike Rother & John Shook, *Learning to See: Value-Stream Mapping to Add Value
   and Eliminate Muda*, Lean Enterprise Institute, 1999.
2. Karen Martin & Mike Osterling, *Value Stream Mapping*, McGraw-Hill, 2013
   (office/service application, %C&A).
3. James P. Womack & Daniel T. Jones, *Lean Thinking*, Free Press, 2003.
4. Beau Keyte & Drew Locher, *The Complete Lean Enterprise: Value Stream Mapping
   for Administrative and Office Processes*, Productivity Press, 2004.
5. Taiichi Ohno, *Toyota Production System*, Productivity Press, 1988.
6. Jeffrey Liker, *The Toyota Way*, McGraw-Hill, 2004.
7. Womack & Jones, *Seeing the Whole Value Stream*, LEI, 2011.
8. Drew Locher, *Value Stream Mapping for Lean Development*, Productivity Press,
   2008.

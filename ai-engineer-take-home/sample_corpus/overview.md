# Aperture: Product Overview

Aperture is a project analytics dashboard that connects to a team's existing task tracker (Jira, Linear, or Trello) and produces weekly burn-down and cycle-time reports automatically. It is aimed at engineering managers who want visibility into delivery health without asking their teams to fill out additional status reports.

## Core concepts

- **Workspace:** the top-level container for a team. Each workspace connects to exactly one task-tracker integration at a time.
- **Snapshot:** a daily read of all open and closed issues in the connected tracker. Snapshots are retained for 400 days on the Team plan and indefinitely on the Enterprise plan.
- **Cycle time:** the elapsed time between an issue moving to "In Progress" and moving to "Done." Aperture computes this per issue and aggregates it per week.
- **Burn-down:** a chart of remaining scoped work in the current sprint or cycle, recalculated from each daily snapshot.

## Who uses Aperture

Aperture is typically installed by an engineering manager or a program manager. Individual contributors do not need an Aperture account to have their issues tracked; Aperture only requires read access to the connected tracker.

## Supported integrations

As of the current release, Aperture supports:

- Jira Cloud (not Jira Server/Data Center)
- Linear
- Trello

GitHub Issues and Asana are on the public roadmap but not yet available.

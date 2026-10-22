// What the team board shows, computed from the team root's files with no
// engine calls, so every rule here is testable on its own.
//
// The board reads; it never decides. Lanes come from the charter, where each
// lane runs from the lead's roster.md, whether a retro is due and whether the
// contracts hold from validate_team.py. Nothing here is written back.

import type { Board, BoardCheck, BoardLane } from '../types'

// The lane a lead holds in its own session. The board runs in the lead's
// session, so that lane is up whenever the board is.
export const LEAD_LANE = 'lead'

/** The lanes under the charter's `## Lanes`, as validate_team.charter_lanes reads them. */
export function charterLanes(charter: string): string[] {
  const lanes: string[] = []
  let inLanes = false
  for (const line of charter.split('\n')) {
    const trimmed = line.trim()
    if (trimmed.startsWith('#')) {
      const depth = trimmed.length - trimmed.replace(/^#+/, '').length
      if (trimmed === '## Lanes') {
        inLanes = true
        continue
      }
      if (inLanes && depth <= 2) break
    }
    if (!inLanes) continue
    const m = /^\s*[-*]\s+([A-Za-z0-9][A-Za-z0-9_-]*)\b/.exec(line)
    if (m?.[1]) lanes.push(m[1])
  }
  return lanes
}

/** Notes in friction.md, counted as validate_team.check_friction_cap counts them. */
export function frictionCount(friction: string): number {
  return friction.split('\n').filter(l => l.trim() && !l.startsWith('#')).length
}

/**
 * The lead's roster line for a lane, or undefined.
 *
 * roster.md has no template: it is one line per lane, written by the lead from
 * each JOIN. The board shows the line as written rather than parsing fields
 * out of it, because a parse would be a template the lead never agreed to.
 * A line that opens with the lane wins over one that only mentions it, so
 * `web: waiting on api` is never read as api's line.
 */
export function rosterLine(roster: string, lane: string): string | undefined {
  const lines = roster.split('\n')
    .map(l => l.trim().replace(/^[-*|]\s*/, ''))
    .filter(l => l && !l.startsWith('#'))
  // Lane names are letters, digits, `_` and `-`, none of them special here.
  const opens = new RegExp(`^\`?${lane}\`?([^\\w-]|$)`)
  const names = new RegExp(`(^|[^\\w-])${lane}([^\\w-]|$)`)
  return lines.find(l => opens.test(l)) ?? lines.find(l => names.test(l))
}

/** The validator's verdict from its exit code and stderr; undefined when it did not run. */
export function parseValidator(exitCode: number, stderr: string): BoardCheck | undefined {
  if (exitCode !== 0 && exitCode !== 1) return undefined
  const lines = stderr.split('\n')
  const after = (prefix: string) =>
    lines.filter(l => l.startsWith(prefix)).map(l => l.slice(prefix.length).trim())
  return { isOk: exitCode === 0, failures: after('FAIL'), warnings: after('warning') }
}

/** Whether the validator says a retro is due. Its [T8] owns the cap. */
export function isRetroDue(check: BoardCheck | undefined): boolean {
  return !!check?.warnings.some(w => w.startsWith('[T8]') && /retro is due/i.test(w))
}

export function lanesOf(
  charter: string,
  roster: string,
  reachable: readonly string[] | undefined,
): BoardLane[] {
  return charterLanes(charter).map(name => {
    const line = rosterLine(roster, name)
    const presence: BoardLane['presence'] =
      name === LEAD_LANE ? 'self'
      : reachable === undefined ? 'unknown'
      : reachable.includes(name) ? 'up'
      : 'down'
    return { name, presence, roster: line, isParked: !!line && /\bparked\b/i.test(line) }
  })
}

/** A lane the team is waiting on that no session answers to. */
function isMissing(lane: BoardLane): boolean {
  return lane.presence === 'down' && !lane.isParked
}

export type Problem = { key: string; text: string }

/**
 * What deserves an alert, keyed so each fires once while it lasts.
 *
 * A lane counts only once it has been seen up. Every lane is down between
 * /teamwork:form and the human starting it, and alerting on all of them then
 * says nothing the human does not already know.
 */
export function problems(board: Board, seen: readonly string[]): Problem[] {
  const out: Problem[] = []
  for (const lane of board.lanes) {
    if (isMissing(lane) && seen.includes(lane.name)) {
      out.push({ key: `down:${lane.name}`, text: `${lane.name} dropped out` })
    }
  }
  if (board.isRetroDue) {
    out.push({ key: 'retro', text: `retro due: friction ${frictionLabel(board)}` })
  }
  if (board.contracts && !board.contracts.isOk) {
    const n = board.contracts.failures.length
    out.push({ key: 'contracts', text: `contracts failing: ${n} check${n === 1 ? '' : 's'}` })
  }
  return out
}

function frictionLabel(board: Board): string {
  return board.frictionCap ? `${board.friction}/${board.frictionCap}` : `${board.friction}`
}

/** The one line under the prompt: what is wrong, or a short all-clear. */
export function statusText(board: Board): string {
  const waiting = board.lanes.filter(l => !l.isParked)
  const missing = waiting.filter(isMissing).map(l => `${l.name} not up`)
  const wrong = [...missing]
  if (board.isRetroDue) wrong.push(`retro due (${frictionLabel(board)})`)
  if (board.contracts && !board.contracts.isOk) wrong.push('contracts failing')
  if (wrong.length) return `team: ${wrong.join(' · ')}`

  const up = waiting.filter(l => l.presence === 'up' || l.presence === 'self').length
  const parked = board.lanes.length - waiting.length
  const parts = [
    waiting.some(l => l.presence === 'unknown') ? 'lanes unknown' : `${up}/${waiting.length} up`,
  ]
  if (parked) parts.push(`${parked} parked`)
  parts.push(`friction ${frictionLabel(board)}`)
  parts.push(board.contracts ? 'contracts ok' : 'contracts unchecked')
  return `team: ${parts.join(' · ')}`
}

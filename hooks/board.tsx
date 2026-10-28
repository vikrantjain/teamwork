// The team board: one line under the lead's prompt, an alert when something
// the lead must act on starts, and a pane on /team-board.
//
// It is a convenience and nothing depends on it. A member is bound by the
// files, and a lead without this module runs /teamwork:status instead. So it
// only reads: it never writes the team root, never messages a lane, and keeps
// no record of its own, because a snapshot beside the tracker drifts from it.
//
// It runs in the lead's session only. Every member running it would raise the
// same alert in every terminal. A session is the lead's when it carries no
// lane, or the `lead` lane, which is how the boundary hook tells them apart.

import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Board, BoardCheck } from '../types'
import {
  frictionCount, isRetroDue, lanesOf, LEAD_LANE, parseValidator, problems, statusText,
} from './board-model'

const PANE = 'team-board'
// ListAgents and two file reads each time. The validator runs only when a
// file in the team root has changed, so a quiet team costs almost nothing.
const REFRESH_MS = 20_000

const board = atom({ plugin: 'teamwork', key: 'board' } as const, null)
const alerted = atom({ plugin: 'teamwork', key: 'alerted' } as const, [])
const seen = atom({ plugin: 'teamwork', key: 'seen' } as const, [])

type $ = EngineInterface

// Module variables start over on a reload, which costs one validator run.
let lastCheck: { root: string; signature: string; check?: BoardCheck } | undefined
let cap: { value?: number } | undefined
let running: Promise<Board | null> | undefined

const parent = (path: string) => path.replace(/\/+[^/]*\/*$/, '') || '/'

async function exists($: $, path: string): Promise<boolean> {
  try {
    await $.fs.stat(path)
    return true
  } catch {
    return false
  }
}

async function readOr($: $, path: string): Promise<string> {
  try {
    return await $.fs.read(path)
  } catch {
    return ''
  }
}

/** The team root, by the ladder the boundary hook and team-root.md use. */
async function findRoot($: $): Promise<string | undefined> {
  const named = await $.env.get('TEAMWORK_ROOT')
  if (named && (await exists($, `${named}/charter.md`))) return named
  const cwd = await $.session.cwd()
  try {
    const git = await $.process.run(
      ['git', 'rev-parse', '--path-format=absolute', '--git-common-dir'], { cwd })
    const common = git.stdout.trim()
    if (git.exitCode === 0 && common) {
      const candidate = `${parent(common)}/.teamwork`
      if (await exists($, `${candidate}/charter.md`)) return candidate
    }
  } catch {
    // No git on this machine. The walk below still finds a root.
  }
  for (let here = cwd; ; here = parent(here)) {
    if (await exists($, `${here}/.teamwork/charter.md`)) return `${here}/.teamwork`
    if (here === '/') return undefined
  }
}

/**
 * Whether a run is live: TEAMWORK_ROOT is set, or the team root holds roster.md.
 * Finishing keeps the team root, and a board for a finished team would report
 * every lane missing forever. The boundary hook's test also counts a resolved
 * lane, which the board skips: a lead's TEAMWORK_LANE=lead outlives the run.
 */
async function isLive($: $, root: string): Promise<boolean> {
  return !!(await $.env.get('TEAMWORK_ROOT')) || exists($, `${root}/roster.md`)
}

/** Session names other sessions on this machine answer to; undefined when unknown. */
async function reachable($: $): Promise<string[] | undefined> {
  try {
    const ran = await $.tool.call({ tool: 'ListAgents' })
    if (ran.deny !== undefined || ran.isError) return undefined
    return (ran.result.sections ?? []).flatMap(s => s.rows.flatMap(r => (r.name ? [r.name] : [])))
  } catch {
    return undefined
  }
}

/** The team root's files by name, size and time, so an unchanged root skips the validator. */
async function signature($: $, root: string): Promise<string> {
  const parts: string[] = []
  for (const dir of [root, `${root}/roles`]) {
    try {
      for (const f of await $.fs.list(dir)) parts.push(`${dir}/${f.name}:${f.size}:${f.mtimeMs}`)
    } catch {
      // A team root without roles/ is the validator's to report, not this.
    }
  }
  return parts.sort().join('\n')
}

async function validate($: $, root: string): Promise<BoardCheck | undefined> {
  const sig = await signature($, root)
  if (lastCheck?.root === root && lastCheck.signature === sig) return lastCheck.check
  let check: BoardCheck | undefined
  try {
    const run = await $.process.run(
      ['python3', `${$.plugin.root}/scripts/validate_team.py`, root])
    check = parseValidator(run.exitCode, run.stderr)
  } catch {
    check = undefined
  }
  lastCheck = { root, signature: sig, check }
  return check
}

/** validate_team.FRICTION_CAP, read from the validator so the cap has one home. */
async function frictionCap($: $): Promise<number | undefined> {
  if (cap) return cap.value
  try {
    const run = await $.process.run([
      'python3', '-c',
      'import sys; sys.path.insert(0, sys.argv[1]); import validate_team; '
        + 'print(validate_team.FRICTION_CAP)',
      `${$.plugin.root}/scripts`,
    ])
    const value = Number.parseInt(run.stdout.trim(), 10)
    cap = { value: run.exitCode === 0 && Number.isFinite(value) ? value : undefined }
  } catch {
    cap = {}
  }
  return cap.value
}

/** Raise what started since the last look, and say when a dropped lane is back. */
async function alert($: $, now: Board): Promise<void> {
  const up = now.lanes.filter(l => l.presence === 'up' || l.presence === 'self').map(l => l.name)
  const known = await update($, seen, list => [...new Set([...list, ...up])])
  const current = problems(now, known)
  const before = await read($, alerted)
  for (const p of current) {
    if (before.includes(p.key)) continue
    $.ui.toast(`team: ${p.text}`)
    void $.ui.notify(p.text, { title: 'teamwork' }).catch(() => undefined)
  }
  for (const key of before) {
    if (key.startsWith('down:') && !current.some(p => p.key === key)) {
      $.ui.toast(`team: ${key.slice('down:'.length)} is back`)
    }
  }
  await update($, alerted, () => current.map(p => p.key))
}

async function look($: $): Promise<Board | null> {
  const root = await findRoot($)
  if (!root || !(await isLive($, root))) {
    await update($, board, () => null)
    $.ui.status(undefined)
    return null
  }
  const [charter, roster, friction, names, contracts, frictionCapValue] = await Promise.all([
    readOr($, `${root}/charter.md`),
    readOr($, `${root}/roster.md`),
    readOr($, `${root}/friction.md`),
    reachable($),
    validate($, root),
    frictionCap($),
  ])
  const now: Board = {
    root,
    lanes: lanesOf(charter, roster, names),
    friction: frictionCount(friction),
    frictionCap: frictionCapValue,
    contracts,
    isRetroDue: isRetroDue(contracts),
  }
  await update($, board, () => now)
  $.ui.status(statusText(now))
  await alert($, now)
  return now
}

/** One look at a time: a timer firing during a slow look waits for it. */
function refresh($: $): Promise<Board | null> {
  running ??= look($).finally(() => {
    running = undefined
  })
  return running
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const started = await next(e)
    const lane = await $.env.get('TEAMWORK_LANE')
    if (lane && lane !== LEAD_LANE) return started
    await $.command.register({
      name: 'team-board',
      description: 'Show the teamwork board: lanes, friction and the contracts check',
    })
    void refresh($)
    $.clock.every(REFRESH_MS, () => void refresh($))
    return started
  })

  on('command.run', { command: 'team-board' }, async $ => {
    const now = await refresh($)
    if (!now) return { text: 'No live teamwork run is visible from this session.' }
    const opened = await $.ui.open({ id: PANE, title: 'Team board', focus: true, closeOnEscape: true })
    return {
      text: opened.isPlaced ? 'Team board opened. Esc closes it.'
        : `Team board could not open: ${opened.reason}`,
    }
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text } = $.ui.resolve(e)
    const now = await read($, board)
    if (!now) return <Text dimColor>No live teamwork run.</Text>
    const width = Math.max(20, e.props.bodyColumns)
    const fit = (s: string) => (s.length > width ? `${s.slice(0, width - 1)}…` : s)
    const pad = Math.max(...now.lanes.map(l => l.name.length), 4)
    const state = (l: Board['lanes'][number]) =>
      l.isParked ? 'parked'
      : l.presence === 'self' ? 'this session'
      : l.presence === 'up' ? 'up'
      : l.presence === 'unknown' ? 'unknown'
      : 'not up'
    const isWrong = (l: Board['lanes'][number]) => l.presence === 'down' && !l.isParked
    const lanes = [...now.lanes].sort((a, b) => Number(isWrong(b)) - Number(isWrong(a)))
    const failures = now.contracts?.failures ?? []
    const shown = Math.max(1, (e.viewport?.rows ?? 24) - lanes.length - 8)

    return (
      <Box flexDirection="column">
        {now.isRetroDue && (
          <Text color="warning">{fit(`! retro due: friction ${now.friction}/${now.frictionCap ?? '?'}`)}</Text>
        )}
        {now.contracts && !now.contracts.isOk && (
          <Text color="error">{fit(`! contracts failing: ${failures.length}`)}</Text>
        )}
        {lanes.map(l => (
          <Text color={isWrong(l) ? 'error' : undefined} dimColor={l.isParked}>
            {fit(`${isWrong(l) ? '!' : ' '} ${l.name.padEnd(pad)}  ${state(l).padEnd(12)}  ${l.roster ?? ''}`)}
          </Text>
        ))}
        <Text dimColor>
          {fit(`friction ${now.friction}${now.frictionCap ? `/${now.frictionCap}` : ''} · contracts ${
            now.contracts ? (now.contracts.isOk ? 'ok' : 'failing') : 'unchecked'}`)}
        </Text>
        {failures.slice(0, shown).map(f => <Text color="error">{fit(`  ${f}`)}</Text>)}
        {failures.length > shown && <Text dimColor>{`  and ${failures.length - shown} more`}</Text>}
        <Text dimColor>{fit(now.root)}</Text>
      </Box>
    )
  })
}

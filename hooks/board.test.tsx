import { expect, mock, test } from 'claude-code/testing'
import type { On } from 'claude-code'

import {
  charterLanes, frictionCount, lanesOf, parseValidator, problems, rosterLine, statusText,
} from './board-model'

const ROOT = '/repo/.teamwork'

const CHARTER = `# Ship billing

Team root: ${ROOT}
Workspace: one shared tree
Workspace root: /repo

## Lanes
- api - the billing service
- web - the dashboard
- lead - integration and docs

## Done
- Both lanes' tests pass.
`

const ROSTER = `- web - /repo - joined, waiting on api
- api - /repo - joined
- lead - /repo - this session
`

const PANE = {
  plugin: 'teamwork',
  component: 'Pane',
  requestId: 'team-board',
  props: {
    title: 'Team board',
    isFocused: true,
    bodyColumns: 72,
    placement: 'dock',
    scroll: { offset: 0, bodyRows: 20 },
    view: {},
  },
} as const

const parent = (p: string) => p.replace(/\/[^/]*$/, '') || '/'

type World = {
  files: Record<string, string>
  agents: string[]
  validator: { exitCode: number; stderr: string }
  statuses: (string | undefined)[]
  toasts: string[]
  registered: string[]
}

/** The engine beneath the plugin: a team root in memory, and the sessions up. */
function world(on: On, env: Record<string, string>, files: Record<string, string>): World {
  const w: World = {
    files,
    agents: ['api', 'web'],
    validator: { exitCode: 0, stderr: 'ok      all checks passed' },
    statuses: [],
    toasts: [],
    registered: [],
  }
  mock.env(on, env)
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('session.cwd', () => ({ value: '/repo' }))
  on('fs.stat', (_, e) => (e.path in w.files
    ? { value: { kind: 'file', size: 1, mtimeMs: 1, isLink: false } }
    : { deny: 'no such file' }))
  on('fs.read', (_, e) => {
    const text = w.files[e.path]
    return text === undefined ? { deny: 'no such file' } : { value: text }
  })
  on('fs.list', (_, e) => ({
    value: Object.keys(w.files).filter(p => parent(p) === e.path).map(p => ({
      name: p.slice(e.path.length + 1),
      kind: 'file' as const,
      size: w.files[p]?.length ?? 0,
      mtimeMs: 1,
      isLink: false,
    })),
  }))
  on('process.run', (_, e) => {
    const out = { stdout: '', stderr: '', isStdoutTruncated: false, isStderrTruncated: false }
    if (e.argv[0] === 'git') return { value: { ...out, exitCode: 128 } }
    if (e.argv[1] === '-c') return { value: { ...out, exitCode: 0, stdout: '25\n' } }
    return { value: { ...out, ...w.validator } }
  })
  on('tool.call', { tool: 'ListAgents' }, () => ({
    result: {
      listing: '',
      sections: [{ kind: 'peers', total: w.agents.length, rows: w.agents.map(name => ({ name })) }],
    },
  }))
  on('command.register', (_, e) => {
    w.registered.push(e.name)
    return { value: { command: e.name } }
  })
  on('ui.status', (_, e) => {
    w.statuses.push(e.text)
    return { value: undefined }
  })
  on('ui.toast', (_, e) => {
    w.toasts.push(e.text)
    return { value: undefined }
  })
  on('ui.notify', () => ({ value: { isSent: true, channel: 'terminal_bell' } }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  return w
}

function liveTeam(): Record<string, string> {
  return {
    [`${ROOT}/charter.md`]: CHARTER,
    [`${ROOT}/roster.md`]: ROSTER,
    [`${ROOT}/friction.md`]: '- api: the lockfile rule cost a turn\n- web: same\n',
  }
}

// --- what the board reads -----------------------------------------------------

test('lanes are read from the charter as the validator reads them', async () => {
  expect(charterLanes(CHARTER)).toEqual(['api', 'web', 'lead'])
})

test('friction is counted as the validator counts it', async () => {
  expect(frictionCount('# Carried\n- one\n\n- two\n')).toBe(2)
})

test('a roster line that opens with the lane wins over one that mentions it', async () => {
  expect(rosterLine(ROSTER, 'api')).toBe('api - /repo - joined')
  expect(rosterLine(ROSTER, 'docs')).toBeUndefined()
})

test('the validator verdict keeps its failures and warnings', async () => {
  const check = parseValidator(1, 'warning [T8] friction.md: 25 notes, cap 25. A retro is due.\n'
    + 'FAIL    [T5] roles/: both own src.\n')
  expect(check?.isOk).toBe(false)
  expect(check?.failures).toEqual(['[T5] roles/: both own src.'])
  expect(parseValidator(2, '')).toBeUndefined()
})

test('a lane never seen up is shown but never alerted', async () => {
  const board = {
    root: ROOT, lanes: lanesOf(CHARTER, ROSTER, ['api']), friction: 0, isRetroDue: false,
  }
  expect(statusText(board)).toBe('team: web not up')
  expect(problems(board, [])).toEqual([])
  expect(problems(board, ['web']).map(p => p.key)).toEqual(['down:web'])
})

test('a parked lane is not missing', async () => {
  const roster = ROSTER.replace('joined, waiting on api', 'parked')
  const board = {
    root: ROOT, lanes: lanesOf(CHARTER, roster, ['api']), friction: 3, frictionCap: 25,
    isRetroDue: false, contracts: { isOk: true, failures: [], warnings: [] },
  }
  expect(statusText(board)).toBe('team: 2/2 up · 1 parked · friction 3/25 · contracts ok')
})

// --- the lead's session -----------------------------------------------------------

test('the status line is a short all-clear while nothing is wrong', async ($, on) => {
  const w = world(on, { TEAMWORK_ROOT: ROOT }, liveTeam())
  const clock = mock.clock(on)
  await $.session.start({ cwd: '/repo', surface: 'terminal', isInteractive: true })
  await clock.settle()
  expect(w.registered).toEqual(['team-board'])
  expect(w.statuses.at(-1)).toBe('team: 3/3 up · friction 2/25 · contracts ok')
  expect(w.toasts).toEqual([])
})

test('a lane that drops out is alerted once, and its return is said', async ($, on) => {
  const w = world(on, { TEAMWORK_ROOT: ROOT }, liveTeam())
  const clock = mock.clock(on)
  await $.session.start({ cwd: '/repo', surface: 'terminal', isInteractive: true })
  await clock.settle()

  w.agents = ['api']
  await clock.advance(20_000)
  expect(w.statuses.at(-1)).toBe('team: web not up')
  expect(w.toasts).toEqual(['team: web dropped out'])

  await clock.advance(20_000)
  expect(w.toasts).toEqual(['team: web dropped out'])

  w.agents = ['api', 'web']
  await clock.advance(20_000)
  expect(w.toasts).toEqual(['team: web dropped out', 'team: web is back'])
  expect(w.statuses.at(-1)).toBe('team: 3/3 up · friction 2/25 · contracts ok')
})

test('failing contracts are alerted and named in the line', async ($, on) => {
  const w = world(on, { TEAMWORK_ROOT: ROOT }, liveTeam())
  w.validator = { exitCode: 1, stderr: 'FAIL    [T7] protocol.md: differs from the plugin.' }
  const clock = mock.clock(on)
  await $.session.start({ cwd: '/repo', surface: 'terminal', isInteractive: true })
  await clock.settle()
  expect(w.statuses.at(-1)).toBe('team: contracts failing')
  expect(w.toasts).toEqual(['team: contracts failing: 1 check'])
})

test('a member session shows no board, because its lead does', async ($, on) => {
  const w = world(on, { TEAMWORK_ROOT: ROOT, TEAMWORK_LANE: 'api' }, liveTeam())
  const clock = mock.clock(on)
  await $.session.start({ cwd: '/repo', surface: 'terminal', isInteractive: true })
  await clock.settle()
  expect(w.registered).toEqual([])
  expect(w.statuses).toEqual([])
})

test('a finished team shows no board', async ($, on) => {
  const files = liveTeam()
  delete files[`${ROOT}/roster.md`]
  const w = world(on, {}, files)
  const clock = mock.clock(on)
  await $.session.start({ cwd: '/repo', surface: 'terminal', isInteractive: true })
  await clock.settle()
  expect(w.statuses.at(-1)).toBeUndefined()
  expect(w.toasts).toEqual([])
})

test('the pane lists what is wrong first, on every surface', async ($, on) => {
  const w = world(on, { TEAMWORK_ROOT: ROOT }, liveTeam())
  w.agents = ['api']
  const clock = mock.clock(on)
  await $.session.start({ cwd: '/repo', surface: 'terminal', isInteractive: true })
  await clock.settle()

  for (const surface of ['terminal', 'desktop', 'vscode', 'mobile'] as const) {
    const ui = await $.ui.mount({ ...PANE, surface })
    const missing = await ui.find({ type: 'Text', text: /^! web/ })
    expect(missing?.text).toContain('not up')
    expect((await ui.find({ type: 'Text', text: /contracts ok/ }))?.text)
      .toBe('friction 2/25 · contracts ok')
    await ui.unmount()
  }
})

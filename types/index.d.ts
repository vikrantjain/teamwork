// The team board's state: what the status line and the pane draw from.

export type BoardLane = {
  name: string
  /**
   * `up` when a session of this name is reachable, `self` for the lane the
   * lead holds in this session, `unknown` when ListAgents could not be asked.
   */
  presence: 'up' | 'self' | 'down' | 'unknown'
  /** The lead's roster.md line for this lane, as written. */
  roster?: string
  isParked: boolean
}

export type BoardCheck = {
  isOk: boolean
  failures: string[]
  warnings: string[]
}

export type Board = {
  root: string
  lanes: BoardLane[]
  friction: number
  /** validate_team.FRICTION_CAP, when it could be read. */
  frictionCap?: number
  /** The validator's verdict; absent when it could not run. */
  contracts?: BoardCheck
  isRetroDue: boolean
}

declare module 'claude-code' {
  interface PluginState {
    teamwork: {
      board: Board | null
      /** Problem keys already alerted, so each fires once while it lasts. */
      alerted: string[]
      /** Lanes seen up this session; only those can drop out. */
      seen: string[]
    }
  }
}

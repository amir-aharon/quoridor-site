export enum Orientation {
  Horizontal = 'horizontal',
  Vertical = 'vertical',
  None = 'none',
}

export interface WallState {
  row: number;
  col: number;
  orientation: Orientation;
  selected: boolean;
  occupied: boolean; // Ensure this is defined
}

export interface CellState {
  row: number;
  col: number;
  standingPlayer: PlayerState | null;
  presentedOption: boolean;
  selected: boolean;
  selectable: boolean; // Ensure this is defined
}

export interface PlayerState {
  playerId: string;
}
